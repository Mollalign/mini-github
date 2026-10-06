from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.modules.repositories.schemas import (
    RepositoryCreate,
    RepositoryResponse,
    RepositoryUpdate,
)

from app.modules.repositories.models import Repository
from app.modules.users.models import User
from app.modules.repositories.repository import RepositoryRepo
from app.common.exceptions import ConflictException, NotFoundException
from app.common.pagination import Page, PageParams


class RepositoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repos_repo = RepositoryRepo(db)


    # Create a repository for the authenticated user.
    async def create_repo(self, data: RepositoryCreate, user: User) -> RepositoryResponse:
        existing_repo = await self.repos_repo.get_by_owner_and_name(user.id, data.name)
        if existing_repo:
            raise ConflictException(
                "Repository already exists",
                code="repo_taken",
            )

        try:
            new_repo = Repository(
                owner_id=user.id,
                name=data.name,
                description=data.description,
                is_private=data.is_private if data.is_private is not None else False,
                default_branch=data.default_branch or "main",
            )
            created_repo = await self.repos_repo.create(new_repo)
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise ConflictException(
                "Repository creation failed due to a database conflict",
                code="duplicate_repo",
            ) from exc

        await self.db.refresh(created_repo)
        return RepositoryResponse.model_validate(created_repo)

    # Return one page of repositories owned by the authenticated user.
    async def get_all_repos(
        self,
        user: User,
        pagination: PageParams,
    ) -> Page[RepositoryResponse]:
        repos, total = await self.repos_repo.get_by_owner(
            user.id,
            offset=pagination.offset,
            limit=pagination.limit,
        )
        return Page(
            items=[RepositoryResponse.model_validate(repo) for repo in repos],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    # Return one repository when it belongs to the authenticated user.
    async def get_repo(self, repo_id: UUID, user: User) -> RepositoryResponse:
        repo = await self._get_owned_repo(repo_id, user)
        return RepositoryResponse.model_validate(repo)

    # Apply the supplied changes to a repository owned by the authenticated user.
    async def update_repo(
        self,
        repo_id: UUID,
        data: RepositoryUpdate,
        user: User,
    ) -> RepositoryResponse:
        repo = await self._get_owned_repo(repo_id, user)
        changes = data.model_dump(exclude_unset=True)

        new_name = changes.get("name")
        if new_name is not None and new_name != repo.name:
            existing_repo = await self.repos_repo.get_by_owner_and_name(
                user.id,
                new_name,
            )
            if existing_repo is not None:
                raise ConflictException(
                    "Repository already exists",
                    code="repo_taken",
                )

        for field, value in changes.items():
            setattr(repo, field, value)

        try:
            updated_repo = await self.repos_repo.update(repo)
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise ConflictException(
                "Repository update failed due to a database conflict",
                code="duplicate_repo",
            ) from exc

        return RepositoryResponse.model_validate(updated_repo)

    # Delete a repository owned by the authenticated user.
    async def delete_repo(self, repo_id: UUID, user: User) -> None:
        repo = await self._get_owned_repo(repo_id, user)

        await self.repos_repo.delete(repo)
        await self.db.commit()

    # Look up a repository and prevent access to repositories owned by others.
    async def _get_owned_repo(self, repo_id: UUID, user: User) -> Repository:
        repo = await self.repos_repo.get_by_id(repo_id)
        if repo is None or repo.owner_id != user.id:
            raise NotFoundException("Repository not found", code="repo_not_found")

        return repo
