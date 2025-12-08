"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables
from .routes import auth, pets, ui

# Create FastAPI app
app = FastAPI(
    title="PixelPet",
    description="A virtual pet web application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(pets.router)
app.include_router(ui.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    create_tables()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
