"""Security utilities: JWT, password hashing, RBAC."""

from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any

import structlog
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from src.core.config import settings

logger = structlog.get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Role(str, Enum):
    """User roles for RBAC."""

    ADMIN = "admin"
    USER = "user"
    READ_ONLY = "read_only"


class Permission(str, Enum):
    """Granular permissions."""

    READ_MEMORY = "read:memory"
    WRITE_MEMORY = "write:memory"
    DELETE_MEMORY = "delete:memory"
    READ_AUDIT = "read:audit"
    MANAGE_USERS = "manage:users"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.READ_MEMORY,
        Permission.WRITE_MEMORY,
        Permission.DELETE_MEMORY,
        Permission.READ_AUDIT,
        Permission.MANAGE_USERS,
    },
    Role.USER: {
        Permission.READ_MEMORY,
        Permission.WRITE_MEMORY,
    },
    Role.READ_ONLY: {
        Permission.READ_MEMORY,
    },
}


class TokenData(BaseModel):
    """JWT token payload."""

    sub: str = Field(description="User ID")
    role: Role = Field(description="User role")
    tenant_id: str = Field(description="Tenant ID for multi-tenancy")
    exp: datetime = Field(description="Expiration timestamp")


class Token(BaseModel):
    """Access token response."""

    access_token: str
    token_type: str = "bearer"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug("access_token_created", user_id=data.get("sub"), expires_at=expire.isoformat())
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(
            sub=payload["sub"],
            role=Role(payload["role"]),
            tenant_id=payload["tenant_id"],
            exp=datetime.fromtimestamp(payload["exp"], UTC),
        )
        return token_data
    except JWTError as e:
        logger.warning("token_decode_failed", error=str(e))
        raise ValueError("Invalid token") from e


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())
