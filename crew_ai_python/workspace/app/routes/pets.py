"""Pet interaction API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
from ..database import get_db
from ..auth import get_current_user
from ..models import User, PetSpecies
from ..pet_service import PetService

router = APIRouter(prefix="/api/pet", tags=["pets"])


class PetCreateRequest(BaseModel):
    name: str
    species: PetSpecies


class PetStatusResponse(BaseModel):
    id: int
    name: str
    species: str
    stage: str
    hunger: int
    happiness: int
    energy: int
    is_sleeping: bool
    updated_at: str
    sprite_url: str


class ActionResponse(BaseModel):
    success: bool
    message: str
    pet: PetStatusResponse


@router.get("/", response_model=PetStatusResponse)
async def get_pet_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current pet status."""
    pet_service = PetService(db)
    pet = pet_service.get_user_pet(current_user)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found. Create a pet first."
        )
    
    pet_status = pet_service.get_pet_status(pet)
    return PetStatusResponse(**pet_status)


@router.post("/create", response_model=PetStatusResponse)
async def create_pet(
    name: str = Form(...),
    species: PetSpecies = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new pet for the user."""
    pet_service = PetService(db)
    
    # Check if user already has a pet
    existing_pet = pet_service.get_user_pet(current_user)
    if existing_pet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a pet"
        )
    
    # Validate name
    if not name or len(name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pet name cannot be empty"
        )
    
    if len(name) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pet name cannot be longer than 50 characters"
        )
    
    # Create the pet
    pet = pet_service.create_pet(current_user, name.strip(), species)
    pet_status = pet_service.get_pet_status(pet)
    return PetStatusResponse(**pet_status)


@router.post("/feed", response_model=ActionResponse)
async def feed_pet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Feed the pet."""
    pet_service = PetService(db)
    pet = pet_service.get_user_pet(current_user)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found"
        )
    
    result = pet_service.feed_pet(pet)
    pet_status = pet_service.get_pet_status(pet)
    
    return ActionResponse(
        success=result["success"],
        message=result["message"],
        pet=PetStatusResponse(**pet_status)
    )


@router.post("/play", response_model=ActionResponse)
async def play_with_pet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Play with the pet."""
    pet_service = PetService(db)
    pet = pet_service.get_user_pet(current_user)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found"
        )
    
    result = pet_service.play_with_pet(pet)
    pet_status = pet_service.get_pet_status(pet)
    
    return ActionResponse(
        success=result["success"],
        message=result["message"],
        pet=PetStatusResponse(**pet_status)
    )


@router.post("/sleep", response_model=ActionResponse)
async def put_pet_to_sleep(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Put the pet to sleep."""
    pet_service = PetService(db)
    pet = pet_service.get_user_pet(current_user)
    
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found"
        )
    
    result = pet_service.put_pet_to_sleep(pet)
    pet_status = pet_service.get_pet_status(pet)
    
    return ActionResponse(
        success=result["success"],
        message=result["message"],
        pet=PetStatusResponse(**pet_status)
    )
