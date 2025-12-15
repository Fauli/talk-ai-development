"""SQLAlchemy models for PixelPet application."""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from .config import settings


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to pet
    pet = relationship("Pet", back_populates="owner", uselist=False)


class Pet(Base):
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)  # otter, cat, dragon, axolotl
    
    # Stats (0-100)
    hunger = Column(Integer, default=50)
    happiness = Column(Integer, default=50)
    energy = Column(Integer, default=50)
    
    # Evolution
    stage = Column(String, default="baby")  # "baby" or "evolved"
    evolution_eligible_since = Column(DateTime, nullable=True)
    
    # Sleep
    is_sleeping = Column(Boolean, default=False)
    sleep_until = Column(DateTime, nullable=True)
    
    # Timestamps
    last_decay = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    owner = relationship("User", back_populates="pet")
    
    def is_awake(self) -> bool:
        """Check if pet is currently awake."""
        if not self.is_sleeping:
            return True
        if self.sleep_until and datetime.utcnow() >= self.sleep_until:
            return True
        return False
    
    def can_evolve(self) -> bool:
        """Check if pet is eligible for evolution."""
        if self.stage == "evolved":
            return False
        if not self.evolution_eligible_since:
            return False
        
        threshold = timedelta(minutes=settings.evolution_threshold_minutes)
        return datetime.utcnow() - self.evolution_eligible_since >= threshold
    
    def to_dict(self) -> dict:
        """Convert pet to dictionary for JSON responses."""
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "stage": self.stage,
            "is_sleeping": self.is_sleeping,
            "sleep_until": self.sleep_until.isoformat() if self.sleep_until else None,
            "can_evolve": self.can_evolve(),
            "is_awake": self.is_awake(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }