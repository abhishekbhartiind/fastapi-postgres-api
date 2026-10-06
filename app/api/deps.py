from typing import Annotated
# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer
# pyrefly: ignore [missing-import]
from jwt.exceptions import InvalidTokenError
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.task_service import TaskService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login-oauth2"
)


# Reusable Annotated type shortcuts
DbSession = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_user_repository(db: DbSession) -> UserRepository:
    """Dependency injection provider for UserRepository."""
    return UserRepository(db)


async def get_task_repository(db: DbSession) -> TaskRepository:
    """Dependency injection provider for TaskRepository."""
    return TaskRepository(db)


async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> AuthService:
    """Dependency injection provider for AuthService."""
    return AuthService(user_repo)


async def get_task_service(
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)]
) -> TaskService:
    """Dependency injection provider for TaskService."""
    return TaskService(task_repo)


async def get_current_user(
    db: DbSession,
    token: TokenDep
) -> User:
    """Extract, decode, and validate the JWT Bearer token and retrieve the User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (InvalidTokenError, ValueError):
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


# Shortcut for protected endpoint user injection
CurrentUser = Annotated[User, Depends(get_current_user)]
