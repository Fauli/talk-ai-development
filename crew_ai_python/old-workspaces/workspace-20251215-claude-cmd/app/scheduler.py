"""Background scheduler for pet stat decay."""

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.models import Pet
from app import pet_service

scheduler = BackgroundScheduler()


def decay_all_pets():
    """Decay stats for all non-sleeping pets and wake up sleeping pets if needed."""
    db = SessionLocal()
    try:
        # Get all pets
        pets = db.query(Pet).all()

        for pet in pets:
            # Check if sleeping pet should wake up
            if pet.is_sleeping:
                pet_service.check_and_wake_pet(db, pet)
            else:
                # Decay stats for non-sleeping pets
                pet_service.decay_stats(db, pet)

    except Exception as e:
        print(f"Error in decay_all_pets: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    if not scheduler.running:
        scheduler.add_job(
            decay_all_pets,
            'interval',
            minutes=1,
            id='decay_stats',
            replace_existing=True
        )
        scheduler.start()
        print("Scheduler started - pet stats will decay every minute")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler stopped")
