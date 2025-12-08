"""Pet business logic and state management."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import Pet, PetSpecies, PetStage, User


class PetService:
    """Service for managing pet state and actions."""
    
    # Action cooldowns (in seconds)
    ACTION_COOLDOWNS = {
        "feed": 60,  # 1 minute
        "play": 60,  # 1 minute  
        "sleep": 300,  # 5 minutes
    }
    
    # Stat decay rates per minute
    DECAY_RATES = {
        "hunger": -2,
        "happiness": -1,
        "energy": -1,
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_pet(self, user: User, name: str, species: PetSpecies) -> Pet:
        """Create a new pet for a user."""
        pet = Pet(
            user_id=user.id,
            name=name,
            species=species,
            hunger=50,
            happiness=50,
            energy=50,
            stage=PetStage.NORMAL,
            updated_at=datetime.utcnow(),
            last_decay=datetime.utcnow()
        )
        self.db.add(pet)
        self.db.commit()
        self.db.refresh(pet)
        return pet
    
    def get_user_pet(self, user: User) -> Optional[Pet]:
        """Get the user's pet."""
        return self.db.query(Pet).filter(Pet.user_id == user.id).first()
    
    def apply_decay(self, pet: Pet) -> Pet:
        """Apply stat decay based on time elapsed."""
        now = datetime.utcnow()
        time_diff = now - pet.last_decay
        minutes_elapsed = time_diff.total_seconds() / 60
        
        if minutes_elapsed >= 1:  # Only decay if at least 1 minute has passed
            # Apply decay
            pet.hunger = max(0, pet.hunger + int(self.DECAY_RATES["hunger"] * minutes_elapsed))
            pet.happiness = max(0, pet.happiness + int(self.DECAY_RATES["happiness"] * minutes_elapsed))
            pet.energy = max(0, pet.energy + int(self.DECAY_RATES["energy"] * minutes_elapsed))
            
            # Update timestamps
            pet.last_decay = now
            pet.updated_at = now
            
            self.db.commit()
            self.db.refresh(pet)
        
        return pet
    
    def feed_pet(self, pet: Pet) -> Dict[str, Any]:
        """Feed the pet."""
        # Apply decay first
        pet = self.apply_decay(pet)
        
        # Check if pet is sleeping
        if self._is_pet_sleeping(pet):
            return {
                "success": False,
                "message": "Your pet is sleeping and cannot be fed right now."
            }
        
        # Feed the pet
        old_hunger = pet.hunger
        pet.hunger = min(100, pet.hunger + 20)
        
        # Decrease happiness if overfed (hunger > 80)
        if pet.hunger > 80:
            pet.happiness = max(0, pet.happiness - 5)
            message = f"{pet.name} is getting full! Happiness decreased."
        else:
            message = f"{pet.name} enjoyed the meal!"
        
        pet.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pet)
        
        return {
            "success": True,
            "message": message,
            "hunger_change": pet.hunger - old_hunger
        }
    
    def play_with_pet(self, pet: Pet) -> Dict[str, Any]:
        """Play with the pet."""
        # Apply decay first
        pet = self.apply_decay(pet)
        
        # Check if pet is sleeping
        if self._is_pet_sleeping(pet):
            return {
                "success": False,
                "message": "Your pet is sleeping and cannot play right now."
            }
        
        # Check if pet has enough energy
        if pet.energy < 10:
            return {
                "success": False,
                "message": f"{pet.name} is too tired to play. Let them sleep first!"
            }
        
        # Play with the pet
        old_happiness = pet.happiness
        old_energy = pet.energy
        
        pet.happiness = min(100, pet.happiness + 15)
        pet.energy = max(0, pet.energy - 10)
        
        pet.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pet)
        
        return {
            "success": True,
            "message": f"{pet.name} had fun playing!",
            "happiness_change": pet.happiness - old_happiness,
            "energy_change": pet.energy - old_energy
        }
    
    def put_pet_to_sleep(self, pet: Pet) -> Dict[str, Any]:
        """Put the pet to sleep."""
        # Apply decay first
        pet = self.apply_decay(pet)
        
        # Check if already sleeping
        if self._is_pet_sleeping(pet):
            return {
                "success": False,
                "message": f"{pet.name} is already sleeping."
            }
        
        # Put pet to sleep
        old_energy = pet.energy
        pet.energy = min(100, pet.energy + 30)
        
        # Set sleep timestamp (store in updated_at for simplicity)
        pet.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pet)
        
        return {
            "success": True,
            "message": f"{pet.name} is now sleeping peacefully.",
            "energy_change": pet.energy - old_energy,
            "sleep_duration": 300  # 5 minutes in seconds
        }
    
    def _is_pet_sleeping(self, pet: Pet) -> bool:
        """Check if pet is currently sleeping."""
        # Pet sleeps for 5 minutes after sleep action
        sleep_duration = timedelta(seconds=300)  # 5 minutes
        return datetime.utcnow() - pet.updated_at < sleep_duration and pet.energy > 80
    
    def check_evolution(self, pet: Pet) -> Dict[str, Any]:
        """Check if pet should evolve."""
        if pet.stage == PetStage.EVOLVED:
            return {"evolved": False, "message": "Pet is already evolved."}
        
        # Check if all stats have been above 70 for 24 hours
        # For demo purposes, we'll use a shorter time (1 hour)
        evolution_threshold = timedelta(hours=1)
        
        if (pet.hunger >= 70 and pet.happiness >= 70 and pet.energy >= 70 and
            datetime.utcnow() - pet.updated_at >= evolution_threshold):
            
            pet.stage = PetStage.EVOLVED
            pet.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(pet)
            
            return {
                "evolved": True,
                "message": f"🎉 {pet.name} has evolved into a magnificent {pet.species.value}!"
            }
        
        return {"evolved": False, "message": "Pet needs all stats above 70 to evolve."}
    
    def get_pet_status(self, pet: Pet) -> Dict[str, Any]:
        """Get current pet status with all information."""
        # Apply decay first
        pet = self.apply_decay(pet)
        
        is_sleeping = self._is_pet_sleeping(pet)
        
        return {
            "id": pet.id,
            "name": pet.name,
            "species": pet.species.value,
            "stage": pet.stage.value,
            "hunger": pet.hunger,
            "happiness": pet.happiness,
            "energy": pet.energy,
            "is_sleeping": is_sleeping,
            "updated_at": pet.updated_at.isoformat(),
            "sprite_url": self._get_sprite_url(pet)
        }
    
    def _get_sprite_url(self, pet: Pet) -> str:
        """Get the sprite URL for the pet."""
        if pet.stage == PetStage.EVOLVED:
            return f"/static/img/evolved/{pet.species.value}_evolved.png"
        else:
            return f"/static/img/{pet.species.value}.png"
