from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from .models import Pet, User
from .config import settings

VALID_SPECIES = ["otter", "cat", "dragon", "axolotl"]

def create_pet(db: Session, user_id: int, name: str, species: str) -> Pet:
    """Create a new pet for a user"""
    if species not in VALID_SPECIES:
        raise ValueError(f"Invalid species. Must be one of: {VALID_SPECIES}")
    
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

def get_pet_by_user_id(db: Session, user_id: int) -> Optional[Pet]:
    """Get a user's pet"""
    return db.query(Pet).filter(Pet.user_id == user_id).first()

def clamp_stat(value: int) -> int:
    """Ensure stat stays within 0-100 range"""
    return max(0, min(100, value))

def feed_pet(db: Session, pet: Pet) -> Pet:
    """Feed the pet - increases hunger, may decrease happiness if overfed"""
    if pet.is_sleeping:
        raise ValueError("Cannot feed a sleeping pet")
    
    pet.hunger = clamp_stat(pet.hunger + 20)
    
    # Decrease happiness if overfed (hunger > 90)
    if pet.hunger > 90:
        pet.happiness = clamp_stat(pet.happiness - 10)
    
    # Force update timestamp by setting to current time
    now = datetime.utcnow()
    pet.updated_at = now
    db.commit()
    db.refresh(pet)
    return pet

def play_with_pet(db: Session, pet: Pet) -> Pet:
    """Play with the pet - increases happiness, decreases energy"""
    if pet.is_sleeping:
        raise ValueError("Cannot play with a sleeping pet")
    
    pet.happiness = clamp_stat(pet.happiness + 15)
    pet.energy = clamp_stat(pet.energy - 10)
    
    # Force update timestamp by setting to current time
    now = datetime.utcnow()
    pet.updated_at = now
    db.commit()
    db.refresh(pet)
    return pet

def put_pet_to_sleep(db: Session, pet: Pet, sleep_minutes: int = 2) -> Pet:
    """Put the pet to sleep - restores energy over time (default: 2 minutes)"""
    if pet.is_sleeping:
        raise ValueError("Pet is already sleeping")

    now = datetime.utcnow()
    pet.is_sleeping = True
    pet.sleep_until = now + timedelta(minutes=sleep_minutes)
    pet.updated_at = now
    
    db.commit()
    db.refresh(pet)
    return pet

def wake_up_pet(db: Session, pet: Pet) -> Pet:
    """Wake up the pet if sleep time is over"""
    if not pet.is_sleeping:
        return pet
    
    now = datetime.utcnow()
    if now >= pet.sleep_until:
        pet.is_sleeping = False
        pet.energy = clamp_stat(pet.energy + 30)  # Restore energy from sleep
        pet.sleep_until = None
        pet.updated_at = now
        db.commit()
        db.refresh(pet)
    
    return pet

def decay_pet_stats(db: Session, pet: Pet) -> Pet:
    """Decay pet stats over time"""
    now = datetime.utcnow()
    time_diff = now - pet.last_decay
    
    # Decay every minute
    minutes_passed = int(time_diff.total_seconds() / 60)
    
    if minutes_passed > 0:
        # Don't decay if sleeping
        if not pet.is_sleeping:
            pet.hunger = clamp_stat(pet.hunger - minutes_passed)
            pet.happiness = clamp_stat(pet.happiness - minutes_passed)
            pet.energy = clamp_stat(pet.energy - minutes_passed)
        
        # Always update last_decay and updated_at when decay occurs
        pet.last_decay = now
        pet.updated_at = now
        
        # Check if pet is eligible for evolution
        if pet.hunger >= 70 and pet.happiness >= 70 and pet.energy >= 70:
            if pet.evolution_eligible_since is None:
                pet.evolution_eligible_since = now
        else:
            pet.evolution_eligible_since = None
        
        db.commit()
        db.refresh(pet)
    
    return pet

def check_evolution(db: Session, pet: Pet) -> Pet:
    """Check if pet can evolve"""
    if pet.stage == "evolved" or pet.evolution_eligible_since is None:
        return pet
    
    now = datetime.utcnow()
    time_diff = now - pet.evolution_eligible_since
    
    # Evolve after 24 hours of high stats
    if time_diff >= timedelta(hours=settings.EVOLUTION_THRESHOLD_HOURS):
        pet.stage = "evolved"
        pet.updated_at = now
        db.commit()
        db.refresh(pet)
    
    return pet

def process_pet_updates(db: Session, pet: Pet) -> Pet:
    """Process all pet updates - wake up, decay, evolution check"""
    pet = wake_up_pet(db, pet)
    pet = decay_pet_stats(db, pet)
    pet = check_evolution(db, pet)
    return pet
