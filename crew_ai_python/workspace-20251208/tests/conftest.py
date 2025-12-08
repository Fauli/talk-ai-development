import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, Pet
from app.auth_simple import get_password_hash
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_db):
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_pet(test_db, test_user):
    pet = Pet(
        user_id=test_user.id,
        name="TestPet",
        species="cat",
        hunger=50,
        happiness=50,
        energy=50
    )
    test_db.add(pet)
    test_db.commit()
    test_db.refresh(pet)
    return pet

@pytest.fixture
def auth_headers(client):
    # Register and login a user
    response = client.post("/auth/register", json={
        "email": "auth@example.com",
        "password": "authpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
