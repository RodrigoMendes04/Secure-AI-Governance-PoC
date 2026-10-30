"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "Admin123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient) -> None:
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_invalid_username(client: TestClient) -> None:
    """Test login with non-existent username."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "Admin123!"},
    )
    assert response.status_code == 401
