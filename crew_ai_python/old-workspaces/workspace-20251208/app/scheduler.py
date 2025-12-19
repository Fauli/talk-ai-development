import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Pet
from .pet_service import process_pet_updates
from .config import settings
import logging

logger = logging.getLogger(__name__)

class PetScheduler:
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the background scheduler"""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._run_scheduler())
            logger.info("Pet scheduler started")
    
    async def stop(self):
        """Stop the background scheduler"""
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            logger.info("Pet scheduler stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                await self._process_all_pets()
                # Wait for the specified interval
                await asyncio.sleep(settings.DECAY_INTERVAL_MINUTES * 60)
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def _process_all_pets(self):
        """Process all pets for stat decay and evolution"""
        db = SessionLocal()
        try:
            pets = db.query(Pet).all()
            for pet in pets:
                try:
                    process_pet_updates(db, pet)
                except Exception as e:
                    logger.error(f"Error processing pet {pet.id}: {e}")
            logger.debug(f"Processed {len(pets)} pets")
        except Exception as e:
            logger.error(f"Error in _process_all_pets: {e}")
        finally:
            db.close()

# Global scheduler instance
scheduler = PetScheduler()