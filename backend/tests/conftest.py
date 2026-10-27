"""
Pytest configuration and fixtures for InsureVisionAI backend tests.
Provides isolated temporary CSV storage so tests never modify real demo data.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from main import app
from services.csv_storage import CSVStorage, csv_storage


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Create an isolated test directory for CSV files during testing."""
    test_dir = tempfile.mkdtemp(prefix="insure_vision_ai_test_data_")
    test_path = Path(test_dir)
    
    # Repoint csv_storage singleton to test directory
    original_data_dir = csv_storage.data_dir
    csv_storage.data_dir = test_path
    csv_storage.initialize_storage()

    yield

    # Clean up test files and restore
    csv_storage.data_dir = original_data_dir
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Test client instance."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def demo_auth_headers(client: TestClient) -> dict:
    """Login with the pre-seeded demo user and return Authorization Bearer headers."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nuzair@email.com", "password": "123456"}
    )
    assert resp.status_code == 200, f"Demo login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def secondary_auth_headers(client: TestClient) -> dict:
    """Create a second distinct user and return their Authorization Bearer headers."""
    email = "secondary.driver@email.com"
    signup_resp = client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Secondary Driver",
            "email": email,
            "password": "password123",
            "phone": "+91 99999 88888",
            "vehicle_type": "Two-Wheeler",
            "vehicle_number": "KA-05-XY-9000"
        }
    )
    # If already created in a previous test, login directly
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"}
    )
    assert login_resp.status_code == 200, f"Secondary login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

