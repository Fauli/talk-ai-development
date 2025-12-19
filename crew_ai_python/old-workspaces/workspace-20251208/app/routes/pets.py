from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models import User, Pet
from ..auth_simple import get_current_user_flexible
from ..pet_service import (
    create_pet,
    get_pet_by_user_id,
    feed_pet,
    play_with_pet,
    put_pet_to_sleep,
    process_pet_updates,
    VALID_SPECIES
)

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
    sleep_until: Optional[datetime]
    evolution_eligible_since: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ActionResponse(BaseModel):
    message: str
    pet: PetResponse

@router.post("/", response_model=PetResponse)
def create_user_pet(
    pet_data: PetCreate,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    # Check if user already has a pet
    existing_pet = get_pet_by_user_id(db, current_user.id)
    if existing_pet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a pet"
        )
    
    if pet_data.species not in VALID_SPECIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid species. Must be one of: {VALID_SPECIES}"
        )
    
    try:
        pet = create_pet(db, current_user.id, pet_data.name, pet_data.species)
        return pet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=PetResponse)
def get_user_pet(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    # Process updates before returning
    pet = process_pet_updates(db, pet)
    return pet

@router.post("/feed", response_model=ActionResponse)
def feed_user_pet(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    try:
        # Process updates first
        pet = process_pet_updates(db, pet)
        pet = feed_pet(db, pet)
        return {
            "message": "Pet has been fed!",
            "pet": pet
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/play", response_model=ActionResponse)
def play_with_user_pet(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    try:
        # Process updates first
        pet = process_pet_updates(db, pet)
        pet = play_with_pet(db, pet)
        return {
            "message": "You played with your pet!",
            "pet": pet
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/sleep", response_model=ActionResponse)
def put_user_pet_to_sleep(
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    pet = get_pet_by_user_id(db, current_user.id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found"
        )
    
    try:
        # Process updates first
        pet = process_pet_updates(db, pet)
        pet = put_pet_to_sleep(db, pet)
        return {
            "message": "Pet is now sleeping!",
            "pet": pet
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
