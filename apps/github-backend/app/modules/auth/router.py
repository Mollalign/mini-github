from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.api.deps import CurrentUser
from app.modules.auth.service import AuthService
from app.common.responses import SuccessResponse, ok

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# Register
@router.post(
    "/register",
    response_model=SuccessResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        result = await service.register(data)
        return ok(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

# Login
@router.post(
    "/login",
    response_model=SuccessResponse[AuthResponse],
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        result = await service.login(data)
        return ok(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

# Reset Token By Refresh token
@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)

    try:
        result = await service.refresh(data)
        return ok(result)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

# Get Current User
@router.get(
    "/me",
    response_model=SuccessResponse[UserResponse],
)
async def get_me(
    current_user: CurrentUser,
):
    return ok(current_user)