"""TinyDB storage for Pi-Lane - simple JSON-based persistence."""

from tinydb import TinyDB, Query
from tinydb.table import Table
from pathlib import Path
from datetime import datetime
from typing import Optional, Any
import threading

from pilane.config import settings


class Database:
    """Simple TinyDB wrapper for Pi-Lane data storage."""
    
    _instance: Optional["Database"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "Database":
        """Singleton pattern for database instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Ensure data directory exists
        data_dir = Path(settings.data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize TinyDB
        self._db = TinyDB(data_dir / "pilane_data.json", indent=2)
        self._initialized = True
    
    @property
    def users(self) -> Table:
        return self._db.table("users")
    
    @property
    def cars(self) -> Table:
        return self._db.table("cars")
    
    @property
    def tracks(self) -> Table:
        return self._db.table("tracks")
    
    @property
    def races(self) -> Table:
        return self._db.table("races")
    
    @property
    def lap_records(self) -> Table:
        return self._db.table("lap_records")
    
    def close(self):
        """Close the database."""
        self._db.close()


# Query helper
Q = Query()


def get_db() -> Database:
    """Get the database instance."""
    return Database()


def generate_id(table: Table) -> int:
    """Generate a simple incremental ID for a table."""
    all_docs = table.all()
    if not all_docs:
        return 1
    return max(doc.get("id", 0) for doc in all_docs) + 1


def now_iso() -> str:
    """Get current timestamp as ISO string."""
    return datetime.utcnow().isoformat()
