from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from .database import init_db
from .routes import auth, pets, pages
from .scheduler import scheduler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting PixelPet application")
    init_db()
    await scheduler.start()
    yield
    # Shutdown
    logger.info("Shutting down PixelPet application")
    await scheduler.stop()

app = FastAPI(
    title="PixelPet",
    description="A virtual pet care application",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers - pages first for HTML routes
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(pets.router)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except RuntimeError:
    # Directory doesn't exist yet, that's okay
    pass

@app.get("/health")
def health_check():
    return {"status": "healthy"}