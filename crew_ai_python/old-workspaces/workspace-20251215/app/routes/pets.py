"""JSON API pet interaction endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user_flexible
from ..database import get_db
from ..pet_service import (
    get_pet_by_user_id, create_pet, get_pet_status,
    feed_pet, play_with_pet, put_pet_to_sleep, evolve_pet
)
from ..config import settings


router = APIRouter(prefix="/pets", tags=["pets"])


class PetCreate(BaseModel):
    name: str
    species: str


class PetResponse(BaseModel):
    id: int
    name: str
    species: str
    hunger: int
    happiness: int
    energy: int
    stage: str
    is_sleeping: bool
    sleep_until: Optional[str] = None
    can_evolve: bool
    is_awake: bool
    created_at: str
    updated_at: str


class ActionResponse(BaseModel):
    success: bool
    message: str
    pet: PetResponse


@router.get("/", response_model=PetResponse)
async def get_pet(db: Session = Depends(get_db), current_user = Depends(get_current_user_flexible)):
    """Get current user's pet status."""
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found. Create one first."
        )
    
    pet_data = get_pet_status(db, pet)
    return pet_data


@router.post("/", response_model=PetResponse)
async def create_new_pet(pet_data: PetCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user_flexible)):
    """Create a new pet for the current user."""
    try:
        pet = create_pet(db, current_user.id, pet_data.name, pet_data.species)
        return get_pet_status(db, pet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/feed", response_model=PetResponse)
async def feed_pet_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user_flexible)):
    """Feed the pet."""
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found"
        )
    
    try:
        feed_pet(db, pet.id)
        return get_pet_status(db, pet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/play", response_model=PetResponse)
async def play_with_pet_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user_flexible)):
    """Play with the pet."""
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found"
        )
    
    try:
        play_with_pet(db, pet.id)
        return get_pet_status(db, pet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/sleep", response_model=PetResponse)
async def sleep_pet_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user_flexible)):
    """Put the pet to sleep."""
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found"
        )
    
    try:
        put_pet_to_sleep(db, pet.id)
        return get_pet_status(db, pet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/evolve", response_model=PetResponse)
async def evolve_pet_endpoint(db: Session = Depends(get_db), current_user = Depends(get_current_user_flexible)):
    """Evolve the pet if eligible."""
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pet found"
        )
    
    try:
        return evolve_pet(db, pet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )