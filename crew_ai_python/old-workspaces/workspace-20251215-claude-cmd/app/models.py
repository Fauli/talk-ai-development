"""SQLAlchemy models for User and Pet."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    pet = relationship("Pet", back_populates="owner", uselist=False)


class Pet(Base):
    """Pet model representing a virtual pet."""

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

    owner = relationship("User", back_populates="pet")
