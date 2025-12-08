"""SQLAlchemy models for users and pets."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class PetSpecies(str, enum.Enum):
    """Available pet species."""
    OTTER = "otter"
    CAT = "cat"
    DRAGON = "dragon"
    AXOLOTL = "axolotl"


class PetStage(str, enum.Enum):
    """Pet evolution stages."""
    NORMAL = "normal"
    EVOLVED = "evolved"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to pet
    pet = relationship("Pet", back_populates="owner", uselist=False)


class Pet(Base):
    """Pet model."""
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(Enum(PetSpecies), nullable=False)
    hunger = Column(Integer, default=50)  # 0-100
    happiness = Column(Integer, default=50)  # 0-100
    energy = Column(Integer, default=50)  # 0-100
    stage = Column(Enum(PetStage), default=PetStage.NORMAL)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_decay = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    owner = relationship("User", back_populates="pet")
