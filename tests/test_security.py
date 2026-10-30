"""Tests for security utilities."""

import pytest
from datetime import datetime, UTC

from src.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
    has_permission,
    Role,
    Permission,
)


def test_password_hashing() -> None:
    """Test password hashing and verification."""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_token_creation_and_decode() -> None:
    """Test JWT token creation and decoding."""
    token_data = {
        "sub": "test_user",
        "role": Role.USER.value,
        "tenant_id": "test_tenant",
    }
    token = create_access_token(token_data)
    decoded = decode_access_token(token)

    assert decoded.sub == "test_user"
    assert decoded.role == Role.USER
    assert decoded.tenant_id == "test_tenant"
    assert isinstance(decoded.exp, datetime)


def test_invalid_token() -> None:
    """Test decoding invalid token."""
    with pytest.raises(ValueError):
        decode_access_token("invalid.token.here")


def test_role_permissions() -> None:
    """Test role permission mapping."""
    assert has_permission(Role.ADMIN, Permission.READ_MEMORY)
    assert has_permission(Role.ADMIN, Permission.WRITE_MEMORY)
    assert has_permission(Role.ADMIN, Permission.READ_AUDIT)

    assert has_permission(Role.USER, Permission.READ_MEMORY)
    assert has_permission(Role.USER, Permission.WRITE_MEMORY)
    assert not has_permission(Role.USER, Permission.READ_AUDIT)

    assert has_permission(Role.READ_ONLY, Permission.READ_MEMORY)
    assert not has_permission(Role.READ_ONLY, Permission.WRITE_MEMORY)
