from __future__ import annotations

from typing import Any


class AppException(Exception):
    """Base exception for application-level errors."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or self.message)

        self.message = message or self.message

        if code is not None:
            self.code = code

        if status_code is not None:
            self.status_code = status_code

        self.details = details or {}


class BadRequestException(AppException):
    """400 Bad Request."""

    status_code = 400
    code = "bad_request"
    message = "Invalid request."


class UnauthorizedException(AppException):
    """401 Unauthorized."""

    status_code = 401
    code = "unauthorized"
    message = "Authentication is required."


class ForbiddenException(AppException):
    """403 Forbidden."""

    status_code = 403
    code = "forbidden"
    message = "You do not have permission to perform this action."


class NotFoundException(AppException):
    """404 Not Found."""

    status_code = 404
    code = "not_found"
    message = "The requested resource was not found."


class ConflictException(AppException):
    """409 Conflict."""

    status_code = 409
    code = "conflict"
    message = "The request conflicts with the current state."


class ValidationException(AppException):
    """422 Validation Error."""

    status_code = 422
    code = "validation_error"
    message = "The request data is invalid."


class TooManyRequestsException(AppException):
    """429 Too Many Requests."""

    status_code = 429
    code = "too_many_requests"
    message = "Too many requests. Please try again later."


class ServiceUnavailableException(AppException):
    """503 Service Unavailable."""

    status_code = 503
    code = "service_unavailable"
    message = "The service is temporarily unavailable."