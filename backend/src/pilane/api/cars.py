"""Cars API router using TinyDB."""

from fastapi import APIRouter, HTTPException, status

from pilane.database import get_db, generate_id, now_iso, Q
from pilane.schemas import CarCreate, Car

router = APIRouter()


@router.get("/", response_model=list[Car])
async def list_cars():
    """Get all registered cars."""
    db = get_db()
    cars = db.cars.all()
    return sorted(cars, key=lambda c: c.get("name", ""))


@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
async def create_car(car: CarCreate):
    """Register a new car."""
    db = get_db()
    
    # Verify owner exists
    if not db.users.search(Q.id == car.owner_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner not found",
        )
    
    new_car = {
        "id": generate_id(db.cars),
        **car.model_dump(),
        "total_laps": 0,
        "total_races": 0,
        "best_lap_time_ms": None,
        "created_at": now_iso(),
    }
    db.cars.insert(new_car)
    return new_car


@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: int):
    """Get a specific car by ID."""
    db = get_db()
    result = db.cars.search(Q.id == car_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    return result[0]


@router.get("/user/{user_id}", response_model=list[Car])
async def list_user_cars(user_id: int):
    """Get all cars owned by a specific user."""
    db = get_db()
    cars = db.cars.search(Q.owner_id == user_id)
    return sorted(cars, key=lambda c: c.get("name", ""))


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int):
    """Delete a car."""
    db = get_db()
    if not db.cars.search(Q.id == car_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    db.cars.remove(Q.id == car_id)
