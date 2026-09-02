"""Global exception handling layer to enforce standardized ErrorResponse envelopes."""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.responses import ErrorDetail, ErrorResponse

logger = structlog.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Map operational and unhandled system exceptions to the ErrorResponse contract."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors: list[ErrorDetail] = []

        for err in exc.errors():
            # Construct a human-readable field path (e.g., "body.user.email")
            # We omit the generic first element if it's just 'body' or 'query'
            loc_path = err.get("loc", ())
            field_name = (
                ".".join(str(loc) for loc in loc_path[1:])
                if len(loc_path) > 1
                else ".".join(str(loc) for loc in loc_path)
            )

            errors.append(
                ErrorDetail(
                    code="validation_error",
                    message=err.get("msg", "Invalid field value."),
                    field=field_name or None,
                )
            )

        # Contextvars (like request_id) are automatically attached by structlog here
        logger.warning(
            "request_validation_failed",
            error_count=len(errors),
        )

        response_body = ErrorResponse(errors=errors)
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(response_body),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.warning(
            "http_exception_raised",
            status_code=exc.status_code,
            detail=exc.detail,
        )

        response_body = ErrorResponse(
            errors=[
                ErrorDetail(
                    code="http_error",
                    message=str(exc.detail),
                )
            ]
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(response_body),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Crucial for production debugging: logs full traceback inside your JSON stream
        logger.exception(
            "unhandled_system_failure",
            error=str(exc),
        )

        response_body = ErrorResponse(
            errors=[
                ErrorDetail(
                    code="internal_server_error",
                    message="An unexpected system error occurred.",
                )
            ]
        )
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(response_body),
        )
