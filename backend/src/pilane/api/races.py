"""Races API router using TinyDB."""

from fastapi import APIRouter, HTTPException, status

from pilane.database import get_db, generate_id, now_iso, Q
from pilane.schemas import RaceCreate, Race, RaceStateEnum

router = APIRouter()


@router.get("/", response_model=list[Race])
async def list_races(track_id: int | None = None, state: str | None = None):
    """Get all races, optionally filtered by track or state."""
    db = get_db()
    races = db.races.all()
    
    if track_id:
        races = [r for r in races if r.get("track_id") == track_id]
    if state:
        races = [r for r in races if r.get("state") == state]
    
    return sorted(races, key=lambda r: r.get("created_at", ""), reverse=True)


@router.post("/", response_model=Race, status_code=status.HTTP_201_CREATED)
async def create_race(race: RaceCreate):
    """Create a new race session."""
    db = get_db()
    
    # Verify track exists
    track = db.tracks.search(Q.id == race.track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Track not found",
        )
    track = track[0]
    
    # Validate participants
    lanes_used = set()
    for participant in race.participants:
        if participant.lane in lanes_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lane {participant.lane} is already assigned",
            )
        lanes_used.add(participant.lane)
        
        if participant.lane > track.get("lanes", 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lane {participant.lane} exceeds track's {track.get('lanes', 2)} lanes",
            )
        
        if not db.cars.search(Q.id == participant.car_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Car {participant.car_id} not found",
            )
    
    new_race = {
        "id": generate_id(db.races),
        "track_id": race.track_id,
        "mode": race.settings.mode.value,
        "state": RaceStateEnum.CREATED.value,
        "target_laps": race.settings.target_laps,
        "time_limit_seconds": race.settings.time_limit_seconds,
        "fuel_simulation_enabled": race.settings.fuel_simulation_enabled,
        "started_at": None,
        "finished_at": None,
        "created_at": now_iso(),
        "participants": [p.model_dump() for p in race.participants],
    }
    db.races.insert(new_race)
    return new_race


@router.get("/{race_id}", response_model=Race)
async def get_race(race_id: int):
    """Get a specific race by ID."""
    db = get_db()
    result = db.races.search(Q.id == race_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    return result[0]


@router.post("/{race_id}/start", response_model=Race)
async def start_race(race_id: int):
    """Start a race (triggers countdown)."""
    db = get_db()
    result = db.races.search(Q.id == race_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    
    race = result[0]
    
    if race.get("state") != RaceStateEnum.CREATED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start race in state: {race.get('state')}",
        )
    
    if not race.get("participants"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start race without participants",
        )
    
    race["state"] = RaceStateEnum.COUNTDOWN.value
    db.races.update(race, Q.id == race_id)
    
    # TODO: Trigger race engine to start countdown
    
    return race


@router.post("/{race_id}/pause", response_model=Race)
async def pause_race(race_id: int):
    """Pause a running race."""
    db = get_db()
    result = db.races.search(Q.id == race_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    
    race = result[0]
    
    if race.get("state") != RaceStateEnum.RUNNING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot pause race in state: {race.get('state')}",
        )
    
    race["state"] = RaceStateEnum.PAUSED.value
    db.races.update(race, Q.id == race_id)
    return race


@router.post("/{race_id}/resume", response_model=Race)
async def resume_race(race_id: int):
    """Resume a paused race."""
    db = get_db()
    result = db.races.search(Q.id == race_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    
    race = result[0]
    
    if race.get("state") != RaceStateEnum.PAUSED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resume race in state: {race.get('state')}",
        )
    
    race["state"] = RaceStateEnum.RUNNING.value
    db.races.update(race, Q.id == race_id)
    return race


@router.post("/{race_id}/stop", response_model=Race)
async def stop_race(race_id: int):
    """Stop/cancel a race."""
    db = get_db()
    result = db.races.search(Q.id == race_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    
    race = result[0]
    
    if race.get("state") in (RaceStateEnum.FINISHED.value, RaceStateEnum.CANCELLED.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Race already ended with state: {race.get('state')}",
        )
    
    race["state"] = RaceStateEnum.CANCELLED.value
    db.races.update(race, Q.id == race_id)
    return race


@router.delete("/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_race(race_id: int):
    """Delete a race."""
    db = get_db()
    if not db.races.search(Q.id == race_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    db.races.remove(Q.id == race_id)
