# PixelPet Web Application

A Tamagotchi-style virtual pet web application built with FastAPI.

## Features

- User authentication with email/password
- Virtual pet with hunger, happiness, and energy stats
- Time-based stat decay
- Pet actions: Feed, Play, Sleep
- Pet evolution system
- Pixel art UI with responsive design

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --reload
```

3. Visit http://localhost:8000 in your browser

## Testing

Run tests with:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app
```

## Project Structure

- `app/` - Main application code
  - `main.py` - FastAPI application entry point
  - `database.py` - Database configuration
  - `models.py` - SQLAlchemy models
  - `auth.py` - Authentication utilities
  - `pet_service.py` - Pet business logic
  - `scheduler.py` - Background tasks
  - `routes/` - API route handlers
  - `templates/` - Jinja2 HTML templates
  - `static/` - CSS and image assets
- `tests/` - Test suite
- `requirements.txt` - Python dependencies
