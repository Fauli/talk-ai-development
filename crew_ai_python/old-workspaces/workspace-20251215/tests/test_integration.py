"""Integration tests for the PixelPet application."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


def test_full_user_journey(client):
    """Test complete user journey from registration to pet interaction."""
    user_data = {"email": "integration@example.com", "password": "testpass123"}
    pet_data = {"name": "IntegrationPet", "species": "dragon"}
    
    # 1. Register user
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create pet
    response = client.post("/pets/", json=pet_data, headers=headers)
    assert response.status_code == 200
    pet_info = response.json()
    assert pet_info["name"] == "IntegrationPet"
    assert pet_info["species"] == "dragon"
    
    # 3. Feed pet
    initial_hunger = pet_info["hunger"]
    response = client.post("/pets/feed", headers=headers)
    assert response.status_code == 200
    updated_pet = response.json()
    assert updated_pet["hunger"] == min(100, initial_hunger + 20)
    
    # 4. Play with pet
    initial_happiness = updated_pet["happiness"]
    initial_energy = updated_pet["energy"]
    response = client.post("/pets/play", headers=headers)
    assert response.status_code == 200
    final_pet = response.json()
    assert final_pet["happiness"] == min(100, initial_happiness + 15)
    assert final_pet["energy"] == max(0, initial_energy - 10)

    # 5. Put pet to sleep
    response = client.post("/pets/sleep", headers=headers)
    assert response.status_code == 200
    sleeping_pet = response.json()
    assert sleeping_pet["is_sleeping"] is True


def test_multiple_users_separate_pets(client):
    """Test that multiple users have separate pets."""
    user1_data = {"email": "user1@example.com", "password": "pass1"}
    user2_data = {"email": "user2@example.com", "password": "pass2"}
    
    pet1_data = {"name": "Pet1", "species": "cat"}
    pet2_data = {"name": "Pet2", "species": "otter"}
    
    # Register both users
    response1 = client.post("/auth/register", json=user1_data)
    response2 = client.post("/auth/register", json=user2_data)
    
    token1 = response1.json()["access_token"]
    token2 = response2.json()["access_token"]
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Create pets for both users
    client.post("/pets/", json=pet1_data, headers=headers1)
    client.post("/pets/", json=pet2_data, headers=headers2)
    
    # Get pets and verify they're separate
    pet1_response = client.get("/pets/", headers=headers1)
    pet2_response = client.get("/pets/", headers=headers2)
    
    pet1 = pet1_response.json()
    pet2 = pet2_response.json()
    
    assert pet1["name"] == "Pet1"
    assert pet1["species"] == "cat"
    assert pet2["name"] == "Pet2"
    assert pet2["species"] == "otter"
    assert pet1["id"] != pet2["id"]


def test_authentication_required_for_pet_actions(client):
    """Test that all pet actions require authentication."""
    # Try pet actions without authentication
    endpoints = [
        ("/pets/", "GET"),
        ("/pets/", "POST"),
        ("/pets/feed", "POST"),
        ("/pets/play", "POST"),
        ("/pets/sleep", "POST")
    ]
    
    for endpoint, method in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]


def test_duplicate_pet_creation(client):
    """Test that users can only have one pet."""
    user_data = {"email": "single@example.com", "password": "testpass"}
    pet_data = {"name": "FirstPet", "species": "axolotl"}
    
    # Register user
    response = client.post("/auth/register", json=user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create first pet
    response = client.post("/pets/", json=pet_data, headers=headers)
    assert response.status_code == 200
    
    # Try to create second pet
    second_pet_data = {"name": "SecondPet", "species": "dragon"}
    response = client.post("/pets/", json=second_pet_data, headers=headers)
    assert response.status_code == 400
    assert "already has a pet" in response.json()["detail"]


def test_invalid_species(client):
    """Test pet creation with invalid species."""
    user_data = {"email": "species@example.com", "password": "testpass"}
    invalid_pet_data = {"name": "BadPet", "species": "unicorn"}  # Invalid species
    
    # Register user
    response = client.post("/auth/register", json=user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create pet with invalid species
    response = client.post("/pets/", json=invalid_pet_data, headers=headers)
    assert response.status_code == 400
    assert "Invalid species" in response.json()["detail"]


def test_pet_actions_while_sleeping(client):
    """Test that pet actions are blocked while sleeping."""
    user_data = {"email": "sleepy@example.com", "password": "testpass"}
    pet_data = {"name": "SleepyPet", "species": "otter"}
    
    # Register user and create pet
    response = client.post("/auth/register", json=user_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    client.post("/pets/", json=pet_data, headers=headers)
    
    # Put pet to sleep
    client.post("/pets/sleep", headers=headers)
    
    # Try to feed sleeping pet
    response = client.post("/pets/feed", headers=headers)
    assert response.status_code == 400
    assert "sleeping" in response.json()["detail"]
    
    # Try to play with sleeping pet
    response = client.post("/pets/play", headers=headers)
    assert response.status_code == 400
    assert "sleeping" in response.json()["detail"]
