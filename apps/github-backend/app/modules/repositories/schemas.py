from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RepositoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    is_private: bool = False
    default_branch: str = Field(
        default="main",
        min_length=1,
        max_length=100,
    )


class RepositoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    is_private: bool | None = None
    default_branch: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    is_private: bool
    default_branch: str
    created_at: datetime
    updated_at: datetime