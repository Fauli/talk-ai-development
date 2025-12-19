"""Pet service: core game logic for pet interactions."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Pet, User


def clamp_stat(value: int) -> int:
    """Clamp a stat value between MIN and MAX."""
    return max(settings.MIN_STAT_VALUE, min(settings.MAX_STAT_VALUE, value))


def create_pet(db: Session, user: User, name: str, species: str) -> Pet:
    """Create a new pet for a user."""
    if species not in settings.VALID_SPECIES:
        raise ValueError(f"Invalid species. Must be one of: {settings.VALID_SPECIES}")

    # Check if user already has a pet
    existing_pet = db.query(Pet).filter(Pet.user_id == user.id).first()
    if existing_pet:
        raise ValueError("User already has a pet")

    pet = Pet(
        user_id=user.id,
        name=name,
        species=species,
        hunger=settings.INITIAL_STAT_VALUE,
        happiness=settings.INITIAL_STAT_VALUE,
        energy=settings.INITIAL_STAT_VALUE,
        stage="baby",
        last_decay=datetime.utcnow(),
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


def get_pet_for_user(db: Session, user: User) -> Optional[Pet]:
    """Get the pet for a user, or None if they don't have one."""
    return db.query(Pet).filter(Pet.user_id == user.id).first()


def check_and_wake_pet(db: Session, pet: Pet) -> bool:
    """Check if a sleeping pet should wake up. Returns True if pet woke up."""
    if not pet.is_sleeping:
        return False

    now = datetime.utcnow()
    if pet.sleep_until and now >= pet.sleep_until:
        pet.is_sleeping = False
        pet.sleep_until = None
        pet.energy = clamp_stat(pet.energy + 30)
        pet.updated_at = now
        db.commit()
        return True

    return False


def feed_pet(db: Session, pet: Pet) -> dict:
    """Feed the pet. Returns result with any messages."""
    check_and_wake_pet(db, pet)

    if pet.is_sleeping:
        return {"success": False, "message": "Your pet is sleeping!"}

    pet.hunger = clamp_stat(pet.hunger + 20)
    messages = []

    # Overfed penalty
    if pet.hunger > 90:
        pet.happiness = clamp_stat(pet.happiness - 10)
        messages.append("Your pet is overfed and feels uncomfortable!")

    pet.updated_at = datetime.utcnow()
    check_evolution(db, pet)
    db.commit()

    return {"success": True, "message": " ".join(messages) if messages else "Yum! Your pet enjoyed the food!"}


def play_with_pet(db: Session, pet: Pet) -> dict:
    """Play with the pet. Returns result with any messages."""
    check_and_wake_pet(db, pet)

    if pet.is_sleeping:
        return {"success": False, "message": "Your pet is sleeping!"}

    pet.happiness = clamp_stat(pet.happiness + 15)
    pet.energy = clamp_stat(pet.energy - 10)
    pet.updated_at = datetime.utcnow()

    messages = []
    if pet.energy < 20:
        messages.append("Your pet is getting tired!")

    check_evolution(db, pet)
    db.commit()

    return {"success": True, "message": " ".join(messages) if messages else "Your pet had fun playing!"}


def put_pet_to_sleep(db: Session, pet: Pet) -> dict:
    """Put the pet to sleep for 2 minutes."""
    check_and_wake_pet(db, pet)

    if pet.is_sleeping:
        remaining = (pet.sleep_until - datetime.utcnow()).total_seconds() if pet.sleep_until else 0
        return {"success": False, "message": f"Your pet is already sleeping! ({int(remaining)}s remaining)"}

    pet.is_sleeping = True
    pet.sleep_until = datetime.utcnow() + timedelta(minutes=settings.SLEEP_DURATION_MINUTES)
    pet.updated_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Your pet is now sleeping. Sweet dreams!"}


def decay_stats(db: Session, pet: Pet) -> None:
    """Decay pet stats by 1 (called every minute for non-sleeping pets)."""
    if pet.is_sleeping:
        return

    pet.hunger = clamp_stat(pet.hunger - 1)
    pet.happiness = clamp_stat(pet.happiness - 1)
    pet.energy = clamp_stat(pet.energy - 1)
    pet.last_decay = datetime.utcnow()
    pet.updated_at = datetime.utcnow()

    check_evolution(db, pet)
    db.commit()


def check_evolution(db: Session, pet: Pet) -> bool:
    """Check and handle evolution. Returns True if pet evolved."""
    if pet.stage == "evolved":
        return False

    all_stats_above_threshold = (
        pet.hunger > settings.EVOLUTION_THRESHOLD and
        pet.happiness > settings.EVOLUTION_THRESHOLD and
        pet.energy > settings.EVOLUTION_THRESHOLD
    )

    now = datetime.utcnow()

    if all_stats_above_threshold:
        if pet.evolution_eligible_since is None:
            pet.evolution_eligible_since = now
        else:
            eligible_duration = (now - pet.evolution_eligible_since).total_seconds() / 60
            if eligible_duration >= settings.EVOLUTION_TIME_MINUTES:
                pet.stage = "evolved"
                pet.evolution_eligible_since = None
                db.commit()
                return True
    else:
        pet.evolution_eligible_since = None

    return False


def get_pet_status(db: Session, pet: Pet) -> dict:
    """Get the current status of a pet as a dictionary."""
    check_and_wake_pet(db, pet)

    status = {
        "id": pet.id,
        "name": pet.name,
        "species": pet.species,
        "hunger": pet.hunger,
        "happiness": pet.happiness,
        "energy": pet.energy,
        "stage": pet.stage,
        "is_sleeping": pet.is_sleeping,
        "sleep_until": pet.sleep_until.isoformat() if pet.sleep_until else None,
        "created_at": pet.created_at.isoformat() if pet.created_at else None,
    }

    # Add notifications
    notifications = []
    if pet.hunger < 30:
        notifications.append("Your pet is hungry!")
    if pet.happiness < 30:
        notifications.append("Your pet is sad!")
    if pet.energy < 30:
        notifications.append("Your pet is tired!")
    if pet.stage == "evolved":
        notifications.append(f"Your {pet.species} has evolved!")

    status["notifications"] = notifications
    return status
