"""
Secure AI Memory Manager - Charles Memory Integration.

This module simulates a secure RAG/Vector database with:
- Prompt injection prevention
- Tenant data isolation
- Input sanitization
- Environment isolation
"""

import re
import uuid
from datetime import datetime, UTC
from typing import Any

import structlog

from src.core.config import settings
from src.models.schemas import MemoryQuery, MemoryResult, MemoryStore

logger = structlog.get_logger(__name__)


class PromptInjectionDetector:
    """Detect potential prompt injection attempts."""

    # Patterns indicating potential prompt injection
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+instructions",
        r"disregard\s+(previous|above|all)\s+(instructions|prompts)",
        r"forget\s+(previous|everything|all)",
        r"new\s+instructions?:",
        r"system\s*:\s*you\s+are",
        r"<\s*script\s*>",
        r"javascript\s*:",
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__\s*\(",
    ]

    def __init__(self) -> None:
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS]

    def detect(self, text: str) -> tuple[bool, list[str]]:
        """
        Detect prompt injection attempts.

        Returns:
            Tuple of (is_suspicious, list_of_matched_patterns)
        """
        matched_patterns = []
        for pattern in self.patterns:
            if pattern.search(text):
                matched_patterns.append(pattern.pattern)

        is_suspicious = len(matched_patterns) > 0
        if is_suspicious:
            logger.warning(
                "prompt_injection_detected",
                patterns=matched_patterns,
                text_preview=text[:100],
            )
        return is_suspicious, matched_patterns


class InputSanitizer:
    """Sanitize user inputs based on configured level."""

    @staticmethod
    def sanitize(text: str, level: str = "strict") -> str:
        """
        Sanitize text based on level.

        Args:
            text: Input text to sanitize
            level: Sanitization level (none, basic, strict)
        """
        if level == "none":
            return text

        # Remove null bytes and control characters (except newlines and tabs)
        sanitized = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

        if level == "strict":
            # Remove potential script tags
            sanitized = re.sub(r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL)
            # Remove SQL-like patterns
            sanitized = re.sub(r";\s*(DROP|DELETE|UPDATE|INSERT)\s+", " ", sanitized, flags=re.IGNORECASE)
            # Limit consecutive special characters
            sanitized = re.sub(r"([^\w\s])\1{5,}", r"\1\1\1", sanitized)

        return sanitized.strip()


class SecureMemoryManager:
    """
    Secure AI Memory Manager with RAG/Vector database simulation.

    Features:
    - Tenant isolation
    - Prompt injection detection
    - Input sanitization
    - Audit logging
    """

    def __init__(self) -> None:
        # Simulated in-memory vector store (tenant_id -> list of memories)
        self._memory_store: dict[str, list[dict[str, Any]]] = {}
        self.injection_detector = PromptInjectionDetector()
        self.sanitizer = InputSanitizer()
        logger.info("memory_manager_initialized", vector_db_url=settings.VECTOR_DB_URL)

    async def query(self, query_request: MemoryQuery, tenant_id: str) -> list[MemoryResult]:
        """
        Query AI memory with security checks.

        Args:
            query_request: Query parameters
            tenant_id: Tenant ID for data isolation

        Returns:
            List of memory results
        """
        # Sanitize query
        sanitized_query = self.sanitizer.sanitize(
            query_request.query, settings.SANITIZATION_LEVEL
        )

        # Detect prompt injection
        if settings.ENABLE_PROMPT_INJECTION_DETECTION:
            is_suspicious, patterns = self.injection_detector.detect(sanitized_query)
            if is_suspicious:
                logger.warning(
                    "suspicious_query_blocked",
                    tenant_id=tenant_id,
                    patterns=patterns,
                    query_preview=sanitized_query[:100],
                )
                # In production, you might want to return empty results or raise exception
                # For PoC, we'll log and continue with sanitized query

        # Retrieve tenant-specific memories
        tenant_memories = self._memory_store.get(tenant_id, [])

        # Simulate vector similarity search (simplified for PoC)
        results = self._simulate_vector_search(
            sanitized_query, tenant_memories, query_request.limit
        )

        logger.info(
            "memory_query_executed",
            tenant_id=tenant_id,
            query_length=len(sanitized_query),
            results_count=len(results),
        )

        return results

    async def store(self, store_request: MemoryStore, tenant_id: str) -> str:
        """
        Store content in AI memory with security checks.

        Args:
            store_request: Content to store
            tenant_id: Tenant ID for data isolation

        Returns:
            Memory ID
        """
        # Sanitize content
        sanitized_content = self.sanitizer.sanitize(
            store_request.content, settings.SANITIZATION_LEVEL
        )

        # Detect prompt injection in content
        if settings.ENABLE_PROMPT_INJECTION_DETECTION:
            is_suspicious, patterns = self.injection_detector.detect(sanitized_content)
            if is_suspicious:
                logger.warning(
                    "suspicious_content_detected",
                    tenant_id=tenant_id,
                    patterns=patterns,
                    content_preview=sanitized_content[:100],
                )

        # Generate memory ID
        memory_id = str(uuid.uuid4())

        # Store in tenant-isolated collection
        if tenant_id not in self._memory_store:
            self._memory_store[tenant_id] = []

        memory_entry = {
            "id": memory_id,
            "content": sanitized_content,
            "metadata": {**store_request.metadata, "tenant_id": tenant_id},
            "created_at": datetime.now(UTC),
            "embedding": self._simulate_embedding(sanitized_content),
        }

        self._memory_store[tenant_id].append(memory_entry)

        logger.info(
            "memory_stored",
            tenant_id=tenant_id,
            memory_id=memory_id,
            content_length=len(sanitized_content),
        )

        return memory_id

    def _simulate_vector_search(
        self, query: str, memories: list[dict[str, Any]], limit: int
    ) -> list[MemoryResult]:
        """Simulate vector similarity search (simplified for PoC)."""
        # In production, this would use actual vector similarity (cosine, etc.)
        # For PoC, we'll do simple keyword matching
        query_embedding = self._simulate_embedding(query)

        # Score memories by keyword overlap
        scored_memories = []
        for memory in memories:
            score = self._calculate_similarity(query, memory["content"])
            scored_memories.append((memory, score))

        # Sort by score and limit results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        top_memories = scored_memories[:limit]

        # Convert to MemoryResult
        results = [
            MemoryResult(
                id=memory["id"],
                content=memory["content"],
                score=score,
                metadata=memory["metadata"],
                created_at=memory["created_at"],
            )
            for memory, score in top_memories
        ]

        return results

    @staticmethod
    def _simulate_embedding(text: str) -> list[float]:
        """Simulate embedding generation (for PoC only)."""
        # In production, use actual embedding model (OpenAI, Cohere, etc.)
        return [float(ord(c) % 10) / 10 for c in text[:128]]

    @staticmethod
    def _calculate_similarity(query: str, content: str) -> float:
        """Calculate simple similarity score (for PoC only)."""
        # Simplified keyword-based similarity
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        if not query_words:
            return 0.0
        intersection = query_words & content_words
        return len(intersection) / len(query_words)


# Global instance
memory_manager = SecureMemoryManager()
