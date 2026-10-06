from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Repository

class RepositoryRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Persist a new repository in the current transaction.
    async def create(self, repo: Repository) -> Repository:
        self.db.add(repo)
        await self.db.flush()
        return repo    

    # Find one repository by its ID.
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

    # Find one repository by its owner and name.
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

    # Fetch a page of an owner's repositories and the total matching count.
    async def get_by_owner(
        self,
        owner_id: UUID,
        *,
        offset: int,
        limit: int,
    ) -> tuple[list[Repository], int]:
        result = await self.db.execute(
            select(Repository)
            .where(Repository.owner_id == owner_id)
            .order_by(Repository.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count_result = await self.db.execute(
            select(func.count())
            .select_from(Repository)
            .where(Repository.owner_id == owner_id)
        )

        return list(result.scalars().all()), count_result.scalar_one()

    # Flush pending changes to a repository and return its refreshed state.
    async def update(
        self,
        repo: Repository,
    ) -> Repository:
        await self.db.flush()
        await self.db.refresh(repo)

        return repo

    # Mark a repository for deletion in the current transaction.
    async def delete(
        self,
        repo: Repository,
    ) -> None:
        await self.db.delete(repo)
        await self.db.flush()

    # Check whether an owner already has a repository with this name.
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
