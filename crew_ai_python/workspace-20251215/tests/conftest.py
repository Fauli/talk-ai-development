"""Pytest configuration and fixtures for PixelPet tests."""
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db, Base
from app.models import User, Pet
from app.routes import auth, pets, pages


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test."""
    # Use in-memory SQLite for tests with StaticPool to share connection
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal

    # Clean up - drop all tables after each test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create a database session for a test."""
    session = test_db()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def app(test_db):
    """Create a test FastAPI app."""
    # Create a simple test app without lifespan events
    test_app = FastAPI(title="PixelPet Test", version="1.0.0")

    # Override database dependency
    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    # Mount static files
    static_dir = Path(__file__).parent.parent / "app" / "static"
    if static_dir.exists():
        test_app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Include routers
    test_app.include_router(pages.router)
    test_app.include_router(auth.router)
    test_app.include_router(pets.router)

    # Add health endpoint (defined in main.py but not in routers)
    @test_app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "PixelPet"}

    return test_app


@pytest.fixture
def client(app):
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def test_pet_data():
    """Test pet data."""
    return {
        "name": "TestPet",
        "species": "cat"
    }