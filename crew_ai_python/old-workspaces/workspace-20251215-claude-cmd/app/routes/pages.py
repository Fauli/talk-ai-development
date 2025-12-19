"""HTML page routes using Jinja2 templates."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_optional,
    get_current_user_flexible,
)
from app.database import get_db
from app.models import User
from app import pet_service

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    db: Session = Depends(get_db),
):
    """Home page - shows welcome or redirects to game if logged in."""
    user = get_current_user_optional(request, db)
    if user:
        pet = pet_service.get_pet_for_user(db, user)
        if pet:
            return RedirectResponse(url="/game", status_code=303)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Login/register page."""
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle login form submission."""
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=401,
        )

    token = create_access_token(user.id)
    response = RedirectResponse(url="/game", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.post("/register", response_class=HTMLResponse)
def register_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle registration form submission."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Email already registered"},
            status_code=400,
        )

    # Create new user
    user = User(
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    response = RedirectResponse(url="/game", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/game", response_class=HTMLResponse)
def game_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """Game page - requires authentication."""
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    pet = pet_service.get_pet_for_user(db, user)
    pet_status = pet_service.get_pet_status(db, pet) if pet else None

    return templates.TemplateResponse(
        "pet.html",
        {
            "request": request,
            "user": user,
            "pet": pet_status,
            "valid_species": ["otter", "cat", "dragon", "axolotl"],
        },
    )


@router.get("/logout")
def logout():
    """Log out by clearing the cookie."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response
