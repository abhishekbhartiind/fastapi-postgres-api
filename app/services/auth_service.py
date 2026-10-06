from app.core.exceptions import AuthenticationError, EntityAlreadyExistsError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token
from app.schemas.user import UserCreate


class AuthService:
    """Business logic for user registration, authentication, and token management."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, user_in: UserCreate) -> User:
        """Register a new user if email is not already taken."""
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise EntityAlreadyExistsError("User", "email", user_in.email)

        hashed_pwd = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False,
        )
        return await self.user_repo.create(new_user)

    async def authenticate(self, email: str, password: str) -> User:
        """Authenticate user credentials and return the active User entity."""
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("Account is currently inactive.")

        return user

    def generate_token(self, user: User) -> Token:
        """Generate a signed JWT token for the authenticated user."""
        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token, token_type="bearer")
