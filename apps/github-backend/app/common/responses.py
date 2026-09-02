"""
Standard response envelopes.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """`{ "data": ... }` envelope for single-resource responses."""

    model_config = ConfigDict(from_attributes=True)

    data: T
    meta: dict[str, object] = Field(default_factory=dict)


class ListResponse(BaseModel, Generic[T]):
    """List envelope with optional pagination metadata."""

    model_config = ConfigDict(from_attributes=True)

    data: list[T]
    meta: dict[str, object] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str
    version: str
    db: bool


class ErrorDetail(BaseModel):
    """Specific error descriptor for validation or system failures."""

    code: str = Field(
        description="Machine-readable error identifier (e.g., 'not_found')."
    )
    message: str = Field(
        description="Human-readable description explaining the error."
    )
    field: str | None = Field(
        default=None,
        description="The target request payload field that caused the issue.",
    )


class ErrorResponse(BaseModel):
    """Global schema layout for all non-2xx API HTTP responses."""

    errors: list[ErrorDetail]
    meta: dict[str, object] = Field(default_factory=dict)


def ok(data: T, meta: dict[str, object] | None = None) -> SuccessResponse[T]:
    """Helper to cleanly wrap single records into a SuccessResponse."""
    return SuccessResponse[T](data=data, meta=meta or {})


def error(
    code: str,
    message: str,
    field: str | None = None,
    meta: dict[str, object] | None = None,
) -> ErrorResponse:
    """Helper to cleanly wrap a standalone error into an ErrorResponse payload."""
    return ErrorResponse(
        errors=[ErrorDetail(code=code, message=message, field=field)],
        meta=meta or {},
    )
