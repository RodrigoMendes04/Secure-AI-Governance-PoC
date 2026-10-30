"""FastAPI dependency injection for authentication and authorization."""

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.security import TokenData, decode_access_token, has_permission, Permission

logger = structlog.get_logger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Validate JWT token and return user data.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        token = credentials.credentials
        token_data = decode_access_token(token)
        logger.debug("user_authenticated", user_id=token_data.sub, role=token_data.role.value)
        return token_data
    except ValueError as e:
        logger.warning("authentication_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


class RequirePermission:
    """Dependency class to enforce permission-based access control."""

    def __init__(self, permission: Permission) -> None:
        self.permission = permission

    async def __call__(self, current_user: TokenData = Depends(get_current_user)) -> TokenData:
        """
        Check if user has required permission.

        Raises:
            HTTPException: If user lacks the required permission.
        """
        if not has_permission(current_user.role, self.permission):
            logger.warning(
                "permission_denied",
                user_id=current_user.sub,
                role=current_user.role.value,
                required_permission=self.permission.value,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {self.permission.value}",
            )

        logger.debug(
            "permission_granted",
            user_id=current_user.sub,
            permission=self.permission.value,
        )
        return current_user


class RequireRole:
    """Dependency class to enforce role-based access control."""

    def __init__(self, *allowed_roles: str) -> None:
        self.allowed_roles = set(allowed_roles)

    async def __call__(self, current_user: TokenData = Depends(get_current_user)) -> TokenData:
        """
        Check if user has an allowed role.

        Raises:
            HTTPException: If user's role is not in allowed roles.
        """
        if current_user.role.value not in self.allowed_roles:
            logger.warning(
                "role_denied",
                user_id=current_user.sub,
                user_role=current_user.role.value,
                allowed_roles=list(self.allowed_roles),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}",
            )

        logger.debug("role_verified", user_id=current_user.sub, role=current_user.role.value)
        return current_user
