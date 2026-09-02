"""Offset-based pagination primitives integrated with standardized ListResponse contracts."""

from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

T = TypeVar("T")


class PageParams(BaseModel):
    """Calculates extraction slices for SQL execution frameworks."""

    page: int = Field(1, ge=1)
    page_size: int = Field(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        """Calculate SQL OFFSET."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Calculate SQL LIMIT."""
        return self.page_size


def page_params(
    page: int = Query(1, ge=1, description="Page number starting from 1."),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Number of items to return per page."
    ),
) -> PageParams:
    """FastAPI query dependency providing type validation and openapi parameter hints."""
    return PageParams(page=page, page_size=page_size)


class Page(BaseModel, Generic[T]):
    """Unified database execution container mapped to your global ListResponse envelope."""

    items: list[T]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        """Calculate total pages using safe integer arithmetic."""
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    def to_meta(self) -> dict[str, object]:
        """Format metadata to fit perfectly into ListResponse.meta."""
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.page < self.total_pages,
            "has_previous": self.page > 1 and self.total_pages > 0,
        }
