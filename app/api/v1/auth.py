from typing import Annotated
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, get_auth_service
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
async def register_user(
    user_in: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> UserResponse:
    """Create a new user account with hashed password and email validation."""
    user = await auth_service.register(user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login with JSON body to retrieve JWT token"
)
async def login_json(
    credentials: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """Authenticate via email/password JSON payload and return a Bearer JWT."""
    user = await auth_service.authenticate(credentials.email, credentials.password)
    return auth_service.generate_token(user)


@router.post(
    "/login-oauth2",
    response_model=Token,
    summary="Login via OAuth2 password flow (used by Swagger UI)"
)
async def login_oauth2(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    """OAuth2 password form login (supports Swagger UI 'Authorize' button)."""
    user = await auth_service.authenticate(form_data.username, form_data.password)
    return auth_service.generate_token(user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile"
)
async def get_current_user_profile(
    current_user: CurrentUser
) -> UserResponse:
    """Return the currently authenticated user based on JWT Bearer token."""
    return current_user
