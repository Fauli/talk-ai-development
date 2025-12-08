import os
from typing import Optional

class Settings:
    DATABASE_URL: str = "sqlite:///./pixelpet.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DECAY_INTERVAL_MINUTES: int = 1
    EVOLUTION_THRESHOLD_HOURS: int = 24
    
    def __init__(self):
        # Override with environment variables if available
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
        
settings = Settings()