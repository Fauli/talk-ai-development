import pytest
from fastapi import status
from app.models import Pet

def test_create_pet_endpoint(client, auth_headers):
    response = client.post("/pets/", json={
        "name": "Buddy",
        "species": "otter"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Buddy"
    assert data["species"] == "otter"
    assert data["hunger"] == 50
    assert data["happiness"] == 50
    assert data["energy"] == 50
    assert data["stage"] == "normal"
    assert data["is_sleeping"] is False

def test_create_pet_invalid_species(client, auth_headers):
    response = client.post("/pets/", json={
        "name": "Invalid",
        "species": "unicorn"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid species" in response.json()["detail"]

def test_create_pet_duplicate(client, auth_headers):
    # Create first pet
    client.post("/pets/", json={
        "name": "First",
        "species": "cat"
    }, headers=auth_headers)
    
    # Try to create second pet
    response = client.post("/pets/", json={
        "name": "Second",
        "species": "dog"
    }, headers=auth_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already has a pet" in response.json()["detail"]

def test_create_pet_unauthorized(client):
    response = client.post("/pets/", json={
        "name": "Unauthorized",
        "species": "cat"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_pet_endpoint(client, auth_headers):
    # Create pet first
    client.post("/pets/", json={
        "name": "GetTest",
        "species": "dragon"
    }, headers=auth_headers)
    
    # Get pet
    response = client.get("/pets/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "GetTest"
    assert data["species"] == "dragon"

def test_get_pet_not_found(client, auth_headers):
    response = client.get("/pets/", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Pet not found" in response.json()["detail"]

def test_get_pet_unauthorized(client):
    response = client.get("/pets/")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_feed_pet_endpoint(client, auth_headers):
    # Create pet first
    client.post("/pets/", json={
        "name": "FeedTest",
        "species": "axolotl"
    }, headers=auth_headers)
    
    # Feed pet
    response = client.post("/pets/feed", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "fed" in data["message"].lower()
    assert data["pet"]["hunger"] == 70  # 50 + 20

def test_feed_pet_not_found(client, auth_headers):
    response = client.post("/pets/feed", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Pet not found" in response.json()["detail"]

def test_play_with_pet_endpoint(client, auth_headers):
    # Create pet first
    client.post("/pets/", json={
        "name": "PlayTest",
        "species": "cat"
    }, headers=auth_headers)
    
    # Play with pet
    response = client.post("/pets/play", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "played" in data["message"].lower()
    assert data["pet"]["happiness"] == 65  # 50 + 15
    assert data["pet"]["energy"] == 40  # 50 - 10

def test_play_with_pet_not_found(client, auth_headers):
    response = client.post("/pets/play", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Pet not found" in response.json()["detail"]

def test_put_pet_to_sleep_endpoint(client, auth_headers):
    # Create pet first
    client.post("/pets/", json={
        "name": "SleepTest",
        "species": "otter"
    }, headers=auth_headers)
    
    # Put pet to sleep
    response = client.post("/pets/sleep", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sleeping" in data["message"].lower()
    assert data["pet"]["is_sleeping"] is True
    assert data["pet"]["sleep_until"] is not None

def test_put_pet_to_sleep_not_found(client, auth_headers):
    response = client.post("/pets/sleep", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Pet not found" in response.json()["detail"]

def test_pet_actions_unauthorized(client):
    # Test all pet actions without authentication
    actions = ["/pets/feed", "/pets/play", "/pets/sleep"]
    
    for action in actions:
        response = client.post(action)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    # Root now returns HTML
    assert "PixelPet" in response.text

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"
