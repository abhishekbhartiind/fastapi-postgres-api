from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class Token(BaseModel):
    """JWT response payload containing bearer access token."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload data."""
    sub: Optional[str] = None
    exp: Optional[int] = None
