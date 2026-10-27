"""
Authentication and System Health Tests for InsureVisionAI.
"""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Verify system health endpoint returns expected payload and status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["application"] == "InsureVisionAI"
    assert data["storage"] == "CSV"
    assert data["version"] == "1.0.0"


def test_demo_login_success(client: TestClient):
    """Verify demo user can authenticate using specified demo credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nuzair@email.com", "password": "123456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient):
    """Verify authentication fails for incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nuzair@email.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Verify authentication fails for non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unknown.user@email.com", "password": "password"}
    )
    assert response.status_code == 401


def test_signup_success(client: TestClient):
    """Verify successful registration of a new user."""
    payload = {
        "name": "Ananya Roy",
        "email": "ananya.roy@email.com",
        "password": "securepassword99",
        "phone": "+91 98111 22233",
        "vehicle_type": "Sedan",
        "vehicle_number": "KA-03-AB-1234"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "ananya.roy@email.com"
    assert data["name"] == "Ananya Roy"
    assert "password_hash" not in data  # Never expose password hash!
    assert "id" in data


def test_signup_duplicate_email_rejection(client: TestClient):
    """Verify duplicate signup attempts with existing email are rejected."""
    payload = {
        "name": "Duplicate Tester",
        "email": "nuzair@email.com",  # Demo email already registered
        "password": "anyPassword123"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_current_user_profile(client: TestClient, demo_auth_headers: dict):
    """Verify authenticated user can retrieve their profile."""
    response = client.get("/api/v1/auth/me", headers=demo_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "nuzair@email.com"
    assert "password_hash" not in data


def test_unauthorized_access_rejected(client: TestClient):
    """Verify protected endpoints reject requests lacking valid bearer token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


def test_invalid_bearer_token(client: TestClient):
    """Verify forged/invalid bearer token returns 401."""
    headers = {"Authorization": "Bearer invalid.forged.jwt.token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

