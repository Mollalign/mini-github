from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    decode_token
)
from app.modules.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
)
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.common.exceptions import ConflictException

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)


    # Register User
    async def register(self, data: RegisterRequest) -> AuthResponse:
        try:
            async with self.db.begin():
                # These checks provide a useful error response. Database unique
                existing_username = await self.user_repo.get_by_username(data.username)
                if existing_username:
                    raise ConflictException(
                        "Username is already taken",
                        code="username_taken",
                    )

                existing_email = await self.user_repo.get_by_email(data.email)
                if existing_email:
                    raise ConflictException(
                        "Email is already registered",
                        code="email_taken",
                    )

                user = User(
                    username=data.username,
                    email=data.email,
                    password_hash=hash_password(data.password),
                    full_name=data.full_name,
                )
                user = await self.user_repo.create(user)
        except IntegrityError as exc:
            raise ConflictException(
                "Username or email is already registered",
                code="duplicate_user",
            ) from exc

        await self.db.refresh(user)

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )

    # Login 
    async def login(self, data: LoginRequest) -> AuthResponse:
        user = await self.user_repo.get_by_username_or_email(
            data.username_or_email
        )

        # Don't reveal whether username/email exists
        if not user or not verify_password(
            data.password,
            user.password_hash
        ):
            raise ValueError("Invalid username/email or password")

        # check if the user is active
        if not user.is_active:
            raise ValueError("User account is inactive")

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )

    # Reset Token by Refresh Token
    async def refresh(self, data: RefreshTokenRequest) -> TokenResponse:
        payload = decode_token(data.refresh_token)
        if not payload:
            raise ValueError("Token could not be decoded")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing subject identifier")

        if not user_id:
            raise ValueError("Invalid refresh token")


        try:
            user_uuid = UUID(user_id)
        except (ValueError, AttributeError):
            raise ValueError("Invalid user ID format")

        user = await self.user_repository.get(user_uuid)
        if not user or not user.is_active:
            raise ValueError("User inactive or not found")

        return TokenResponse(
            access_token=create_access_token(user_uuid),
            refresh_token=create_refresh_token(user_uuid),
        )



        
