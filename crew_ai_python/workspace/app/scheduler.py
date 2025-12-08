"""Background task scheduler for pet stat decay and evolution checks."""

import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Pet
from .pet_service import PetService
import logging

logger = logging.getLogger(__name__)


class PetScheduler:
    """Scheduler for periodic pet maintenance tasks."""
    
    def __init__(self):
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the background scheduler."""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info("Pet scheduler started")
    
    async def stop(self):
        """Stop the background scheduler."""
        if not self.running:
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Pet scheduler stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop."""
        while self.running:
            try:
                await self._process_all_pets()
                # Run every minute
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in pet scheduler: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(10)
    
    async def _process_all_pets(self):
        """Process decay and evolution for all pets."""
        db = SessionLocal()
        try:
            pets = db.query(Pet).all()
            
            for pet in pets:
                try:
                    # Apply decay
                    PetService.apply_decay(db, pet)
                    
                    # Check for evolution
                    pet, evolved = PetService.check_evolution(db, pet)
                    if evolved:
                        logger.info(f"Pet {pet.name} (ID: {pet.id}) evolved!")
                
                except Exception as e:
                    logger.error(f"Error processing pet {pet.id}: {e}")
                    db.rollback()
        
        finally:
            db.close()
    
    def process_pet_on_request(self, db: Session, pet: Pet) -> Pet:
        """Process a single pet when user makes a request (fallback)."""
        try:
            # Apply decay
            pet = PetService.apply_decay(db, pet)
            
            # Check for evolution
            pet, evolved = PetService.check_evolution(db, pet)
            if evolved:
                logger.info(f"Pet {pet.name} (ID: {pet.id}) evolved on request!")
            
            return pet
        except Exception as e:
            logger.error(f"Error processing pet {pet.id} on request: {e}")
            return pet


# Global scheduler instance
scheduler = PetScheduler()


async def startup_scheduler():
    """Start the scheduler on application startup."""
    await scheduler.start()


async def shutdown_scheduler():
    """Stop the scheduler on application shutdown."""
    await scheduler.stop()


def get_scheduler() -> PetScheduler:
    """Get the global scheduler instance."""
    return scheduler
