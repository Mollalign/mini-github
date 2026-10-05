from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.repositories.schemas import (
    RepositoryCreate,
    RepositoryUpdate,
    RepositoryResponse,
)
from app.api.deps import CurrentUser
from app.modules.repositories.service import RepositoryService
from app.common.responses import SuccessResponse, ok

router = APIRouter(
    prefix="/repository",
    tags=["Repository Management"],
)

# Create Repository
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
    
    try:
        result = await service.create_repo(data, current_user)
        return ok(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
