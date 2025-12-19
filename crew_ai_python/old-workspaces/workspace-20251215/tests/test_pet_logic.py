"""Tests for pet logic and mechanics."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.models import Pet, User
from app.pet_service import (
    create_pet, feed_pet, play_with_pet, put_pet_to_sleep,
    wake_up_pet, apply_stat_decay, check_evolution
)


def test_create_pet(db_session):
    """Test pet creation."""
    # Create a user first
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    # Create pet
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    
    assert pet.name == "TestPet"
    assert pet.species == "cat"
    assert pet.hunger == 50
    assert pet.happiness == 50
    assert pet.energy == 50
    assert pet.stage == "baby"
    assert pet.is_sleeping is False


def test_feed_pet(db_session):
    """Test feeding a pet."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    initial_hunger = pet.hunger
    
    # Feed pet
    result = feed_pet(db_session, pet.id)
    
    assert result["success"] is True
    assert pet.hunger == min(100, initial_hunger + 20)


def test_feed_pet_overfed_penalty(db_session):
    """Test overfed penalty when feeding."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    pet.hunger = 95  # High hunger to trigger overfed penalty
    db_session.commit()
    
    initial_happiness = pet.happiness
    
    # Feed pet
    result = feed_pet(db_session, pet.id)
    
    assert result["success"] is True
    assert pet.hunger == 100  # Capped at 100
    assert pet.happiness == max(0, initial_happiness - 10)  # Penalty applied


def test_play_with_pet(db_session):
    """Test playing with a pet."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    initial_happiness = pet.happiness
    initial_energy = pet.energy
    
    # Play with pet
    result = play_with_pet(db_session, pet.id)
    
    assert result["success"] is True
    assert pet.happiness == min(100, initial_happiness + 15)
    assert pet.energy == max(0, initial_energy - 10)


def test_put_pet_to_sleep(db_session):
    """Test putting pet to sleep."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    
    # Put pet to sleep
    result = put_pet_to_sleep(db_session, pet.id)
    
    assert result["success"] is True
    assert pet.is_sleeping is True
    assert pet.sleep_until is not None
    assert pet.sleep_until > datetime.utcnow()


def test_wake_up_pet(db_session):
    """Test waking up a pet."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    
    # Put pet to sleep first
    put_pet_to_sleep(db_session, pet.id)
    initial_energy = pet.energy
    
    # Manually set sleep_until to past time to allow waking
    pet.sleep_until = datetime.utcnow() - timedelta(seconds=1)
    db_session.commit()
    
    # Wake up pet
    result = wake_up_pet(db_session, pet.id)
    
    assert result["success"] is True
    assert pet.is_sleeping is False
    assert pet.sleep_until is None
    assert pet.energy == min(100, initial_energy + 30)


def test_stat_decay(db_session):
    """Test stat decay functionality."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    
    # Set last_decay to past time to trigger decay
    pet.last_decay = datetime.utcnow() - timedelta(minutes=2)
    db_session.commit()
    
    initial_hunger = pet.hunger
    initial_happiness = pet.happiness
    initial_energy = pet.energy
    
    # Apply stat decay
    apply_stat_decay(db_session, pet.id)

    # 2 minutes elapsed = 2 points decay per stat
    assert pet.hunger == max(0, initial_hunger - 2)
    assert pet.happiness == max(0, initial_happiness - 2)
    assert pet.energy == max(0, initial_energy - 2)


def test_evolution_eligibility(db_session):
    """Test pet evolution eligibility."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    
    # Set high stats and past evolution time
    pet.hunger = 60
    pet.happiness = 60
    pet.energy = 60
    pet.evolution_eligible_since = datetime.utcnow() - timedelta(minutes=6)
    db_session.commit()
    
    # Check evolution
    result = check_evolution(db_session, pet.id)
    
    assert result["evolved"] is True
    assert pet.stage == "evolved"


def test_no_evolution_low_stats(db_session):
    """Test that pet doesn't evolve with low stats."""
    # Create user and pet
    user = User(email="test@example.com", password_hash="dummy_hash")
    db_session.add(user)
    db_session.commit()
    
    pet = create_pet(db_session, user.id, "TestPet", "cat")
    
    # Set low stats
    pet.hunger = 30
    pet.happiness = 30
    pet.energy = 30
    db_session.commit()
    
    # Check evolution
    result = check_evolution(db_session, pet.id)
    
    assert result["evolved"] is False
    assert pet.stage == "baby"
    assert pet.evolution_eligible_since is None
