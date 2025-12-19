"""Tests for API endpoints."""

import pytest


class TestPetAPI:
    """Tests for pet API endpoints."""

    def test_get_pet_unauthenticated(self, client):
        """Test that getting pet without auth fails."""
        response = client.get("/pets/")
        assert response.status_code == 401

    def test_get_pet_no_pet(self, authenticated_client):
        """Test getting pet when user has no pet."""
        response = authenticated_client.get("/pets/")
        assert response.status_code == 200
        assert response.json() is None

    def test_get_pet_with_pet(self, authenticated_client, test_pet):
        """Test getting pet when user has a pet."""
        response = authenticated_client.get("/pets/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Testy"
        assert data["species"] == "cat"

    def test_create_pet(self, authenticated_client):
        """Test creating a new pet."""
        response = authenticated_client.post(
            "/pets/",
            json={"name": "Buddy", "species": "otter"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Buddy"
        assert data["species"] == "otter"
        assert data["hunger"] == 50
        assert data["stage"] == "baby"

    def test_create_pet_invalid_species(self, authenticated_client):
        """Test creating pet with invalid species fails."""
        response = authenticated_client.post(
            "/pets/",
            json={"name": "Buddy", "species": "unicorn"},
        )
        assert response.status_code == 400

    def test_create_pet_duplicate(self, authenticated_client, test_pet):
        """Test creating second pet fails."""
        response = authenticated_client.post(
            "/pets/",
            json={"name": "Another", "species": "dragon"},
        )
        assert response.status_code == 400

    def test_feed_pet(self, authenticated_client, test_pet, db):
        """Test feeding a pet."""
        test_pet.hunger = 50
        db.commit()

        response = authenticated_client.post("/pets/feed")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["pet"]["hunger"] == 70

    def test_feed_pet_no_pet(self, authenticated_client):
        """Test feeding when user has no pet."""
        response = authenticated_client.post("/pets/feed")
        assert response.status_code == 404

    def test_play_with_pet(self, authenticated_client, test_pet, db):
        """Test playing with a pet."""
        test_pet.happiness = 50
        test_pet.energy = 50
        db.commit()

        response = authenticated_client.post("/pets/play")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["pet"]["happiness"] == 65
        assert data["pet"]["energy"] == 40

    def test_sleep_pet(self, authenticated_client, test_pet):
        """Test putting a pet to sleep."""
        response = authenticated_client.post("/pets/sleep")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["pet"]["is_sleeping"] is True

    def test_bearer_token_auth(self, client, test_user_token):
        """Test that Bearer token authentication works."""
        response = client.get(
            "/pets/",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code == 200
