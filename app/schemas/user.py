from datetime import datetime
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="Unique email address", examples=["user@example.com"])
    full_name: Optional[str] = Field(default=None, max_length=100, examples=["John Doe"])
    is_active: bool = Field(default=True, description="Account active state")


class UserCreate(BaseModel):
    """Payload required to register a new user."""
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=8, max_length=100, description="Minimum 8 characters password", examples=["SecureP@ss123"])
    full_name: Optional[str] = Field(default=None, max_length=100, examples=["John Doe"])


class UserLogin(BaseModel):
    """Payload for logging in and obtaining an access token."""
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["SecureP@ss123"])


class UserUpdate(BaseModel):
    """Optional fields for updating a user profile."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=8, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Safe user profile response schema (excludes password)."""
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
