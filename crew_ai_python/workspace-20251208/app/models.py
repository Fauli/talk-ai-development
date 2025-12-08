from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    pet = relationship("Pet", back_populates="owner", uselist=False)

class Pet(Base):
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)  # otter, cat, dragon, axolotl
    hunger = Column(Integer, default=50)  # 0-100
    happiness = Column(Integer, default=50)  # 0-100
    energy = Column(Integer, default=50)  # 0-100
    stage = Column(String, default="normal")  # normal, evolved
    is_sleeping = Column(Boolean, default=False)
    sleep_until = Column(DateTime, nullable=True)
    last_decay = Column(DateTime, default=datetime.utcnow)
    evolution_eligible_since = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="pet")