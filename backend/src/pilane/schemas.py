"""Pydantic models for data entities - used for validation and serialization."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============ Enums ============

class RaceModeEnum(str, Enum):
    """Race mode types."""
    PRACTICE = "practice"
    TIME_TRIAL = "time_trial"
    RACE_LAPS = "race_laps"
    RACE_TIME = "race_time"


class RaceStateEnum(str, Enum):
    """Race state machine states."""
    CREATED = "created"
    COUNTDOWN = "countdown"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"


# ============ User Schemas ============

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    avatar_color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: str


# ============ Car Schemas ============

class CarBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#EF4444", pattern=r"^#[0-9A-Fa-f]{6}$")


class CarCreate(CarBase):
    owner_id: int


class Car(CarBase):
    id: int
    owner_id: int
    total_laps: int = 0
    total_races: int = 0
    best_lap_time_ms: Optional[int] = None
    created_at: str


# ============ Track Schemas ============

class TrackPiece(BaseModel):
    """Single track piece in the layout."""
    piece_id: str
    type: str  # straight, curve, lane_change, crossing
    x: float = 0
    y: float = 0
    rotation: float = 0  # degrees


class TrackLayout(BaseModel):
    """Complete track layout."""
    pieces: list[TrackPiece] = Field(default_factory=list)
    connections: list[dict] = Field(default_factory=list)


class TrackBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    lanes: int = Field(default=2, ge=1, le=8)
    layout: TrackLayout = Field(default_factory=TrackLayout)


class TrackCreate(TrackBase):
    pass


class Track(TrackBase):
    id: int
    track_record_ms: Optional[int] = None
    track_record_car_id: Optional[int] = None
    created_at: str
    updated_at: str


# ============ Race Schemas ============

class RaceParticipant(BaseModel):
    car_id: int
    lane: int = Field(..., ge=1)
    current_lap: int = 0
    best_lap_time_ms: Optional[int] = None
    total_time_ms: int = 0
    fuel_level: float = 100.0
    estimated_position: float = 0.0
    finished: bool = False
    finish_position: Optional[int] = None


class RaceSettings(BaseModel):
    """Race configuration settings."""
    mode: RaceModeEnum = RaceModeEnum.RACE_LAPS
    target_laps: int = Field(default=10, ge=1)
    time_limit_seconds: Optional[int] = Field(None, ge=60)
    fuel_simulation_enabled: bool = False


class RaceCreate(BaseModel):
    track_id: int
    settings: RaceSettings = Field(default_factory=RaceSettings)
    participants: list[RaceParticipant] = Field(default_factory=list)


class Race(BaseModel):
    id: int
    track_id: int
    mode: RaceModeEnum
    state: RaceStateEnum
    target_laps: int
    time_limit_seconds: Optional[int] = None
    fuel_simulation_enabled: bool = False
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    created_at: str
    participants: list[RaceParticipant] = []


# ============ Lap Record Schemas ============

class LapRecord(BaseModel):
    id: int
    race_id: int
    car_id: int
    lap_number: int
    lap_time_ms: int
    lane: int
    timestamp: str


# ============ Leaderboard Schemas ============

class LeaderboardEntry(BaseModel):
    rank: int
    car_id: int
    car_name: str
    car_color: str
    owner_name: str
    best_lap_time_ms: int


class TrackLeaderboard(BaseModel):
    track_id: int
    track_name: str
    entries: list[LeaderboardEntry]


# ============ WebSocket Messages ============

class WSMessage(BaseModel):
    type: str
    payload: Any
    timestamp: float


class PowerUpdate(BaseModel):
    lane: int
    power_level: float = Field(..., ge=0, le=100)
