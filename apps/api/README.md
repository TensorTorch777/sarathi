# Sarathi AI — API

FastAPI backend skeleton for Sarathi AI (Python 3.12, Poetry, SQLAlchemy, Alembic).

## Layout

```
app/
  core/             Settings, logging, security, middleware, errors, DI
  domain/           Entities, value objects, repository interfaces
  application/      Use cases, ports, DTOs (no business logic yet)
  infrastructure/   SQLAlchemy, Redis, Qdrant, LLM adapters
  api/              HTTP routers, schemas, lifespan
  workers/          Background job entrypoints (stubs)
  extensions/       Future voice / journaling / multilingual / memory
```

## Local development

```bash
# from repository root
cp .env.example .env
make install
make up
make migrate
```

API docs: http://localhost:8000/docs

## Endpoints (skeleton)

- `GET /api/v1/health` — liveness/readiness
- `GET /api/v1/version` — application version
