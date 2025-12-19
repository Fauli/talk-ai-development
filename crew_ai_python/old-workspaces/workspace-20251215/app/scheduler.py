"""Background scheduler for pet stat decay and maintenance."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from .database import SessionLocal
from .pet_service import get_all_pets, apply_stat_decay, check_evolution_eligibility
from .config import settings


logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


def decay_all_pets():
    """Process stat decay for all pets."""
    db: Session = SessionLocal()
    try:
        pets = get_all_pets(db)
        logger.info(f"Processing {len(pets)} pets for stat decay")
        
        for pet in pets:
            try:
                # Apply stat decay
                apply_stat_decay(db, pet.id)
                
                # Check evolution eligibility
                check_evolution_eligibility(db, pet)
                
            except Exception as e:
                logger.error(f"Error processing pet {pet.id}: {str(e)}")
                db.rollback()
                
    except Exception as e:
        logger.error(f"Error in decay_all_pets: {str(e)}")
    finally:
        db.close()


def process_all_pets():
    """Process stat decay and evolution for all pets."""
    decay_all_pets()  # Use the same implementation


def start_scheduler():
    """Start the background scheduler."""
    try:
        # Schedule stat decay every minute
        scheduler.add_job(
            process_all_pets,
            "interval",
            minutes=settings.decay_interval_minutes,
            id="pet_maintenance",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started")
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")


def stop_scheduler():
    """Stop the background scheduler."""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")