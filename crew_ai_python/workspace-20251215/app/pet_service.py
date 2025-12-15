"""Pet business logic and state management."""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .config import settings
from .models import User, Pet


VALID_SPECIES = settings.valid_species


def get_pet_by_user_id(db: Session, user_id: int) -> Optional[Pet]:
    """Get pet by user ID."""
    return db.query(Pet).filter(Pet.user_id == user_id).first()


def create_pet(db: Session, user_id: int, name: str, species: str) -> Pet:
    """Create a new pet for the user."""
    # Validate species
    if species not in VALID_SPECIES:
        raise ValueError(f"Invalid species. Must be one of: {', '.join(VALID_SPECIES)}")
    
    # Check if user already has a pet
    existing_pet = get_pet_by_user_id(db, user_id)
    if existing_pet:
        raise ValueError("User already has a pet")
    
    # Create new pet
    pet = Pet(
        user_id=user_id,
        name=name,
        species=species,
        hunger=50,
        happiness=50,
        energy=50
    )
    
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


def get_pet_status(db: Session, pet: Pet) -> dict:
    """Get current pet status with real-time updates."""
    # Apply any pending stat decay
    apply_stat_decay(db, pet.id)
    
    # Check if pet should wake up
    if pet.is_sleeping and pet.sleep_until and datetime.utcnow() >= pet.sleep_until:
        wake_up_pet(db, pet.id)
    
    # Check evolution eligibility
    check_evolution_eligibility(db, pet)
    
    db.refresh(pet)
    return pet.to_dict()


def feed_pet(db: Session, pet_id: int) -> dict:
    """Feed the pet."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise ValueError("Pet not found")
    
    if not pet.is_awake():
        raise ValueError("Cannot feed a sleeping pet")
    
    # Apply stat changes
    pet.hunger = min(100, pet.hunger + 20)
    
    # Overfed penalty
    if pet.hunger > 90:
        pet.happiness = max(0, pet.happiness - 10)
    
    pet.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True}


def play_with_pet(db: Session, pet_id: int) -> dict:
    """Play with the pet."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise ValueError("Pet not found")
    
    if not pet.is_awake():
        raise ValueError("Cannot play with a sleeping pet")
    
    # Apply stat changes
    pet.happiness = min(100, pet.happiness + 15)
    pet.energy = max(0, pet.energy - 10)
    pet.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"success": True}


def put_pet_to_sleep(db: Session, pet_id: int) -> dict:
    """Put the pet to sleep."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise ValueError("Pet not found")
    
    if pet.is_sleeping:
        raise ValueError("Pet is already sleeping")
    
    # Set sleep state
    pet.is_sleeping = True
    pet.sleep_until = datetime.utcnow() + timedelta(minutes=settings.sleep_duration_minutes)
    pet.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"success": True}


def wake_up_pet(db: Session, pet_id: int) -> dict:
    """Wake up the pet and restore energy."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise ValueError("Pet not found")
    
    pet.is_sleeping = False
    pet.sleep_until = None
    pet.energy = min(100, pet.energy + 30)
    pet.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True}


def apply_stat_decay(db: Session, pet_id: int) -> None:
    """Apply stat decay based on time elapsed."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet or not pet.is_awake():
        return  # No decay while sleeping or if pet not found
    
    now = datetime.utcnow()
    time_diff = now - pet.last_decay
    minutes_elapsed = int(time_diff.total_seconds() / 60)
    
    if minutes_elapsed > 0:
        # Apply decay
        pet.hunger = max(0, pet.hunger - minutes_elapsed)
        pet.happiness = max(0, pet.happiness - minutes_elapsed)
        pet.energy = max(0, pet.energy - minutes_elapsed)
        pet.last_decay = now
        pet.updated_at = now
        db.commit()


def check_evolution_eligibility(db: Session, pet: Pet) -> None:
    """Check and update evolution eligibility."""
    if pet.stage == "evolved":
        return
    
    # Check if all stats are above 50
    all_stats_high = pet.hunger > 50 and pet.happiness > 50 and pet.energy > 50
    
    if all_stats_high:
        if pet.evolution_eligible_since is None:
            # Start tracking eligibility
            pet.evolution_eligible_since = datetime.utcnow()
            pet.updated_at = datetime.utcnow()
            db.commit()
    else:
        if pet.evolution_eligible_since is not None:
            # Reset eligibility
            pet.evolution_eligible_since = None
            pet.updated_at = datetime.utcnow()
            db.commit()


def check_evolution(db: Session, pet_id: int) -> dict:
    """Check and perform evolution if eligible."""
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise ValueError("Pet not found")
    
    # Update evolution eligibility first
    check_evolution_eligibility(db, pet)
    
    # Check if pet can evolve (5 minutes for testing instead of 24 hours)
    if pet.can_evolve():
        pet.stage = "evolved"
        pet.evolution_eligible_since = None
        pet.updated_at = datetime.utcnow()
        db.commit()
        return {"evolved": True}
    
    return {"evolved": False}


def evolve_pet(db: Session, pet: Pet) -> dict:
    """Evolve the pet if eligible."""
    if not pet.can_evolve():
        raise ValueError("Pet is not eligible for evolution")
    
    pet.stage = "evolved"
    pet.evolution_eligible_since = None
    pet.updated_at = datetime.utcnow()
    
    db.commit()
    
    return get_pet_status(db, pet)


def get_all_pets(db: Session) -> list[Pet]:
    """Get all pets for background processing."""
    return db.query(Pet).all()