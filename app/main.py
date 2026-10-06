from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    # Startup: Ensure tables exist (useful for dev and SQLite test runs)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Dispose engine connection pool cleanly
    await engine.dispose()


def create_application() -> FastAPI:
    """Application factory configuring middleware, routes, and error handling."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "Production-ready FastAPI + PostgreSQL microservice featuring "
            "Clean Architecture, JWT Authentication, SQLAlchemy 2.0 Async ORM, "
            "Alembic migrations, Docker containerization, and automated tests."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Domain Exception Handlers
    register_exception_handlers(app)

    # Mount API v1 Routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "api": settings.API_V1_STR
        }

    return app


app = create_application()
