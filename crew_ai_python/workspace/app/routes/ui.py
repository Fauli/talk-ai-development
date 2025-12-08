"""Web UI routes for serving HTML templates."""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user_optional
from ..models import User, PetSpecies
from ..pet_service import PetService

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Landing page - redirect to pet if authenticated, otherwise show login."""
    if current_user:
        return RedirectResponse(url="/pet", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Login page."""
    if current_user:
        return RedirectResponse(url="/pet", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Registration page."""
    if current_user:
        return RedirectResponse(url="/pet", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/pet", response_class=HTMLResponse)
async def pet_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Main pet interaction page."""
    if not current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    pet_service = PetService(db)
    pet = pet_service.get_user_pet(current_user)
    
    if not pet:
        # User needs to create a pet
        return templates.TemplateResponse("create_pet.html", {
            "request": request,
            "user": current_user,
            "species_options": [species.value for species in PetSpecies]
        })
    
    # Get pet status
    pet_status = pet_service.get_pet_status(pet)
    
    return templates.TemplateResponse("pet.html", {
        "request": request,
        "user": current_user,
        "pet": pet_status
    })
