"""AI Memory endpoints with RBAC protection."""

import structlog
from fastapi import APIRouter, Depends

from src.core.dependencies import RequirePermission
from src.core.security import Permission, TokenData
from src.models.schemas import (
    MemoryQuery,
    MemoryQueryResponse,
    MemoryStore,
    MemoryStoreResponse,
)
from src.services.memory import memory_manager

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/query", response_model=MemoryQueryResponse)
async def query_memory(
    query: MemoryQuery,
    current_user: TokenData = Depends(RequirePermission(Permission.READ_MEMORY)),
) -> MemoryQueryResponse:
    """
    Query AI memory with tenant isolation.

    Requires: READ_MEMORY permission
    """
    # Use tenant_id from token for isolation
    tenant_id = current_user.tenant_id

    # Execute query with security checks
    results = await memory_manager.query(query, tenant_id)

    logger.info(
        "memory_query",
        user_id=current_user.sub,
        tenant_id=tenant_id,
        results_count=len(results),
    )

    return MemoryQueryResponse(
        results=results,
        query=query.query,
        total_results=len(results),
    )


@router.post("/store", response_model=MemoryStoreResponse)
async def store_memory(
    store_request: MemoryStore,
    current_user: TokenData = Depends(RequirePermission(Permission.WRITE_MEMORY)),
) -> MemoryStoreResponse:
    """
    Store content in AI memory with tenant isolation.

    Requires: WRITE_MEMORY permission
    """
    # Use tenant_id from token for isolation
    tenant_id = current_user.tenant_id

    # Store with security checks
    memory_id = await memory_manager.store(store_request, tenant_id)

    logger.info(
        "memory_store",
        user_id=current_user.sub,
        tenant_id=tenant_id,
        memory_id=memory_id,
    )

    return MemoryStoreResponse(
        id=memory_id,
        status="success",
        message="Memory stored successfully",
    )
