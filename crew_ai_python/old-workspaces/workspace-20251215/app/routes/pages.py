"""HTML page routes with cookie-based authentication."""
from pathlib import Path

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..auth import authenticate_user, create_user, create_access_token, get_current_user_flexible
from ..database import get_db
from ..pet_service import get_pet_by_user_id, get_pet_status
from ..config import settings


router = APIRouter()
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page - welcome or redirect to game."""
    try:
        # Try to get current user
        user = get_current_user_flexible(request, db)
        # If user is authenticated, redirect to game
        return RedirectResponse(url="/game", status_code=303)
    except HTTPException:
        # User not authenticated, show welcome page
        return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login/register page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Handle login form submission."""
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        })
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Redirect to game with cookie
    response = RedirectResponse(url="/game", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax"
    )
    return response


@router.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Handle registration form submission."""
    try:
        user = create_user(db, email, password)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Redirect to game with cookie
        response = RedirectResponse(url="/game", status_code=303)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=settings.access_token_expire_minutes * 60,
            samesite="lax"
        )
        return response
        
    except HTTPException as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": e.detail
        })


@router.get("/game", response_class=HTMLResponse)
async def game_page(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user_flexible)):
    """Main game page."""
    pet = get_pet_by_user_id(db, user.id)
    pet_data = None
    
    if pet:
        pet_data = get_pet_status(db, pet)
    
    return templates.TemplateResponse("pet.html", {
        "request": request,
        "user": user,
        "pet": pet_data,
        "valid_species": settings.valid_species
    })


@router.get("/logout")
async def logout():
    """Logout and redirect to home."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response