from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Repository

class RepositoryRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Create Repository
    async def create(self, repo: Repository) -> Repository:
        self.db.add(repo)
        await self.db.flush()
        return repo    

    # Get Repository by ID
    async def get_by_id(
        self,
        repo_id: UUID,
    ) -> Repository | None:
        result = await self.db.execute(
            select(Repository).where(
                Repository.id == repo_id
            )
        )

        return result.scalar_one_or_none()

    # Get Repository by owner and name
    async def get_by_owner_and_name(
        self,
        owner_id: UUID,
        name: str,
    ) -> Repository | None:
        result = await self.db.execute(
            select(Repository).where(
                Repository.owner_id == owner_id,
                Repository.name == name,
            )
        )

        return result.scalar_one_or_none()

    # Get all repositories owned by a user
    async def get_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Repository]:
        result = await self.db.execute(
            select(Repository)
            .where(Repository.owner_id == owner_id)
            .order_by(Repository.created_at.desc())
        )

        return list(result.scalars().all())

    # Update Repository
    async def update(
        self,
        repo: Repository,
    ) -> Repository:
        await self.db.flush()
        await self.db.refresh(repo)

        return repo

    # Delete Repository
    async def delete(
        self,
        repo: Repository,
    ) -> None:
        await self.db.delete(repo)
        await self.db.flush()

    # Check if repository exists
    async def exists(
        self,
        owner_id: UUID,
        name: str,
    ) -> bool:
        result = await self.db.execute(
            select(Repository.id).where(
                Repository.owner_id == owner_id,
                Repository.name == name,
            )
        )

        return result.scalar_one_or_none() is not None