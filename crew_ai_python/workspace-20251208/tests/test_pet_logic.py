import pytest
from datetime import datetime, timedelta
from app.pet_service import (
    create_pet,
    get_pet_by_user_id,
    feed_pet,
    play_with_pet,
    put_pet_to_sleep,
    wake_up_pet,
    decay_pet_stats,
    check_evolution,
    process_pet_updates,
    clamp_stat,
    VALID_SPECIES
)
from app.models import Pet

def test_create_pet(test_db, test_user):
    pet = create_pet(test_db, test_user.id, "Fluffy", "cat")
    
    assert pet.name == "Fluffy"
    assert pet.species == "cat"
    assert pet.user_id == test_user.id
    assert pet.hunger == 50
    assert pet.happiness == 50
    assert pet.energy == 50
    assert pet.stage == "normal"
    assert pet.is_sleeping is False

def test_create_pet_invalid_species(test_db, test_user):
    with pytest.raises(ValueError, match="Invalid species"):
        create_pet(test_db, test_user.id, "Invalid", "unicorn")

def test_get_pet_by_user_id(test_db, test_pet):
    pet = get_pet_by_user_id(test_db, test_pet.user_id)
    assert pet is not None
    assert pet.id == test_pet.id
    
    # Test non-existent user
    pet = get_pet_by_user_id(test_db, 99999)
    assert pet is None

def test_clamp_stat():
    assert clamp_stat(-10) == 0
    assert clamp_stat(0) == 0
    assert clamp_stat(50) == 50
    assert clamp_stat(100) == 100
    assert clamp_stat(150) == 100

def test_feed_pet(test_db, test_pet):
    original_hunger = test_pet.hunger
    original_updated_at = test_pet.updated_at
    pet = feed_pet(test_db, test_pet)
    
    assert pet.hunger == clamp_stat(original_hunger + 20)
    assert pet.updated_at >= original_updated_at  # Should be updated or same

def test_feed_sleeping_pet(test_db, test_pet):
    test_pet.is_sleeping = True
    test_db.commit()
    
    with pytest.raises(ValueError, match="Cannot feed a sleeping pet"):
        feed_pet(test_db, test_pet)

def test_feed_overfed_pet(test_db, test_pet):
    # Set hunger to high value to trigger overfeed
    test_pet.hunger = 85
    test_db.commit()
    
    original_happiness = test_pet.happiness
    pet = feed_pet(test_db, test_pet)
    
    assert pet.hunger > 90  # Should be overfed
    assert pet.happiness < original_happiness  # Should decrease happiness

def test_play_with_pet(test_db, test_pet):
    original_happiness = test_pet.happiness
    original_energy = test_pet.energy
    
    pet = play_with_pet(test_db, test_pet)
    
    assert pet.happiness == clamp_stat(original_happiness + 15)
    assert pet.energy == clamp_stat(original_energy - 10)

def test_play_with_sleeping_pet(test_db, test_pet):
    test_pet.is_sleeping = True
    test_db.commit()
    
    with pytest.raises(ValueError, match="Cannot play with a sleeping pet"):
        play_with_pet(test_db, test_pet)

def test_put_pet_to_sleep(test_db, test_pet):
    pet = put_pet_to_sleep(test_db, test_pet, sleep_minutes=2)
    
    assert pet.is_sleeping is True
    assert pet.sleep_until is not None
    assert pet.sleep_until > datetime.utcnow()

def test_put_already_sleeping_pet_to_sleep(test_db, test_pet):
    test_pet.is_sleeping = True
    test_db.commit()
    
    with pytest.raises(ValueError, match="Pet is already sleeping"):
        put_pet_to_sleep(test_db, test_pet)

def test_wake_up_pet(test_db, test_pet):
    # Put pet to sleep for a very short time
    test_pet.is_sleeping = True
    test_pet.sleep_until = datetime.utcnow() - timedelta(minutes=1)  # Already past sleep time
    original_energy = test_pet.energy
    test_db.commit()
    
    pet = wake_up_pet(test_db, test_pet)
    
    assert pet.is_sleeping is False
    assert pet.sleep_until is None
    assert pet.energy == clamp_stat(original_energy + 30)

def test_wake_up_pet_not_ready(test_db, test_pet):
    # Put pet to sleep for future time
    test_pet.is_sleeping = True
    test_pet.sleep_until = datetime.utcnow() + timedelta(hours=2)
    test_db.commit()
    
    pet = wake_up_pet(test_db, test_pet)
    
    # Should still be sleeping
    assert pet.is_sleeping is True
    assert pet.sleep_until is not None

def test_decay_pet_stats(test_db, test_pet):
    # Set last decay to 2 minutes ago
    original_last_decay = datetime.utcnow() - timedelta(minutes=2)
    test_pet.last_decay = original_last_decay
    original_hunger = test_pet.hunger
    original_happiness = test_pet.happiness
    original_energy = test_pet.energy
    test_db.commit()
    
    pet = decay_pet_stats(test_db, test_pet)
    
    # Should decay by 2 points (2 minutes)
    assert pet.hunger == clamp_stat(original_hunger - 2)
    assert pet.happiness == clamp_stat(original_happiness - 2)
    assert pet.energy == clamp_stat(original_energy - 2)
    assert pet.last_decay >= original_last_decay  # Should be updated

def test_decay_sleeping_pet_stats(test_db, test_pet):
    # Sleeping pets should not decay
    test_pet.is_sleeping = True
    test_pet.last_decay = datetime.utcnow() - timedelta(minutes=5)
    original_hunger = test_pet.hunger
    test_db.commit()
    
    pet = decay_pet_stats(test_db, test_pet)
    
    # Stats should not change for sleeping pet
    assert pet.hunger == original_hunger

def test_evolution_eligibility(test_db, test_pet):
    # Set high stats and force last_decay to be old enough to trigger check
    test_pet.hunger = 75
    test_pet.happiness = 75
    test_pet.energy = 75
    test_pet.evolution_eligible_since = None
    test_pet.last_decay = datetime.utcnow() - timedelta(minutes=2)  # Force decay check
    test_db.commit()
    
    pet = decay_pet_stats(test_db, test_pet)
    
    # Should become eligible for evolution
    assert pet.evolution_eligible_since is not None

def test_evolution_eligibility_lost(test_db, test_pet):
    # Set evolution eligible then reduce stats
    test_pet.evolution_eligible_since = datetime.utcnow()
    test_pet.hunger = 60  # Below threshold
    test_pet.happiness = 75
    test_pet.energy = 75
    test_pet.last_decay = datetime.utcnow() - timedelta(minutes=2)  # Force decay check
    test_db.commit()
    
    pet = decay_pet_stats(test_db, test_pet)
    
    # Should lose evolution eligibility
    assert pet.evolution_eligible_since is None

def test_check_evolution(test_db, test_pet):
    # Set evolution eligible for more than 24 hours ago
    test_pet.evolution_eligible_since = datetime.utcnow() - timedelta(hours=25)
    test_pet.stage = "normal"
    test_db.commit()
    
    pet = check_evolution(test_db, test_pet)
    
    assert pet.stage == "evolved"

def test_check_evolution_not_ready(test_db, test_pet):
    # Set evolution eligible for less than 24 hours ago
    test_pet.evolution_eligible_since = datetime.utcnow() - timedelta(hours=12)
    test_pet.stage = "normal"
    test_db.commit()
    
    pet = check_evolution(test_db, test_pet)
    
    assert pet.stage == "normal"  # Should not evolve yet

def test_check_evolution_already_evolved(test_db, test_pet):
    test_pet.stage = "evolved"
    test_pet.evolution_eligible_since = datetime.utcnow() - timedelta(hours=25)
    test_db.commit()
    
    pet = check_evolution(test_db, test_pet)
    
    assert pet.stage == "evolved"  # Should stay evolved

def test_process_pet_updates(test_db, test_pet):
    # Set up pet for multiple updates
    test_pet.is_sleeping = True
    test_pet.sleep_until = datetime.utcnow() - timedelta(minutes=1)  # Should wake up
    test_pet.last_decay = datetime.utcnow() - timedelta(minutes=2)  # Should decay
    test_pet.hunger = 75
    test_pet.happiness = 75
    test_pet.energy = 75
    test_db.commit()
    
    pet = process_pet_updates(test_db, test_pet)
    
    # Should have woken up
    assert pet.is_sleeping is False
    # Should have decayed (but gained energy from sleep)
    # Should be eligible for evolution
    assert pet.evolution_eligible_since is not None
