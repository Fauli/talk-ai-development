import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import Pet

def test_complete_user_journey(client):
    """Test complete user journey from registration to pet interaction"""
    
    # 1. Register user
    register_response = client.post("/auth/register", json={
        "email": "journey@example.com",
        "password": "journeypassword"
    })
    assert register_response.status_code == status.HTTP_200_OK
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Try to get pet (should not exist)
    get_response = client.get("/pets/", headers=headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    # 3. Create pet
    create_response = client.post("/pets/", json={
        "name": "Journey",
        "species": "dragon"
    }, headers=headers)
    assert create_response.status_code == status.HTTP_200_OK
    pet_data = create_response.json()
    assert pet_data["name"] == "Journey"
    assert pet_data["species"] == "dragon"
    
    # 4. Get pet (should exist now)
    get_response = client.get("/pets/", headers=headers)
    assert get_response.status_code == status.HTTP_200_OK
    
    # 5. Feed pet
    feed_response = client.post("/pets/feed", headers=headers)
    assert feed_response.status_code == status.HTTP_200_OK
    assert feed_response.json()["pet"]["hunger"] > pet_data["hunger"]
    
    # 6. Play with pet
    play_response = client.post("/pets/play", headers=headers)
    assert play_response.status_code == status.HTTP_200_OK
    assert play_response.json()["pet"]["happiness"] > pet_data["happiness"]
    
    # 7. Put pet to sleep
    sleep_response = client.post("/pets/sleep", headers=headers)
    assert sleep_response.status_code == status.HTTP_200_OK
    assert sleep_response.json()["pet"]["is_sleeping"] is True
    
    # 8. Try to feed sleeping pet (should fail)
    feed_sleeping_response = client.post("/pets/feed", headers=headers)
    assert feed_sleeping_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "sleeping" in feed_sleeping_response.json()["detail"].lower()

def test_multi_user_pet_isolation(client):
    """Test that users can only access their own pets"""
    
    # Register two users
    user1_response = client.post("/auth/register", json={
        "email": "user1@example.com",
        "password": "password1"
    })
    user1_token = user1_response.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    
    user2_response = client.post("/auth/register", json={
        "email": "user2@example.com",
        "password": "password2"
    })
    user2_token = user2_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    # Create pets for both users
    client.post("/pets/", json={
        "name": "User1Pet",
        "species": "cat"
    }, headers=user1_headers)
    
    client.post("/pets/", json={
        "name": "User2Pet",
        "species": "otter"
    }, headers=user2_headers)
    
    # Each user should only see their own pet
    user1_pet = client.get("/pets/", headers=user1_headers)
    assert user1_pet.json()["name"] == "User1Pet"
    
    user2_pet = client.get("/pets/", headers=user2_headers)
    assert user2_pet.json()["name"] == "User2Pet"
    
    # Users should not be able to create multiple pets
    duplicate_response = client.post("/pets/", json={
        "name": "SecondPet",
        "species": "dragon"
    }, headers=user1_headers)
    assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST

def test_pet_stat_boundaries(client, auth_headers):
    """Test that pet stats stay within 0-100 boundaries"""
    
    # Create pet
    client.post("/pets/", json={
        "name": "BoundaryTest",
        "species": "axolotl"
    }, headers=auth_headers)
    
    # Feed multiple times to test upper boundary
    for _ in range(10):
        client.post("/pets/feed", headers=auth_headers)
    
    pet_response = client.get("/pets/", headers=auth_headers)
    pet_data = pet_response.json()
    
    # Stats should not exceed 100
    assert pet_data["hunger"] <= 100
    assert pet_data["happiness"] <= 100
    assert pet_data["energy"] <= 100
    
    # Stats should not go below 0 (would need to simulate decay for this)
    assert pet_data["hunger"] >= 0
    assert pet_data["happiness"] >= 0
    assert pet_data["energy"] >= 0

def test_authentication_required_for_all_pet_actions(client):
    """Test that all pet endpoints require authentication"""
    
    endpoints = [
        ("GET", "/pets/"),
        ("POST", "/pets/"),
        ("POST", "/pets/feed"),
        ("POST", "/pets/play"),
        ("POST", "/pets/sleep"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_token_handling(client):
    """Test handling of invalid authentication tokens"""
    
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    
    response = client.get("/pets/", headers=invalid_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.post("/pets/feed", headers=invalid_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_application_health_endpoints(client):
    """Test application health and status endpoints"""
    
    # Test root endpoint (returns HTML)
    root_response = client.get("/")
    assert root_response.status_code == status.HTTP_200_OK
    assert "PixelPet" in root_response.text
    
    # Test health endpoint
    health_response = client.get("/health")
    assert health_response.status_code == status.HTTP_200_OK
    assert health_response.json()["status"] == "healthy"
