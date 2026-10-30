# Secure AI Governance PoC

Enterprise-grade FastAPI backend demonstrating secure AI integration with comprehensive governance controls.

## Architecture Overview

This PoC showcases:
- **Role-Based Access Control (RBAC)** with FastAPI dependency injection
- **Secure AI Memory Management** with RAG/Vector database simulation
- **Multi-tenant isolation** with strict data sanitization
- **Audit logging** for compliance and security
- **Prompt injection prevention** mechanisms
- **Production-ready structure** with Docker support

## Project Structure

```
Secure-AI-Governance-PoC/
├── src/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core configuration and security
│   ├── services/         # Business logic and AI services
│   └── models/           # Data models and schemas
├── tests/                # Comprehensive test suite
├── docker/               # Docker configurations
├── pyproject.toml        # Project dependencies
└── Dockerfile            # Production container
```

## Features

### 1. Authorization & Governance (Baseline 002)
- RBAC with granular permission control
- JWT-based authentication
- Request/response audit logging
- Pydantic v2 strict validation

### 2. Secure AI Memory (Charles Memory)
- Prompt injection prevention
- Tenant data isolation
- Vector database simulation
- RAG pattern implementation
- Input sanitization pipeline

### 3. Enterprise Patterns
- Dependency injection
- Repository pattern
- Service layer architecture
- Comprehensive error handling
- Health checks and observability

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run locally
uvicorn src.main:app --reload

# Run with Docker
docker build -t secure-ai-governance .
docker run -p 8000:8000 secure-ai-governance

# Run tests
pytest tests/ -v --cov=src
```

## API Endpoints

- `POST /api/v1/auth/login` - Authenticate user
- `GET /api/v1/memory/query` - Query AI memory (RBAC protected)
- `POST /api/v1/memory/store` - Store AI memory (Admin only)
- `GET /api/v1/audit/logs` - Retrieve audit logs (Admin only)
- `GET /health` - Health check endpoint

## Configuration

Environment variables:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
VECTOR_DB_URL=http://localhost:6333
LOG_LEVEL=INFO
ENABLE_AUDIT=true
```

## Security Features

- Input validation with Pydantic v2
- SQL injection prevention
- Prompt injection detection
- Rate limiting
- CORS configuration
- Security headers

## Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Coverage report
pytest --cov=src --cov-report=html
```

## License

MIT
