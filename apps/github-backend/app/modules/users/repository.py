from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Create User
    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    # Get User By id
    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    # Get the user by username
    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )

        return result.scalar_one_or_none()

    
    # get the user by email
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()


    # get the user by username or email
    async def get_by_username_or_email(
        self,
        identifier: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                (User.username == identifier)
                | (User.email == identifier)
            )
        )

        return result.scalar_one_or_none()

    # check if the user exist by this username
    async def exists_by_username(self, username: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.username == username)
        )

        return result.scalar_one_or_none() is not None

    # check if the user exist by this email
    async def exists_by_email(self, email: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )

        return result.scalar_one_or_none() is not None
