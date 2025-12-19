"""Tests for authentication functionality."""

import pytest

from app.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.models import User


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a salted hash."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        # Hash should contain salt and hash separated by colon
        assert ":" in hashed
        salt, hash_value = hashed.split(":")
        assert len(salt) == 32  # 16 bytes hex = 32 chars
        assert len(hash_value) == 64  # SHA256 hex = 64 chars

    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (different salts)."""
        password = "mysecretpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that correct password verifies successfully."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_invalid_hash(self):
        """Test that invalid hash format returns False."""
        assert verify_password("password", "invalidhash") is False
        assert verify_password("password", "") is False


class TestJWT:
    """Tests for JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test that access token is created successfully."""
        user_id = 123
        token = create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test that token decodes to correct user_id."""
        user_id = 456
        token = create_access_token(user_id)

        decoded_id = decode_access_token(token)
        assert decoded_id == user_id

    def test_decode_invalid_token(self):
        """Test that invalid token returns None."""
        assert decode_access_token("invalid.token.here") is None

    def test_decode_empty_token(self):
        """Test that empty token returns None."""
        assert decode_access_token("") is None


class TestAuthAPI:
    """Tests for authentication API endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={"email": "new@example.com", "password": "newpassword"},
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "password"},
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent email fails."""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "password"},
        )

        assert response.status_code == 401
