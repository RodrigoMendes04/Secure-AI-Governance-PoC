"""Audit log endpoints (admin only)."""

import structlog
from fastapi import APIRouter, Depends

from src.core.dependencies import RequirePermission
from src.core.security import Permission, TokenData

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/logs")
async def get_audit_logs(
    limit: int = 100,
    current_user: TokenData = Depends(RequirePermission(Permission.READ_AUDIT)),
) -> dict[str, str]:
    """
    Retrieve audit logs.

    Requires: READ_AUDIT permission (admin only)
    """
    logger.info(
        "audit_logs_accessed",
        user_id=current_user.sub,
        limit=limit,
    )

    # In production, read from audit log file or database
    return {
        "message": "Audit log retrieval",
        "status": "In production, this would return actual audit logs",
        "user_id": current_user.sub,
    }
