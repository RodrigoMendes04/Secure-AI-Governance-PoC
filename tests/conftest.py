"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.core.security import create_access_token, Role


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def admin_token() -> str:
    """Generate admin JWT token for testing."""
    return create_access_token(
        data={"sub": "test_admin", "role": Role.ADMIN.value, "tenant_id": "test_tenant"}
    )


@pytest.fixture
def user_token() -> str:
    """Generate user JWT token for testing."""
    return create_access_token(
        data={"sub": "test_user", "role": Role.USER.value, "tenant_id": "test_tenant"}
    )


@pytest.fixture
def readonly_token() -> str:
    """Generate read-only JWT token for testing."""
    return create_access_token(
        data={"sub": "test_readonly", "role": Role.READ_ONLY.value, "tenant_id": "test_tenant"}
    )
