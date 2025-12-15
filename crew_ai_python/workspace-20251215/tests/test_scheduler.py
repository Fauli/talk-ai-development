"""Tests for the background scheduler functionality."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.models import Pet, User
from app.scheduler import decay_all_pets


def test_decay_all_pets(db_session):
    """Test that decay_all_pets processes all pets correctly."""
    # Create users and pets
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    
    # Create pets with old last_decay times
    old_time = datetime.utcnow() - timedelta(minutes=2)
    
    pet1 = Pet(
        user_id=user1.id,
        name="Pet1",
        species="cat",
        hunger=60,
        happiness=70,
        energy=80,
        last_decay=old_time
    )
    
    pet2 = Pet(
        user_id=user2.id,
        name="Pet2", 
        species="dog",
        hunger=50,
        happiness=60,
        energy=70,
        last_decay=old_time,
        is_sleeping=True  # Sleeping pets should not decay
    )
    
    db_session.add(pet1)
    db_session.add(pet2)
    db_session.commit()
    
    pet1_id = pet1.id
    pet2_id = pet2.id

    # Mock the database session for the scheduler (don't close it)
    with patch('app.scheduler.SessionLocal', return_value=db_session):
        with patch.object(db_session, 'close'):  # Prevent session close
            # Run decay function
            decay_all_pets()

    # Refresh to get updated values
    db_session.refresh(pet1)
    db_session.refresh(pet2)

    # Check that awake pet decayed (2 minutes = 2 points)
    assert pet1.hunger == 58  # 60 - 2
    assert pet1.happiness == 68  # 70 - 2
    assert pet1.energy == 78  # 80 - 2
    assert pet1.last_decay > old_time

    # Check that sleeping pet did not decay
    assert pet2.hunger == 50  # Unchanged
    assert pet2.happiness == 60  # Unchanged
    assert pet2.energy == 70  # Unchanged


def test_decay_respects_minimum_values(db_session):
    """Test that stats don't decay below 0."""
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # Create pet with very low stats
    old_time = datetime.utcnow() - timedelta(minutes=2)
    pet = Pet(
        user_id=user.id,
        name="LowStatsPet",
        species="axolotl",
        hunger=0,
        happiness=1,
        energy=0,
        last_decay=old_time
    )
    
    db_session.add(pet)
    db_session.commit()
    
    # Mock the database session for the scheduler
    with patch('app.scheduler.SessionLocal', return_value=db_session):
        # Run decay function
        decay_all_pets()

    # Check that stats don't go below 0 (2 minutes = 2 points decay)
    assert pet.hunger == 0  # Already at minimum, stays 0
    assert pet.happiness == 0  # 1 - 2 = -1, clamped to 0
    assert pet.energy == 0  # Already at minimum, stays 0


def test_no_decay_for_recent_pets(db_session):
    """Test that pets with recent last_decay don't get processed."""
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # Create pet with recent last_decay time
    recent_time = datetime.utcnow() - timedelta(seconds=30)  # 30 seconds ago
    pet = Pet(
        user_id=user.id,
        name="RecentPet",
        species="dragon",
        hunger=60,
        happiness=70,
        energy=80,
        last_decay=recent_time
    )
    
    db_session.add(pet)
    db_session.commit()
    
    initial_hunger = pet.hunger
    initial_happiness = pet.happiness
    initial_energy = pet.energy
    
    # Mock the database session for the scheduler (don't close it)
    with patch('app.scheduler.SessionLocal', return_value=db_session):
        with patch.object(db_session, 'close'):  # Prevent session close
            # Run decay function
            decay_all_pets()

    # Refresh to get updated values
    db_session.refresh(pet)

    # Check that stats didn't change (0 minutes elapsed, no decay)
    assert pet.hunger == initial_hunger
    assert pet.happiness == initial_happiness
    assert pet.energy == initial_energy


def test_evolution_eligibility_tracking(db_session):
    """Test that evolution eligibility is tracked correctly during decay."""
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # Create pet with high stats (above 50)
    old_time = datetime.utcnow() - timedelta(minutes=2)
    pet = Pet(
        user_id=user.id,
        name="HighStatsPet",
        species="otter",
        hunger=60,
        happiness=70,
        energy=80,
        last_decay=old_time,
        evolution_eligible_since=None
    )
    
    db_session.add(pet)
    db_session.commit()
    
    # Mock the database session for the scheduler (don't close it)
    with patch('app.scheduler.SessionLocal', return_value=db_session):
        with patch.object(db_session, 'close'):  # Prevent session close
            # Run decay function
            decay_all_pets()

    # Refresh to get updated values
    db_session.refresh(pet)

    # After decay: hunger=58, happiness=68, energy=78 (all still > 50)
    # So evolution_eligible_since should be set
    assert pet.evolution_eligible_since is not None
    assert pet.evolution_eligible_since <= datetime.utcnow()


def test_evolution_eligibility_reset_on_low_stats(db_session):
    """Test that evolution eligibility resets when stats drop below 50."""
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # Create pet with stats that will drop below 50 after decay
    old_time = datetime.utcnow() - timedelta(minutes=2)
    eligible_time = datetime.utcnow() - timedelta(minutes=3)
    
    pet = Pet(
        user_id=user.id,
        name="BorderlinePet",
        species="cat",
        hunger=50,  # Will become 49 after decay
        happiness=70,
        energy=80,
        last_decay=old_time,
        evolution_eligible_since=eligible_time
    )
    
    db_session.add(pet)
    db_session.commit()
    
    # Mock the database session for the scheduler (don't close it)
    with patch('app.scheduler.SessionLocal', return_value=db_session):
        with patch.object(db_session, 'close'):  # Prevent session close
            # Run decay function
            decay_all_pets()

    # Refresh to get updated values
    db_session.refresh(pet)

    # After decay: hunger=48 (< 50), so evolution eligibility should reset
    assert pet.evolution_eligible_since is None
