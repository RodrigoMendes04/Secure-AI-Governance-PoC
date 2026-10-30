"""Custom middleware for security and audit logging."""

import time
import uuid
from pathlib import Path
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.config import settings

logger = structlog.get_logger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests for audit purposes."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.audit_log_path = Path(settings.AUDIT_LOG_PATH)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log audit information."""
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Extract user context if available
        user_id = "anonymous"
        tenant_id = "default"
        if hasattr(request.state, "user"):
            user_id = request.state.user.get("sub", "anonymous")
            tenant_id = request.state.user.get("tenant_id", "default")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log audit event
        audit_event = {
            "request_id": request_id,
            "timestamp": time.time(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else "unknown",
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }

        logger.info("audit_log", **audit_event)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response
