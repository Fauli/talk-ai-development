"""Pytest fixtures for PixelPet tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User, Pet
from app.auth import hash_password, create_access_token


# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Get an access token for the test user."""
    return create_access_token(test_user.id)


@pytest.fixture
def authenticated_client(client, test_user_token):
    """Create a test client with authentication cookie."""
    client.cookies.set("access_token", test_user_token)
    return client


@pytest.fixture
def test_pet(db, test_user):
    """Create a test pet for the test user."""
    pet = Pet(
        user_id=test_user.id,
        name="Testy",
        species="cat",
        hunger=50,
        happiness=50,
        energy=50,
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet
