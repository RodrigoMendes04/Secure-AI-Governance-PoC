"""Pydantic v2 schemas for request/response validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.core.security import Role


class UserLogin(BaseModel):
    """User login request."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


class UserResponse(BaseModel):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    role: Role
    tenant_id: str
    created_at: datetime


class MemoryQuery(BaseModel):
    """AI memory query request."""

    query: str = Field(min_length=1, max_length=4000, description="User query to search memory")
    tenant_id: str | None = Field(
        default=None, description="Optional tenant ID (auto-filled from token)"
    )
    limit: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    filters: dict[str, Any] | None = Field(
        default=None, description="Optional metadata filters"
    )

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        """Basic sanitization of query input."""
        # Remove null bytes and control characters
        sanitized = "".join(char for char in v if ord(char) >= 32 or char in "\n\t")
        return sanitized.strip()


class MemoryStore(BaseModel):
    """AI memory storage request."""

    content: str = Field(
        min_length=1, max_length=10000, description="Content to store in memory"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata for the memory"
    )
    tenant_id: str | None = Field(
        default=None, description="Optional tenant ID (auto-filled from token)"
    )

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Sanitize content before storage."""
        sanitized = "".join(char for char in v if ord(char) >= 32 or char in "\n\t")
        return sanitized.strip()


class MemoryResult(BaseModel):
    """AI memory search result."""

    id: str
    content: str
    score: float = Field(ge=0.0, le=1.0, description="Relevance score")
    metadata: dict[str, Any]
    created_at: datetime


class MemoryQueryResponse(BaseModel):
    """AI memory query response."""

    results: list[MemoryResult]
    query: str
    total_results: int


class MemoryStoreResponse(BaseModel):
    """AI memory storage response."""

    id: str
    status: str
    message: str


class AuditLogEntry(BaseModel):
    """Audit log entry schema."""

    request_id: str
    timestamp: datetime
    user_id: str
    tenant_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
