"""Authentication endpoints."""

from datetime import timedelta

import structlog
from fastapi import APIRouter, HTTPException, status

from src.core.config import settings
from src.core.security import (
    Role,
    Token,
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.models.schemas import UserLogin

router = APIRouter()
logger = structlog.get_logger(__name__)

# Mock user database (in production, use real database)
MOCK_USERS = {
    "admin": {
        "user_id": "user_001",
        "username": "admin",
        "password_hash": get_password_hash("Admin123!"),
        "role": Role.ADMIN,
        "tenant_id": "tenant_001",
    },
    "user": {
        "user_id": "user_002",
        "username": "user",
        "password_hash": get_password_hash("User123!"),
        "role": Role.USER,
        "tenant_id": "tenant_001",
    },
    "readonly": {
        "user_id": "user_003",
        "username": "readonly",
        "password_hash": get_password_hash("Read123!"),
        "role": Role.READ_ONLY,
        "tenant_id": "tenant_002",
    },
}


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin) -> Token:
    """
    Authenticate user and return JWT token.

    Test credentials:
    - admin / Admin123! (full access)
    - user / User123! (read/write memory)
    - readonly / Read123! (read-only)
    """
    # Retrieve user
    user = MOCK_USERS.get(user_login.username)
    if not user or not verify_password(user_login.password, user["password_hash"]):
        logger.warning("login_failed", username=user_login.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["user_id"],
            "role": user["role"].value,
            "tenant_id": user["tenant_id"],
        },
        expires_delta=access_token_expires,
    )

    logger.info(
        "login_successful",
        user_id=user["user_id"],
        username=user_login.username,
        role=user["role"].value,
    )

    return Token(access_token=access_token)
