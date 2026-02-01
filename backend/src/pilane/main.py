"""FastAPI application entry point for Pi-Lane."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from pilane.config import settings
from pilane.database import get_db
from pilane.api import users, cars, tracks, races, websocket_routes

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting {settings.app_name}...")
    logger.info(f"Hardware mode: {settings.hardware_mode}")
    logger.info(f"Data directory: {settings.data_dir}")
    
    # Initialize database (creates file if needed)
    get_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Slot car racing control system for Carrera analog tracks",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware (allow Vue dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(cars.router, prefix="/api/cars", tags=["Cars"])
app.include_router(tracks.router, prefix="/api/tracks", tags=["Tracks"])
app.include_router(races.router, prefix="/api/races", tags=["Races"])
app.include_router(websocket_routes.router, tags=["WebSocket"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": settings.app_name,
        "status": "running",
        "hardware_mode": settings.hardware_mode,
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    from pilane.websocket import manager
    return {
        "status": "healthy",
        "websocket_connections": manager.connection_count,
        "hardware_mode": settings.hardware_mode,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "pilane.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
