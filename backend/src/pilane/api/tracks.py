"""Tracks API router using TinyDB."""

from fastapi import APIRouter, HTTPException, status

from pilane.database import get_db, generate_id, now_iso, Q
from pilane.schemas import TrackCreate, Track

router = APIRouter()


@router.get("/", response_model=list[Track])
async def list_tracks():
    """Get all tracks."""
    db = get_db()
    tracks = db.tracks.all()
    return sorted(tracks, key=lambda t: t.get("name", ""))


@router.post("/", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_track(track: TrackCreate):
    """Create a new track."""
    db = get_db()
    
    # Check if track name already exists
    if db.tracks.search(Q.name == track.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Track name already exists",
        )
    
    now = now_iso()
    new_track = {
        "id": generate_id(db.tracks),
        **track.model_dump(),
        "track_record_ms": None,
        "track_record_car_id": None,
        "created_at": now,
        "updated_at": now,
    }
    db.tracks.insert(new_track)
    return new_track


@router.get("/{track_id}", response_model=Track)
async def get_track(track_id: int):
    """Get a specific track by ID."""
    db = get_db()
    result = db.tracks.search(Q.id == track_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return result[0]


@router.put("/{track_id}", response_model=Track)
async def update_track(track_id: int, track_update: TrackCreate):
    """Update a track's layout and settings."""
    db = get_db()
    
    result = db.tracks.search(Q.id == track_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    
    existing = result[0]
    updated = {
        **existing,
        **track_update.model_dump(),
        "updated_at": now_iso(),
    }
    db.tracks.update(updated, Q.id == track_id)
    return updated


@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(track_id: int):
    """Delete a track."""
    db = get_db()
    if not db.tracks.search(Q.id == track_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    db.tracks.remove(Q.id == track_id)
