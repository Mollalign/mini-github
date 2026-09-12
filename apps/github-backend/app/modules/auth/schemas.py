from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ─────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=39,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    full_name: str | None = Field(
        default=None,
        max_length=255,
    )


# ─────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────

class LoginRequest(BaseModel):
    username_or_email: str
    password: str


# ─────────────────────────────────────────────
# User response
# ─────────────────────────────────────────────

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    full_name: str | None
    bio: str | None
    avatar_url: str | None
    is_active: bool


# ─────────────────────────────────────────────
# Token response
# ─────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ─────────────────────────────────────────────
# Auth response
# ─────────────────────────────────────────────

class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


# ─────────────────────────────────────────────
# Refresh token request
# ─────────────────────────────────────────────

class RefreshTokenRequest(BaseModel):
    refresh_token: str