"""JSON API routes for pet interactions."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user_flexible
from app.config import settings
from app.database import get_db
from app.models import User
from app import pet_service

router = APIRouter(prefix="/pets", tags=["pets"])


class CreatePetRequest(BaseModel):
    """Request body for creating a pet."""
    name: str
    species: str


class PetResponse(BaseModel):
    """Response body for pet data."""
    id: int
    name: str
    species: str
    hunger: int
    happiness: int
    energy: int
    stage: str
    is_sleeping: bool
    sleep_until: str | None
    created_at: str | None
    notifications: list[str]


class ActionResponse(BaseModel):
    """Response body for pet actions."""
    success: bool
    message: str
    pet: PetResponse | None = None


@router.get("/", response_model=PetResponse | None)
def get_pet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible),
):
    """Get the current user's pet status."""
    pet = pet_service.get_pet_for_user(db, current_user)
    if not pet:
        return None
    return pet_service.get_pet_status(db, pet)


@router.post("/", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(
    request: CreatePetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible),
):
    """Create a new pet for the current user."""
    if request.species not in settings.VALID_SPECIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid species. Must be one of: {settings.VALID_SPECIES}",
        )

    existing_pet = pet_service.get_pet_for_user(db, current_user)
    if existing_pet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pet",
        )

    pet = pet_service.create_pet(db, current_user, request.name, request.species)
    return pet_service.get_pet_status(db, pet)


@router.post("/feed", response_model=ActionResponse)
def feed_pet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible),
):
    """Feed the user's pet."""
    pet = pet_service.get_pet_for_user(db, current_user)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't have a pet",
        )

    result = pet_service.feed_pet(db, pet)
    return ActionResponse(
        success=result["success"],
        message=result["message"],
        pet=pet_service.get_pet_status(db, pet),
    )


@router.post("/play", response_model=ActionResponse)
def play_with_pet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible),
):
    """Play with the user's pet."""
    pet = pet_service.get_pet_for_user(db, current_user)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't have a pet",
        )

    result = pet_service.play_with_pet(db, pet)
    return ActionResponse(
        success=result["success"],
        message=result["message"],
        pet=pet_service.get_pet_status(db, pet),
    )


@router.post("/sleep", response_model=ActionResponse)
def put_pet_to_sleep(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible),
):
    """Put the user's pet to sleep."""
    pet = pet_service.get_pet_for_user(db, current_user)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't have a pet",
        )

    result = pet_service.put_pet_to_sleep(db, pet)
    return ActionResponse(
        success=result["success"],
        message=result["message"],
        pet=pet_service.get_pet_status(db, pet),
    )
