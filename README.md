# 🚀 FastAPI + PostgreSQL Reference Service

[![CI Pipeline](https://github.com/abhishekbhartiind/fastapi-postgres-api/actions/workflows/ci.yml/badge.svg)](https://github.com/abhishekbhartiind/fastapi-postgres-api/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

A layered backend service with JWT auth and a task API, built with **FastAPI**, **PostgreSQL**,
**SQLAlchemy 2.0 (async)**, **Alembic** and **Docker**. It follows **Clean / Layered Architecture**
and **SOLID** principles and is meant as a clear, tested reference for how I structure a Python backend.

**Scope, stated honestly:** this is a single service with two domains (users, tasks), not a fleet of
microservices. The point is the structure, the database work, and the engineering hygiene around it.

**Highlights**
- Four-layer separation: routers → services → repositories → models
- Async SQLAlchemy 2.0 with a generic `BaseRepository[ModelType]`
- JWT auth with bcrypt password hashing
- Composite and B-Tree indexes, with `EXPLAIN (ANALYZE, BUFFERS)` write-up in [`docs/SQL_AND_QUERY_PLANS.md`](docs/SQL_AND_QUERY_PLANS.md)
- N+1 avoided via eager loading (`joinedload`)
- Alembic migrations, Docker Compose, GitHub Actions CI with a Postgres 16 service container

---

## 🏛️ Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                     HTTP Client                          │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│  Presentation Layer (app/api/v1/)                        │
│  - FastAPI routers, HTTP serialization, status codes     │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│  Service Layer (app/services/)                           │
│  - Business logic, password hashing, JWT issuance        │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│  Repository Layer (app/repositories/)                    │
│  - Async SQLAlchemy 2.0 queries, joins, index filters    │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│  Persistence & Domain Models (app/models/, app/db/)      │
│  - PostgreSQL tables, relationships, indexes             │
└──────────────────────────────────────────────────────────┘
```

### How it maps to SOLID

| Principle | How it shows up here |
|---|---|
| **S**ingle Responsibility | Repositories query data, services hold business logic, routers handle HTTP |
| **O**pen/Closed | Generic `BaseRepository[ModelType]` extends data access without touching core query mechanics |
| **L**iskov Substitution | `UserRepository` and `TaskRepository` substitute cleanly for `BaseRepository` |
| **I**nterface Segregation | Narrow Pydantic schemas (`UserCreate`, `UserLogin`, `UserResponse`) keep payloads clean |
| **D**ependency Inversion | Routers receive dependencies through FastAPI `Depends()`, so tests swap the database easily |

---

## 🧭 Design decisions and trade-offs

| Decision | Why | Trade-off |
|---|---|---|
| Repository pattern | Isolates SQL from business logic, easy to mock | Extra indirection for simple CRUD; earns its keep as queries grow |
| Async SQLAlchemy 2.0 | Non-blocking I/O under concurrent requests | Async sessions need care (lazy loading fails, so eager-load explicitly) |
| `joinedload` for task → owner | One query instead of N+1 for a many-to-one | For one-to-many, `selectinload` is the better choice |
| Composite index `(owner_id, status)` | Serves "my tasks filtered by status" directly | Column order matters, and every index slows writes slightly |
| Stateless JWT | No session store, simple horizontal scaling | No server-side revocation until refresh tokens or a denylist exist |
| Alembic migrations (not `create_all`) | Versioned, reviewable, reversible schema changes | More ceremony than auto-creating tables |
| In-memory SQLite for tests | Zero infrastructure, fast feedback | Dialect drift from PostgreSQL (see roadmap) |

---

## 📁 Repository structure

```text
fastapi-postgres-api/
├── .github/workflows/ci.yml     # CI: Ruff lint + pytest, Postgres 16 service container
├── .dockerignore
├── .env.example                 # Environment variable template
├── .gitignore
├── Dockerfile                   # Multi-stage production image
├── docker-compose.yml           # API + PostgreSQL orchestration
├── pyproject.toml               # Project metadata
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py                   # Async Alembic environment
│   └── versions/
│       └── 001_initial_schema.py
├── app/
│   ├── main.py                  # App factory, CORS, lifespan, error handlers
│   ├── core/
│   │   ├── config.py            # Pydantic Settings
│   │   ├── security.py          # bcrypt hashing, PyJWT tokens
│   │   └── exceptions.py        # Domain exceptions and handlers
│   ├── db/
│   │   ├── base.py              # DeclarativeBase, TimestampMixin
│   │   └── session.py           # Async engine and session generator
│   ├── models/
│   │   ├── user.py              # User model, B-Tree indexes
│   │   └── task.py              # Task model, FK and composite index
│   ├── schemas/                 # Pydantic v2 request/response models
│   │   ├── token.py
│   │   ├── user.py
│   │   └── task.py
│   ├── repositories/            # Data access layer
│   │   ├── base.py              # Generic async BaseRepository
│   │   ├── user_repository.py
│   │   └── task_repository.py   # Joins and index-backed filters
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py
│   │   └── task_service.py
│   └── api/
│       ├── deps.py              # Dependency injection, JWT verification
│       └── v1/
│           ├── auth.py          # /register, /login, /me
│           ├── tasks.py         # Task CRUD
│           └── router.py
├── docs/
│   └── SQL_AND_QUERY_PLANS.md   # Joins, indexes, EXPLAIN ANALYZE walkthrough
└── tests/
    ├── conftest.py              # AsyncClient fixture, in-memory test DB
    ├── test_auth.py
    └── test_tasks.py
```

---

## ⚡ Quick start (Docker)

```bash
git clone https://github.com/abhishekbhartiind/fastapi-postgres-api.git
cd fastapi-postgres-api

# Start PostgreSQL and the API in the background
docker-compose up --build -d

# Follow API logs
docker-compose logs -f api
```

| Service | URL |
|---|---|
| API root | http://localhost:8000/ |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health check | http://localhost:8000/api/v1/health |

Stop and remove containers and volumes:

```bash
docker-compose down -v
```

---

## 💻 Local development

```bash
git clone https://github.com/abhishekbhartiind/fastapi-postgres-api.git
cd fastapi-postgres-api

# Option A: uv (recommended)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Option B: standard venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

> **Before deploying anywhere:** set a strong, unique `SECRET_KEY` in `.env`. Never commit `.env`.

For a quick run without PostgreSQL, set `DATABASE_URL=sqlite+aiosqlite:///./test.db` in `.env`.

Run migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🐘 PostgreSQL: joins, indexes, migrations

1. **Foreign key with cascade.** `tasks.owner_id` references `users.id` with `ondelete="CASCADE"`, so deleting a user removes their tasks atomically.
2. **B-Tree indexes.**
   - `ix_users_email` (unique): O(log N) lookup at login
   - `ix_tasks_owner_id`: fast task ↔ user joins
3. **Composite index.** `idx_tasks_owner_status (owner_id, status)` accelerates
   `SELECT * FROM tasks WHERE owner_id = ? AND status = 'pending'`.
4. **Eager loading.** `TaskRepository.get_task_with_owner()` uses `joinedload(Task.owner)` to avoid the N+1 problem.
5. **Migrations.** Schema changes are versioned with Alembic: `alembic upgrade head`.

For B-Tree internals, `EXPLAIN (ANALYZE, BUFFERS)` output and join mechanics, read
**[docs/SQL_AND_QUERY_PLANS.md](docs/SQL_AND_QUERY_PLANS.md)**.

---

## 🧪 Tests

The suite runs against an isolated in-memory async SQLite database, so it needs no external infrastructure:

```bash
pytest --cov=app --cov-report=term-missing tests/
```

**Coverage areas**
- **Authentication:** registration, duplicate prevention, password validation, JWT issuance, profile retrieval
- **Authorization:** protected routes reject requests without a valid Bearer token
- **Task CRUD:** create, filter by status (composite-index path), update, delete
- **SQL joins:** eager-loading check on `GET /tasks/{id}/with-owner`

---

## 🔄 CI (GitHub Actions)

Defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Runs on every push and pull request to `main`:

1. Starts a **PostgreSQL 16** service container with a healthcheck
2. Sets up Python 3.12 with dependency caching
3. Lints with **Ruff**
4. Runs **pytest** with coverage

---

## 📖 API reference

Base URL: `http://localhost:8000/api/v1`

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | No | Create a user |
| POST | `/auth/login` | No | Exchange credentials for a JWT |
| GET | `/auth/me` | Bearer | Current user profile |
| POST | `/tasks/` | Bearer | Create a task |
| GET | `/tasks/{id}/with-owner` | Bearer | Task with owner profile (SQL JOIN) |
| GET | `/health` | No | Liveness check |

Full interactive docs are at `/docs`.

### Register

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SuperSecretPassword123!",
    "full_name": "Senior Engineer"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SuperSecretPassword123!"
  }'
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Current user

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### Create a task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Configure Database Indexes",
    "description": "Add composite index on (owner_id, status) for performance",
    "status": "in_progress",
    "priority": "high"
  }'
```

### Task with joined owner

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1/with-owner" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

```json
{
  "id": 1,
  "title": "Configure Database Indexes",
  "description": "Add composite index on (owner_id, status) for performance",
  "status": "in_progress",
  "priority": "high",
  "owner_id": 1,
  "created_at": "2026-10-07T01:50:00Z",
  "updated_at": "2026-10-07T01:50:00Z",
  "owner": {
    "id": 1,
    "email": "developer@example.com",
    "full_name": "Senior Engineer",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2026-10-07T01:48:00Z",
    "updated_at": "2026-10-07T01:48:00Z"
  }
}
```

---

## 🗺️ Roadmap

Known gaps I intend to close. Items already done get checked off.

- [ ] Run the test suite against PostgreSQL in CI, not only SQLite, to catch dialect differences
- [ ] Refresh tokens and token revocation
- [ ] Rate limiting on `/auth/login`
- [ ] Pagination on list endpoints
- [ ] Structured JSON logging with request IDs
- [ ] OpenTelemetry tracing

---

## 👤 Author

Built by [Abhishek Bharti](https://abhishekbharti.com): 9 years building production web platforms, now
focused on AI systems and forward-deployed engineering.
[LinkedIn](https://www.linkedin.com/in/imabhishekbharti/)

Related: [forward-deployed-engineer](https://github.com/abhishekbhartiind/forward-deployed-engineer), a practical guide to FDE roles.