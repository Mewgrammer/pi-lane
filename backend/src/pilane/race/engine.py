"""Race engine core - manages race lifecycle and state."""

import asyncio
import logging
from datetime import datetime
from typing import Callable, Any
from dataclasses import dataclass, field
from enum import Enum

from pilane.config import settings
from pilane.websocket import manager, create_ws_message
from pilane.schemas import RaceStateEnum


logger = logging.getLogger(__name__)


class RaceEngineState(Enum):
    """Internal race engine state."""
    IDLE = "idle"
    COUNTDOWN = "countdown"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass
class LaneState:
    """State for a single lane during a race."""
    lane_number: int
    car_id: int
    power_level: float = 0.0  # 0-100%
    current_lap: int = 0
    lap_times_ms: list[int] = field(default_factory=list)
    best_lap_time_ms: int | None = None
    total_time_ms: int = 0
    last_lap_timestamp: float = 0.0  # Time of last lap crossing
    estimated_position: float = 0.0  # 0.0-1.0 track progress
    fuel_level: float = 100.0
    finished: bool = False
    finish_position: int | None = None


@dataclass
class RaceState:
    """Complete race state."""
    race_id: int
    track_id: int
    mode: str
    target_laps: int
    time_limit_seconds: int | None
    fuel_simulation_enabled: bool
    lanes: dict[int, LaneState] = field(default_factory=dict)
    state: RaceEngineState = RaceEngineState.IDLE
    start_time: float | None = None
    elapsed_time_ms: int = 0
    countdown_remaining: int = 5
    finish_order: list[int] = field(default_factory=list)


class RaceEngine:
    """
    Core race engine that manages race lifecycle.
    
    This engine handles:
    - Race countdown and start
    - Lap detection processing
    - Position estimation
    - Race completion detection
    - State broadcasting via WebSocket
    """
    
    def __init__(self):
        self._current_race: RaceState | None = None
        self._tick_task: asyncio.Task | None = None
        self._lap_callbacks: list[Callable[[int, int, int], Any]] = []
    
    @property
    def current_race(self) -> RaceState | None:
        return self._current_race
    
    def setup_race(
        self,
        race_id: int,
        track_id: int,
        participants: list[dict],
        mode: str = "race_laps",
        target_laps: int = 10,
        time_limit_seconds: int | None = None,
        fuel_simulation_enabled: bool = False,
    ) -> RaceState:
        """Set up a new race with participants."""
        if self._current_race and self._current_race.state == RaceEngineState.RUNNING:
            raise RuntimeError("Cannot setup new race while another is running")
        
        lanes = {}
        for p in participants:
            lane_num = p["lane"]
            lanes[lane_num] = LaneState(
                lane_number=lane_num,
                car_id=p["car_id"],
            )
        
        self._current_race = RaceState(
            race_id=race_id,
            track_id=track_id,
            mode=mode,
            target_laps=target_laps,
            time_limit_seconds=time_limit_seconds,
            fuel_simulation_enabled=fuel_simulation_enabled,
            lanes=lanes,
        )
        
        logger.info(f"Race {race_id} setup with {len(lanes)} lanes")
        return self._current_race
    
    async def start_countdown(self) -> None:
        """Start the race countdown sequence."""
        if not self._current_race:
            raise RuntimeError("No race to start")
        
        self._current_race.state = RaceEngineState.COUNTDOWN
        self._current_race.countdown_remaining = 5
        
        # Broadcast countdown
        for i in range(5, 0, -1):
            self._current_race.countdown_remaining = i
            await self._broadcast_state()
            await manager.broadcast_to_race(
                self._current_race.race_id,
                create_ws_message("race:countdown", {"remaining": i})
            )
            await asyncio.sleep(1)
        
        # Start race!
        await self._start_race()
    
    async def _start_race(self) -> None:
        """Actually start the race after countdown."""
        if not self._current_race:
            return
        
        self._current_race.state = RaceEngineState.RUNNING
        self._current_race.start_time = asyncio.get_event_loop().time()
        
        # Initialize lap timestamps
        for lane in self._current_race.lanes.values():
            lane.last_lap_timestamp = self._current_race.start_time
        
        # Start the tick loop
        self._tick_task = asyncio.create_task(self._race_tick_loop())
        
        await manager.broadcast_to_race(
            self._current_race.race_id,
            create_ws_message("race:started", {"race_id": self._current_race.race_id})
        )
        
        logger.info(f"Race {self._current_race.race_id} started!")
    
    async def _race_tick_loop(self) -> None:
        """Main race loop - updates positions and checks end conditions."""
        while self._current_race and self._current_race.state == RaceEngineState.RUNNING:
            await self._tick()
            await asyncio.sleep(0.1)  # 10Hz update rate
    
    async def _tick(self) -> None:
        """Single race tick - update positions and elapsed time."""
        if not self._current_race or not self._current_race.start_time:
            return
        
        current_time = asyncio.get_event_loop().time()
        self._current_race.elapsed_time_ms = int((current_time - self._current_race.start_time) * 1000)
        
        # Update estimated positions based on power and elapsed time
        for lane in self._current_race.lanes.values():
            if not lane.finished:
                self._update_position_estimate(lane, current_time)
                
                # Update fuel if enabled
                if self._current_race.fuel_simulation_enabled:
                    # Fuel consumption based on power level
                    consumption = lane.power_level * 0.001  # 0.1% per tick at max power
                    lane.fuel_level = max(0, lane.fuel_level - consumption)
        
        # Check time limit
        if self._current_race.time_limit_seconds:
            if self._current_race.elapsed_time_ms >= self._current_race.time_limit_seconds * 1000:
                await self._finish_race()
                return
        
        # Broadcast state (throttled - every 5 ticks = 0.5s)
        if int(current_time * 10) % 5 == 0:
            await self._broadcast_state()
    
    def _update_position_estimate(self, lane: LaneState, current_time: float) -> None:
        """Estimate car position based on power level and time since last lap."""
        if lane.last_lap_timestamp == 0:
            return
        
        time_since_lap = current_time - lane.last_lap_timestamp
        
        # Estimate position using power level and expected lap time
        # At 100% power, assume we complete a lap in base_lap_time
        base_lap_time_s = settings.sim_base_lap_time_ms / 1000
        
        if lane.power_level > 0:
            # Speed factor based on power (0% = stopped, 100% = full speed)
            speed_factor = lane.power_level / 100.0
            expected_progress = (time_since_lap * speed_factor) / base_lap_time_s
            lane.estimated_position = expected_progress % 1.0
        else:
            # Power is off - position doesn't change
            pass
    
    async def record_lap(self, lane: int) -> None:
        """Record a lap crossing event (from light barrier)."""
        if not self._current_race or self._current_race.state != RaceEngineState.RUNNING:
            return
        
        if lane not in self._current_race.lanes:
            logger.warning(f"Lap recorded for unknown lane {lane}")
            return
        
        lane_state = self._current_race.lanes[lane]
        if lane_state.finished:
            return
        
        current_time = asyncio.get_event_loop().time()
        
        # Calculate lap time
        lap_time_ms = int((current_time - lane_state.last_lap_timestamp) * 1000)
        lane_state.last_lap_timestamp = current_time
        
        # Skip first crossing if it's too fast (car was already at start line)
        if lane_state.current_lap == 0 and lap_time_ms < 1000:
            return
        
        lane_state.current_lap += 1
        lane_state.lap_times_ms.append(lap_time_ms)
        lane_state.total_time_ms += lap_time_ms
        lane_state.estimated_position = 0.0  # Reset to start
        
        # Track best lap
        is_best = False
        if lane_state.best_lap_time_ms is None or lap_time_ms < lane_state.best_lap_time_ms:
            lane_state.best_lap_time_ms = lap_time_ms
            is_best = True
        
        logger.info(f"Lap {lane_state.current_lap} for lane {lane}: {lap_time_ms}ms")
        
        # Broadcast lap event
        await manager.broadcast_to_race(
            self._current_race.race_id,
            create_ws_message("race:lap", {
                "race_id": self._current_race.race_id,
                "car_id": lane_state.car_id,
                "lane": lane,
                "lap_number": lane_state.current_lap,
                "lap_time_ms": lap_time_ms,
                "is_best_lap": is_best,
            })
        )
        
        # Check if this car finished (lap mode)
        if self._current_race.mode == "race_laps":
            if lane_state.current_lap >= self._current_race.target_laps:
                lane_state.finished = True
                lane_state.finish_position = len(self._current_race.finish_order) + 1
                self._current_race.finish_order.append(lane)
                
                # Check if all finished
                all_finished = all(l.finished for l in self._current_race.lanes.values())
                if all_finished:
                    await self._finish_race()
    
    def set_power(self, lane: int, power_level: float) -> None:
        """Set power level for a lane (0-100%)."""
        if not self._current_race:
            return
        
        if lane in self._current_race.lanes:
            self._current_race.lanes[lane].power_level = max(0, min(100, power_level))
    
    async def pause(self) -> None:
        """Pause the race."""
        if self._current_race and self._current_race.state == RaceEngineState.RUNNING:
            self._current_race.state = RaceEngineState.PAUSED
            if self._tick_task:
                self._tick_task.cancel()
            await self._broadcast_state()
    
    async def resume(self) -> None:
        """Resume a paused race."""
        if self._current_race and self._current_race.state == RaceEngineState.PAUSED:
            self._current_race.state = RaceEngineState.RUNNING
            self._tick_task = asyncio.create_task(self._race_tick_loop())
            await self._broadcast_state()
    
    async def stop(self) -> None:
        """Stop/cancel the race."""
        if self._tick_task:
            self._tick_task.cancel()
        if self._current_race:
            self._current_race.state = RaceEngineState.FINISHED
            await manager.broadcast_to_race(
                self._current_race.race_id,
                create_ws_message("race:cancelled", {"race_id": self._current_race.race_id})
            )
    
    async def _finish_race(self) -> None:
        """Handle race completion."""
        if self._tick_task:
            self._tick_task.cancel()
        
        if not self._current_race:
            return
        
        self._current_race.state = RaceEngineState.FINISHED
        
        # Mark all cars as finished with positions
        for lane in self._current_race.lanes.values():
            if not lane.finished:
                lane.finished = True
                lane.finish_position = len(self._current_race.finish_order) + 1
                self._current_race.finish_order.append(lane.lane_number)
        
        await manager.broadcast_to_race(
            self._current_race.race_id,
            create_ws_message("race:finished", {
                "race_id": self._current_race.race_id,
                "finish_order": self._current_race.finish_order,
                "results": {
                    lane: {
                        "car_id": state.car_id,
                        "laps": state.current_lap,
                        "total_time_ms": state.total_time_ms,
                        "best_lap_ms": state.best_lap_time_ms,
                        "position": state.finish_position,
                    }
                    for lane, state in self._current_race.lanes.items()
                }
            })
        )
        
        logger.info(f"Race {self._current_race.race_id} finished!")
    
    async def _broadcast_state(self) -> None:
        """Broadcast current race state to all subscribers."""
        if not self._current_race:
            return
        
        participants = [
            {
                "lane": lane,
                "car_id": state.car_id,
                "current_lap": state.current_lap,
                "best_lap_time_ms": state.best_lap_time_ms,
                "total_time_ms": state.total_time_ms,
                "fuel_level": state.fuel_level,
                "estimated_position": state.estimated_position,
                "finished": state.finished,
                "finish_position": state.finish_position,
            }
            for lane, state in self._current_race.lanes.items()
        ]
        
        await manager.broadcast_to_race(
            self._current_race.race_id,
            create_ws_message("race:state", {
                "race_id": self._current_race.race_id,
                "state": self._current_race.state.value,
                "elapsed_time_ms": self._current_race.elapsed_time_ms,
                "participants": participants,
            })
        )


# Global race engine instance
race_engine = RaceEngine()
