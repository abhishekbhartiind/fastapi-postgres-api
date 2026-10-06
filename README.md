# 🚀 Containerized FastAPI + PostgreSQL Service

[![CI Pipeline](https://github.com/example/fastapi-postgres-service/actions/workflows/ci.yml/badge.svg)](https://github.com/example/fastapi-postgres-service/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

A production-grade, enterprise-structured backend microservice built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0 Async ORM**, **Alembic**, and **Docker**. Architected with **Clean / Layered Architecture** and **SOLID principles**.

---

## 🏛️ Architectural Overview & SOLID Principles

This service adopts **Clean / Layered Architecture** to enforce separation of concerns, high maintainability, and testability:

```text
 ┌──────────────────────────────────────────────────────────┐
 │                     HTTP Client                          │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │  Presentation Layer (app/api/v1/)                        │
 │  - FastAPI Routers, HTTP Serialization, Status Codes     │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │  Service Layer (app/services/)                           │
 │  - Business Logic, Password Hashing, JWT Issuance        │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │  Repository Layer (app/repositories/)                    │
 │  - Async SQLAlchemy 2.0 Queries, SQL Joins, Index Filters│
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │  Persistence & Domain Models (app/models/, app/db/)      │
 │  - PostgreSQL Database Tables, Relationships, Indexes    │
 └──────────────────────────────────────────────────────────┘
```

### Mapping to SOLID Principles:
- **S (Single Responsibility)**: Repositories handle data queries; Services encapsulate business logic; Routers manage HTTP serialization.
- **O (Open/Closed)**: Generic `BaseRepository[ModelType]` allows extending data access without modifying core query mechanics.
- **L (Liskov Substitution)**: Specialized repositories (`UserRepository`, `TaskRepository`) substitute cleanly for `BaseRepository`.
- **I (Interface Segregation)**: Granular Pydantic schemas (`UserCreate`, `UserLogin`, `UserResponse`) prevent payload pollution.
- **D (Dependency Inversion)**: Routers depend on abstract dependencies injected via FastAPI's `Depends()`, making testing against SQLite instant and isolated.

---

## 📁 Repository Structure

```text
fastapi-postgres-service/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow (linting + pytest)
├── .dockerignore                # Docker ignore rules
├── .env.example                 # Environment variables template
├── .gitignore                   # Python gitignore
├── Dockerfile                   # Multi-stage production container image
├── docker-compose.yml           # App + PostgreSQL container orchestration
├── pyproject.toml               # Project metadata and dependencies (uv/pip)
├── requirements.txt             # Pip dependencies
├── alembic.ini                  # Alembic database migration config
├── README.md                    # Project documentation
├── alembic/
│   ├── env.py                   # Async Alembic execution environment
│   └── versions/
│       └── 001_initial_schema.py# Initial database migration script
├── app/
│   ├── main.py                  # Application factory, CORS, lifespan & error handlers
│   ├── core/                    # Core configuration, security, JWT & exceptions
│   │   ├── config.py            # Pydantic Settings
│   │   ├── security.py          # Bcrypt hashing & PyJWT token management
│   │   └── exceptions.py        # Domain exceptions & error handlers
│   ├── db/                      # Database connection and sessions
│   │   ├── base.py              # DeclarativeBase & TimestampMixin
│   │   └── session.py           # Async engine & session generator
│   ├── models/                  # SQLAlchemy 2.0 ORM models
│   │   ├── user.py              # User model with B-Tree indexes
│   │   └── task.py              # Task model with Foreign Key & composite index
│   ├── schemas/                 # Pydantic v2 validation models
│   │   ├── token.py             # JWT token models
│   │   ├── user.py              # User request/response schemas
│   │   └── task.py              # Task request/response schemas (with joins)
│   ├── repositories/            # Data Access Layer (Repository Pattern)
│   │   ├── base.py              # Generic Async BaseRepository
│   │   ├── user_repository.py   # User queries
│   │   └── task_repository.py   # Task queries (Joins & Index filters)
│   ├── services/                # Business Logic Layer
│   │   ├── auth_service.py      # Registration & Authentication
│   │   └── task_service.py      # Task management & authorization
│   └── api/                     # HTTP Delivery Layer
│       ├── deps.py              # Dependency injection & JWT verification
│       └── v1/
│           ├── auth.py          # Auth routes (/register, /login, /me)
│           ├── tasks.py         # Task CRUD routes (/tasks/)
│           └── router.py        # Combined v1 router
├── docs/
│   └── SQL_AND_QUERY_PLANS.md   # PostgreSQL deep dive: Joins, Indexes, Query Plans
└── tests/
    ├── conftest.py              # AsyncClient fixture & in-memory test DB
    ├── test_auth.py             # Auth integration tests
    └── test_tasks.py            # Task CRUD & Join tests
```

---

## ⚡ Quick Start: Containerized Execution with Docker

The fastest way to spin up the application with a real PostgreSQL database is using **Docker Compose**:

```bash
# 1. Clone / Navigate to directory
cd /Users/abhishekbharti/GenAI/Projects/fastapi-postgres-service

# 2. Start PostgreSQL and FastAPI in background
docker-compose up --build -d

# 3. View live application logs
docker-compose logs -f api
```

The services will be available at:
- **API Root**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

To stop the containers:
```bash
docker-compose down -v
```

---

## 💻 Local Development Setup

### 1. Using `uv` (Recommended)
```bash
cd /Users/abhishekbharti/GenAI/Projects/fastapi-postgres-service

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Using standard Python `venv`
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(For quick local testing without PostgreSQL running, you can set `DATABASE_URL=sqlite+aiosqlite:///./test.db` in `.env`)*

### 4. Run Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🐘 PostgreSQL, SQL Joins & Indexes

This project incorporates database engineering best practices:

1. **Foreign Key & Cascade Deletion**:
   `tasks.owner_id` references `users.id` with `ondelete="CASCADE"`. Deleting a user purges their tasks in a single atomic transaction.
2. **Single-Column B-Tree Indexes**:
   - `ix_users_email` (Unique B-Tree): Instant $O(\log N)$ user lookups during login.
   - `ix_tasks_owner_id`: Fast joins between tasks and users.
3. **Composite Index**:
   - `idx_tasks_owner_status (owner_id, status)`: Accelerates queries like `SELECT * FROM tasks WHERE owner_id = ? AND status = 'pending'`.
4. **SQL Joins & Eager Loading**:
   - Implemented in `TaskRepository.get_task_with_owner()` using SQLAlchemy's `joinedload(Task.owner)`.
   - Eliminates the classic **N+1 query problem**.
5. **Alembic Database Migrations**:
   ```bash
   alembic upgrade head
   ```

👉 For a comprehensive technical analysis on PostgreSQL B-Trees, `EXPLAIN (ANALYZE, BUFFERS)` execution plans, and join mechanics, see **[docs/SQL_AND_QUERY_PLANS.md](./docs/SQL_AND_QUERY_PLANS.md)**.

---

## 🧪 Running the Automated Test Suite

The test suite runs against an isolated async in-memory SQLite database, requiring zero external infrastructure:

```bash
# Run all tests with coverage report
pytest --cov=app --cov-report=term-missing tests/
```

### What is covered:
- **Authentication**: Registration, duplicate prevention, password validation, JWT token issuance, profile retrieval.
- **Authorization**: Protected routes rejection without valid Bearer token.
- **Task CRUD**: Creating, filtering by status (composite index), updating, and deleting.
- **SQL Joins**: Eager loading verification on `GET /tasks/{id}/with-owner`.

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Located at [`.github/workflows/ci.yml`](./.github/workflows/ci.yml):
- **Triggers**: On every `push` and `pull_request` to `main`.
- **Steps**:
  1. Spins up an official **PostgreSQL 16** service container with automated healthcheck.
  2. Sets up Python 3.12 environment with caching.
  3. Lints the codebase with **Ruff**.
  4. Runs **Pytest** with coverage thresholds.

---

## 📖 API Endpoint Reference & cURL Examples

### 1. Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SuperSecretPassword123!",
    "full_name": "Senior Engineer"
  }'
```

### 2. Login to Obtain JWT Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "password": "SuperSecretPassword123!"
  }'
```
*Response:*
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Authenticated User Profile
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 4. Create a Task (Protected)
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

### 5. Fetch Task with Joined Owner Profile (SQL JOIN)
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1/with-owner" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```
*Response:*
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
