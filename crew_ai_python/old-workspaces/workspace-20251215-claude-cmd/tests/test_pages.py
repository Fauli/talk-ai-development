"""Tests for HTML page routes."""

import pytest


class TestHomeRoute:
    """Tests for the home page."""

    def test_home_page_renders(self, client):
        """Test that home page renders HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "PixelPet" in response.text
        assert "text/html" in response.headers["content-type"]

    def test_home_page_shows_login_link(self, client):
        """Test that home page shows login link for unauthenticated users."""
        response = client.get("/")
        assert "Login" in response.text or "Get Started" in response.text

    def test_home_page_redirects_with_pet(self, authenticated_client, test_pet):
        """Test that authenticated user with pet is redirected to game."""
        response = authenticated_client.get("/", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/game"


class TestLoginRoute:
    """Tests for the login page."""

    def test_login_page_renders(self, client):
        """Test that login page renders."""
        response = client.get("/login")
        assert response.status_code == 200
        assert "Login" in response.text

    def test_login_form_success(self, client, test_user):
        """Test successful form login."""
        response = client.post(
            "/login",
            data={"email": "test@example.com", "password": "testpassword"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/game"
        assert "access_token" in response.cookies

    def test_login_form_failure(self, client, test_user):
        """Test failed form login shows error."""
        response = client.post(
            "/login",
            data={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "Invalid" in response.text


class TestRegisterRoute:
    """Tests for the register route."""

    def test_register_form_success(self, client):
        """Test successful form registration."""
        response = client.post(
            "/register",
            data={"email": "newuser@example.com", "password": "newpassword"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/game"
        assert "access_token" in response.cookies

    def test_register_form_duplicate(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/register",
            data={"email": "test@example.com", "password": "password"},
        )
        assert response.status_code == 400
        assert "already registered" in response.text


class TestGameRoute:
    """Tests for the game page."""

    def test_game_page_requires_auth(self, client):
        """Test that game page redirects unauthenticated users."""
        response = client.get("/game", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"

    def test_game_page_renders(self, authenticated_client):
        """Test that authenticated user can access game page."""
        response = authenticated_client.get("/game")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_game_page_shows_pet_creation(self, authenticated_client):
        """Test that game page shows pet creation form when no pet."""
        response = authenticated_client.get("/game")
        assert "Adopt Your Pet" in response.text

    def test_game_page_shows_pet(self, authenticated_client, test_pet):
        """Test that game page shows pet when user has one."""
        response = authenticated_client.get("/game")
        assert "Testy" in response.text
        assert "Feed" in response.text
        assert "Play" in response.text
        assert "Sleep" in response.text


class TestLogoutRoute:
    """Tests for the logout route."""

    def test_logout_clears_cookie(self, authenticated_client):
        """Test that logout clears the auth cookie."""
        response = authenticated_client.get("/logout", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"
        # Cookie should be deleted (set to empty or with expiry in past)
        assert "access_token" in response.headers.get("set-cookie", "")
