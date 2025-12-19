"""Configuration settings for PixelPet application."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    
    # Database
    database_url: str = "sqlite:///./pixelpet.db"
    
    # JWT Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Pet Settings
    decay_interval_minutes: int = 1
    evolution_threshold_minutes: int = 5
    sleep_duration_minutes: int = 2
    
    # Valid pet species
    valid_species: list = ["otter", "cat", "dragon", "axolotl"]


settings = Settings()
