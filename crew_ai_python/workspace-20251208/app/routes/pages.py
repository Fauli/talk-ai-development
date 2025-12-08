"""HTML page routes with cookie-based authentication."""

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta
import jwt
from jwt.exceptions import InvalidTokenError

from ..database import get_db
from ..models import User, Pet
from ..auth_simple import (
    get_user_by_email,
    authenticate_user,
    create_access_token,
    get_password_hash
)
from ..pet_service import VALID_SPECIES
from ..config import settings

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def get_user_from_cookie(request: Request, db: Session) -> Optional[User]:
    """Get user from session cookie if valid."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email:
            return get_user_by_email(db, email)
    except InvalidTokenError:
        pass
    return None


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    """Home page - welcome screen."""
    user = get_user_from_cookie(request, db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user
    })


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    """Login/Register page."""
    user = get_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/game", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        })

    # Create token and set cookie
    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/game", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
    return response


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle registration form submission."""
    existing = get_user_by_email(db, email)
    if existing:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email already registered"
        })

    # Create user
    hashed_password = get_password_hash(password)
    user = User(email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create token and set cookie
    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(url="/game", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
    return response


@router.post("/logout")
def logout():
    """Handle logout."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/game", response_class=HTMLResponse)
def game_page(request: Request, db: Session = Depends(get_db)):
    """Main game page - pet dashboard."""
    user = get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # Get user's pet if exists
    pet = db.query(Pet).filter(Pet.user_id == user.id).first()

    return templates.TemplateResponse("pet.html", {
        "request": request,
        "user": user,
        "pet": pet,
        "species_list": VALID_SPECIES
    })


# Keep /pet as alias for backwards compatibility
@router.get("/pet", response_class=HTMLResponse)
def pet_page(request: Request, db: Session = Depends(get_db)):
    """Alias for /game."""
    return game_page(request, db)
