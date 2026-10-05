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
from app.common.exceptions import ConflictException


class RepositoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repos_repo = RepositoryRepo(db)


    # Create Repository
    async def create_repo(self, data: RepositoryCreate, user: User) -> RepositoryResponse:
        try:
            async with self.db.begin():
                existing_repo = await self.repos_repo.get_by_owner_and_name(
                    user.id,
                    data.name,
                )
                if existing_repo:
                    raise ConflictException(
                        "Repository already exists",
                        code="repo_taken",
                    )

                new_repo = Repository(
                    owner_id=user.id,
                    name=data.name,
                    description=data.description,
                    is_private=data.is_private if data.is_private is not None else False,
                    default_branch=data.default_branch or "main"
                )

                created_repo = await self.repos_repo.create(new_repo)
                
        except IntegrityError as exc:
            raise ConflictException(
                "Repository creation failed due to a database conflict",
                code="duplicate_repo",
            ) from exc
            
        await self.db.refresh(created_repo)
        return RepositoryResponse.model_validate(created_repo)
