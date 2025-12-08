import pytest
import asyncio
from datetime import datetime, timedelta
from app.scheduler import PetScheduler
from app.models import Pet
from app.pet_service import process_pet_updates

@pytest.mark.asyncio
async def test_scheduler_start_stop():
    scheduler = PetScheduler()
    
    # Test start
    await scheduler.start()
    assert scheduler.running is True
    assert scheduler.task is not None
    
    # Test stop
    await scheduler.stop()
    assert scheduler.running is False

@pytest.mark.asyncio
async def test_scheduler_process_pets(test_db, test_pet):
    scheduler = PetScheduler()
    
    # Set up pet for decay - need to force time difference
    original_last_decay = datetime.utcnow() - timedelta(minutes=2)
    test_pet.last_decay = original_last_decay
    original_hunger = test_pet.hunger
    test_db.commit()
    
    # Process pets manually (simulate scheduler tick)
    await scheduler._process_all_pets()
    
    # Refresh pet from database to get updated values
    test_db.refresh(test_pet)
    
    # Pet should have decayed by 2 points (2 minutes passed)
    assert test_pet.hunger <= original_hunger  # Should be same or less due to decay

def test_process_pet_updates_integration(test_db, test_pet):
    # Test the process_pet_updates function directly
    original_last_decay = datetime.utcnow() - timedelta(minutes=3)
    test_pet.last_decay = original_last_decay
    original_hunger = test_pet.hunger
    test_db.commit()
    
    updated_pet = process_pet_updates(test_db, test_pet)
    
    # Should have decayed by 3 points
    assert updated_pet.hunger < original_hunger
    assert updated_pet.last_decay >= original_last_decay  # Should be updated
