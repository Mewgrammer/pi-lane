"""Configuration management for Pi-Lane."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Pi-Lane"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Data storage
    data_dir: str = "./data"
    
    # Hardware mode
    hardware_mode: Literal["simulation", "raspberry_pi"] = "simulation"
    
    # Track configuration
    default_lanes: int = Field(default=2, ge=1, le=8)
    
    # Race defaults
    default_race_laps: int = 10
    default_race_time_minutes: int = 5
    
    # Simulation settings
    sim_base_lap_time_ms: int = 5000  # Base lap time in milliseconds
    sim_lap_time_variance_ms: int = 500  # Random variance in lap times
    
    model_config = {
        "env_prefix": "PILANE_",
        "env_file": ".env",
    }


# Global settings instance
settings = Settings()
