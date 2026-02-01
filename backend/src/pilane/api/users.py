"""Users API router using TinyDB."""

from fastapi import APIRouter, HTTPException, status

from pilane.database import get_db, generate_id, now_iso, Q
from pilane.schemas import UserCreate, User

router = APIRouter()


@router.get("/", response_model=list[User])
async def list_users():
    """Get all registered users."""
    db = get_db()
    users = db.users.all()
    return sorted(users, key=lambda u: u.get("name", ""))


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Register a new user."""
    db = get_db()
    
    # Check if username already exists
    if db.users.search(Q.name == user.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    
    new_user = {
        "id": generate_id(db.users),
        **user.model_dump(),
        "created_at": now_iso(),
    }
    db.users.insert(new_user)
    return new_user


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID."""
    db = get_db()
    result = db.users.search(Q.id == user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return result[0]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user."""
    db = get_db()
    if not db.users.search(Q.id == user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.users.remove(Q.id == user_id)
