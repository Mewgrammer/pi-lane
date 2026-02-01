"""Track simulation for development without hardware."""

import asyncio
import random
import logging
from typing import Callable, Awaitable

from pilane.config import settings
from pilane.race.engine import race_engine


logger = logging.getLogger(__name__)


class TrackSimulator:
    """
    Simulates a slot car track for development.
    
    This simulator generates fake lap events based on power levels,
    allowing full development and testing of the UI without real hardware.
    """
    
    def __init__(self):
        self._running = False
        self._tasks: dict[int, asyncio.Task] = {}  # lane -> simulation task
    
    async def start_simulation(self) -> None:
        """Start simulating all lanes in the current race."""
        if not race_engine.current_race:
            logger.warning("No race to simulate")
            return
        
        self._running = True
        
        for lane in race_engine.current_race.lanes.keys():
            task = asyncio.create_task(self._simulate_lane(lane))
            self._tasks[lane] = task
        
        logger.info(f"Started simulation for {len(self._tasks)} lanes")
    
    async def stop_simulation(self) -> None:
        """Stop all lane simulations."""
        self._running = False
        
        for task in self._tasks.values():
            task.cancel()
        
        self._tasks.clear()
        logger.info("Simulation stopped")
    
    async def _simulate_lane(self, lane: int) -> None:
        """
        Simulate a single lane.
        
        This estimates when the car completes a lap based on power level
        and triggers the lap recording.
        """
        try:
            while self._running and race_engine.current_race:
                if race_engine.current_race.state.value != "running":
                    await asyncio.sleep(0.1)
                    continue
                
                lane_state = race_engine.current_race.lanes.get(lane)
                if not lane_state or lane_state.finished:
                    break
                
                # Calculate estimated lap time based on power
                power = lane_state.power_level
                
                if power <= 0:
                    # Car is stopped
                    await asyncio.sleep(0.1)
                    continue
                
                # Base lap time adjusted by power and random variance
                speed_factor = power / 100.0
                base_time = settings.sim_base_lap_time_ms / 1000  # Convert to seconds
                variance = random.uniform(
                    -settings.sim_lap_time_variance_ms,
                    settings.sim_lap_time_variance_ms
                ) / 1000
                
                # Lap time = base_time / speed_factor + variance
                # At 100% power: ~base_time
                # At 50% power: ~2x base_time
                if speed_factor > 0:
                    lap_time = (base_time / speed_factor) + variance
                else:
                    lap_time = float('inf')
                
                # Wait for the lap to complete
                # We do this in small increments to respond to power changes
                elapsed = 0.0
                while elapsed < lap_time and self._running:
                    await asyncio.sleep(0.1)
                    elapsed += 0.1
                    
                    # Check if power changed significantly
                    new_power = lane_state.power_level
                    if abs(new_power - power) > 10:
                        # Recalculate remaining time
                        if new_power > 0:
                            remaining_distance = 1 - (elapsed / lap_time)
                            new_speed_factor = new_power / 100.0
                            new_remaining_time = (remaining_distance * base_time) / new_speed_factor
                            lap_time = elapsed + new_remaining_time
                            power = new_power
                    
                    # Check if race is still running
                    if race_engine.current_race.state.value != "running":
                        break
                
                # If we completed the lap, record it
                if elapsed >= lap_time and self._running:
                    await race_engine.record_lap(lane)
        
        except asyncio.CancelledError:
            logger.debug(f"Simulation for lane {lane} cancelled")
        except Exception as e:
            logger.error(f"Simulation error for lane {lane}: {e}")


class SimulatedLightBarrier:
    """
    Simulates a light barrier sensor.
    
    In the real hardware, this would be replaced with GPIO interrupt handling.
    """
    
    def __init__(self, lane: int, callback: Callable[[], Awaitable[None]]):
        self.lane = lane
        self.callback = callback
        self._triggered = False
    
    async def trigger(self) -> None:
        """Simulate a car crossing the light barrier."""
        if not self._triggered:
            self._triggered = True
            await self.callback()
            # Small debounce
            await asyncio.sleep(0.1)
            self._triggered = False


class SimulatedPWMController:
    """
    Simulates a PWM power controller.
    
    In the real hardware, this would control actual PWM signals to the track.
    """
    
    def __init__(self, num_lanes: int = 2):
        self.power_levels: dict[int, float] = {
            lane: 0.0 for lane in range(1, num_lanes + 1)
        }
    
    def set_power(self, lane: int, power: float) -> None:
        """Set power level for a lane (0-100%)."""
        if lane in self.power_levels:
            self.power_levels[lane] = max(0, min(100, power))
            # Also update the race engine
            race_engine.set_power(lane, power)
            logger.debug(f"Lane {lane} power set to {power}%")
    
    def get_power(self, lane: int) -> float:
        """Get current power level for a lane."""
        return self.power_levels.get(lane, 0.0)
    
    def emergency_stop(self) -> None:
        """Cut power to all lanes immediately."""
        for lane in self.power_levels:
            self.power_levels[lane] = 0.0
            race_engine.set_power(lane, 0.0)
        logger.warning("Emergency stop - all lanes powered off")


# Global simulator instance
track_simulator = TrackSimulator()
pwm_controller = SimulatedPWMController()
