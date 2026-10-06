from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.repositories.schemas import (
    RepositoryCreate,
    RepositoryResponse,
    RepositoryUpdate,
)
from app.api.deps import CurrentUser
from app.common.pagination import PageParams, page_params
from app.common.responses import ListResponse, SuccessResponse, ok
from app.modules.repositories.service import RepositoryService

router = APIRouter(
    prefix="/repository",
    tags=["Repository Management"],
)

# Create a repository for the authenticated user.
@router.post(
    "/",
    response_model=SuccessResponse[RepositoryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RepositoryCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = RepositoryService(db)

    result = await service.create_repo(data, current_user)
    return ok(result)


# List the authenticated user's repositories. Supports `page` and `page_size` query parameters.
@router.get(
    "/",
    response_model=ListResponse[RepositoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_repos(
    current_user: CurrentUser,
    pagination: PageParams = Depends(page_params),
    db: AsyncSession = Depends(get_db),
):
    service = RepositoryService(db)

    result = await service.get_all_repos(current_user, pagination)
    return ListResponse(data=result.items, meta=result.to_meta())


# Get one repository owned by the authenticated user.
@router.get(
    "/{repo_id}",
    response_model=SuccessResponse[RepositoryResponse],
)
async def get_repo(
    repo_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = RepositoryService(db)
    result = await service.get_repo(repo_id, current_user)
    return ok(result)


# Update one repository owned by the authenticated user.
@router.put(
    "/{repo_id}",
    response_model=SuccessResponse[RepositoryResponse],
)
@router.patch(
    "/{repo_id}",
    response_model=SuccessResponse[RepositoryResponse],
)
async def update_repo(
    repo_id: UUID,
    data: RepositoryUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    service = RepositoryService(db)
    result = await service.update_repo(repo_id, data, current_user)
    return ok(result)


# Delete one repository owned by the authenticated user.
@router.delete(
    "/{repo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_repo(
    repo_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Response:
    service = RepositoryService(db)
    await service.delete_repo(repo_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
