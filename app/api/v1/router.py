# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from app.api.v1 import auth, tasks

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health", tags=["Health"], summary="Service health check")
async def health_check():
    return {
        "status": "healthy",
        "service": "fastapi-postgres-service"
    }

api_router.include_router(auth.router)
api_router.include_router(tasks.router)
