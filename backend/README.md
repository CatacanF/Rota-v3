# Rota-v1 Clean Architecture Backend

This directory contains the production-grade backend for Rota-v1.

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose

### Running the Stack

```bash
cd ..
docker-compose up --build
```

This will start:
- **API**: http://localhost:8000
- **TimescaleDB**: Port 5432
- **Redis**: Port 6379
- **Celery Worker**: Background processing

### Architecture

- **FastAPI**: Async API framework
- **SQLAlchemy + AsyncPG**: Async database ORM
- **TimescaleDB**: Time-series database
- **Celery + Redis**: Background workers
- **Redis Pub/Sub**: Real-time WebSockets

### Directory Structure

- `/app/api`: API endpoints (Routers)
- `/app/core`: Configuration & Security
- `/app/db`: Database session & base
- `/app/models`: Database models
- `/app/schemas`: Pydantic models
- `/app/services`: External API integration
- `/app/worker`: Celery tasks
