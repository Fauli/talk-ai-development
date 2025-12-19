"""Tests for pet service functionality."""

from datetime import datetime, timedelta

import pytest

from app import pet_service
from app.models import Pet
from app.config import settings


class TestCreatePet:
    """Tests for pet creation."""

    def test_create_pet_success(self, db, test_user):
        """Test successful pet creation."""
        pet = pet_service.create_pet(db, test_user, "Fluffy", "cat")

        assert pet is not None
        assert pet.name == "Fluffy"
        assert pet.species == "cat"
        assert pet.hunger == settings.INITIAL_STAT_VALUE
        assert pet.happiness == settings.INITIAL_STAT_VALUE
        assert pet.energy == settings.INITIAL_STAT_VALUE
        assert pet.stage == "baby"
        assert pet.is_sleeping is False

    def test_create_pet_invalid_species(self, db, test_user):
        """Test that invalid species raises error."""
        with pytest.raises(ValueError, match="Invalid species"):
            pet_service.create_pet(db, test_user, "Fluffy", "unicorn")

    def test_create_pet_duplicate(self, db, test_user, test_pet):
        """Test that creating second pet for user raises error."""
        with pytest.raises(ValueError, match="already has a pet"):
            pet_service.create_pet(db, test_user, "Another", "dragon")


class TestFeedPet:
    """Tests for feeding pet."""

    def test_feed_pet_increases_hunger(self, db, test_pet):
        """Test that feeding increases hunger stat."""
        test_pet.hunger = 50
        db.commit()

        result = pet_service.feed_pet(db, test_pet)

        assert result["success"] is True
        assert test_pet.hunger == 70  # 50 + 20

    def test_feed_pet_capped_at_100(self, db, test_pet):
        """Test that hunger cannot exceed 100."""
        test_pet.hunger = 90
        db.commit()

        pet_service.feed_pet(db, test_pet)

        assert test_pet.hunger == 100

    def test_feed_pet_overfed_penalty(self, db, test_pet):
        """Test that overfeeding reduces happiness."""
        test_pet.hunger = 80
        test_pet.happiness = 50
        db.commit()

        result = pet_service.feed_pet(db, test_pet)

        assert test_pet.hunger == 100
        assert test_pet.happiness == 40  # 50 - 10 penalty
        assert "overfed" in result["message"].lower()

    def test_feed_sleeping_pet_fails(self, db, test_pet):
        """Test that feeding sleeping pet fails."""
        test_pet.is_sleeping = True
        test_pet.sleep_until = datetime.utcnow() + timedelta(minutes=2)
        db.commit()

        result = pet_service.feed_pet(db, test_pet)

        assert result["success"] is False
        assert "sleeping" in result["message"].lower()


class TestPlayWithPet:
    """Tests for playing with pet."""

    def test_play_increases_happiness(self, db, test_pet):
        """Test that playing increases happiness."""
        test_pet.happiness = 50
        test_pet.energy = 50
        db.commit()

        result = pet_service.play_with_pet(db, test_pet)

        assert result["success"] is True
        assert test_pet.happiness == 65  # 50 + 15

    def test_play_decreases_energy(self, db, test_pet):
        """Test that playing decreases energy."""
        test_pet.energy = 50
        db.commit()

        pet_service.play_with_pet(db, test_pet)

        assert test_pet.energy == 40  # 50 - 10

    def test_play_energy_warning(self, db, test_pet):
        """Test that low energy shows warning."""
        test_pet.energy = 25
        db.commit()

        result = pet_service.play_with_pet(db, test_pet)

        assert "tired" in result["message"].lower()

    def test_play_sleeping_pet_fails(self, db, test_pet):
        """Test that playing with sleeping pet fails."""
        test_pet.is_sleeping = True
        test_pet.sleep_until = datetime.utcnow() + timedelta(minutes=2)
        db.commit()

        result = pet_service.play_with_pet(db, test_pet)

        assert result["success"] is False


class TestSleepPet:
    """Tests for putting pet to sleep."""

    def test_sleep_sets_sleeping_state(self, db, test_pet):
        """Test that sleep sets is_sleeping flag."""
        result = pet_service.put_pet_to_sleep(db, test_pet)

        assert result["success"] is True
        assert test_pet.is_sleeping is True
        assert test_pet.sleep_until is not None

    def test_sleep_already_sleeping_fails(self, db, test_pet):
        """Test that sleeping an already sleeping pet fails."""
        test_pet.is_sleeping = True
        test_pet.sleep_until = datetime.utcnow() + timedelta(minutes=2)
        db.commit()

        result = pet_service.put_pet_to_sleep(db, test_pet)

        assert result["success"] is False
        assert "already sleeping" in result["message"].lower()


class TestWakePet:
    """Tests for waking pet."""

    def test_wake_pet_after_sleep_duration(self, db, test_pet):
        """Test that pet wakes up after sleep duration."""
        test_pet.is_sleeping = True
        test_pet.sleep_until = datetime.utcnow() - timedelta(seconds=1)  # Past
        test_pet.energy = 50
        db.commit()

        woke_up = pet_service.check_and_wake_pet(db, test_pet)

        assert woke_up is True
        assert test_pet.is_sleeping is False
        assert test_pet.energy == 80  # 50 + 30

    def test_wake_pet_before_sleep_duration(self, db, test_pet):
        """Test that pet doesn't wake up before sleep duration."""
        test_pet.is_sleeping = True
        test_pet.sleep_until = datetime.utcnow() + timedelta(minutes=1)
        db.commit()

        woke_up = pet_service.check_and_wake_pet(db, test_pet)

        assert woke_up is False
        assert test_pet.is_sleeping is True


class TestDecayStats:
    """Tests for stat decay."""

    def test_decay_reduces_all_stats(self, db, test_pet):
        """Test that decay reduces all stats by 1."""
        test_pet.hunger = 50
        test_pet.happiness = 50
        test_pet.energy = 50
        db.commit()

        pet_service.decay_stats(db, test_pet)

        assert test_pet.hunger == 49
        assert test_pet.happiness == 49
        assert test_pet.energy == 49

    def test_decay_not_below_zero(self, db, test_pet):
        """Test that stats don't go below 0."""
        test_pet.hunger = 0
        test_pet.happiness = 0
        test_pet.energy = 0
        db.commit()

        pet_service.decay_stats(db, test_pet)

        assert test_pet.hunger == 0
        assert test_pet.happiness == 0
        assert test_pet.energy == 0

    def test_decay_skipped_when_sleeping(self, db, test_pet):
        """Test that decay is skipped for sleeping pets."""
        test_pet.hunger = 50
        test_pet.is_sleeping = True
        test_pet.sleep_until = datetime.utcnow() + timedelta(minutes=2)
        db.commit()

        pet_service.decay_stats(db, test_pet)

        assert test_pet.hunger == 50  # Unchanged


class TestEvolution:
    """Tests for pet evolution."""

    def test_evolution_eligibility_starts(self, db, test_pet):
        """Test that evolution eligibility starts when all stats > 50."""
        test_pet.hunger = 60
        test_pet.happiness = 60
        test_pet.energy = 60
        test_pet.evolution_eligible_since = None
        db.commit()

        pet_service.check_evolution(db, test_pet)

        assert test_pet.evolution_eligible_since is not None

    def test_evolution_eligibility_resets(self, db, test_pet):
        """Test that eligibility resets when stat drops below threshold."""
        test_pet.hunger = 60
        test_pet.happiness = 60
        test_pet.energy = 40  # Below threshold
        test_pet.evolution_eligible_since = datetime.utcnow()
        db.commit()

        pet_service.check_evolution(db, test_pet)

        assert test_pet.evolution_eligible_since is None

    def test_evolution_after_5_minutes(self, db, test_pet):
        """Test that pet evolves after 5 minutes of eligibility."""
        test_pet.hunger = 60
        test_pet.happiness = 60
        test_pet.energy = 60
        test_pet.stage = "baby"
        test_pet.evolution_eligible_since = datetime.utcnow() - timedelta(minutes=6)
        db.commit()

        evolved = pet_service.check_evolution(db, test_pet)

        assert evolved is True
        assert test_pet.stage == "evolved"

    def test_no_double_evolution(self, db, test_pet):
        """Test that already evolved pet doesn't evolve again."""
        test_pet.stage = "evolved"
        test_pet.hunger = 60
        test_pet.happiness = 60
        test_pet.energy = 60
        db.commit()

        evolved = pet_service.check_evolution(db, test_pet)

        assert evolved is False
