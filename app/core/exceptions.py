from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception class for domain errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, extra: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.extra = extra
        super().__init__(message)


class EntityNotFoundError(AppException):
    """Raised when a requested entity does not exist."""
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class EntityAlreadyExistsError(AppException):
    """Raised when attempting to create a duplicate entity."""
    def __init__(self, entity_name: str, field: str, value: Any):
        super().__init__(
            message=f"{entity_name} with {field} '{value}' already exists.",
            status_code=status.HTTP_409_CONFLICT
        )


class AuthenticationError(AppException):
    """Raised for authentication failures."""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(AppException):
    """Raised when an authenticated user lacks permission for an action."""
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "extra": exc.extra
                }
            }
        )
