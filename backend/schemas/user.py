from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

# --- Request Schemas (what comes IN) ---

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    class Config:
        str_strip_whitespace = True  # auto trims accidental spaces

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# --- Response Schemas (what goes OUT) ---

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # lets pydantic read SQLAlchemy model attributes

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"