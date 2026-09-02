import time
from uuid import uuid4

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    """Pure ASGI middleware for safe contextvars propagation and performance logging."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Case-insensitive header lookup safely handling ASGI bytes
        request_id = str(uuid4())
        for key, value in scope.get("headers", []):
            if key.lower() == b"x-request-id":
                request_id = value.decode("utf-8")
                break

        # Dynamically attach query string only if it contains parameters
        context = {
            "request_id": request_id,
            "method": scope["method"],
            "path": scope["path"],
        }
        if query_raw := scope.get("query_string"):
            context["query_string"] = query_raw.decode("utf-8")

        structlog.contextvars.bind_contextvars(**context)

        start_time = time.perf_counter()
        status_code = None

        async def send_wrapper(message: dict) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = message.setdefault("headers", [])
                response_headers.append((b"x-request-id", request_id.encode("utf-8")))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)

            duration = time.perf_counter() - start_time
            logger.info(
                "request_processed",
                duration_ms=round(duration * 1000, 2),
                status_code=status_code,
            )

        except Exception as exc:
            duration = time.perf_counter() - start_time
            logger.exception(
                "unhandled_request_exception",
                duration_ms=round(duration * 1000, 2),
                status_code=status_code or 500,  # Fallback to standard Server Error code
                error=str(exc),
            )
            raise

        finally:
            structlog.contextvars.clear_contextvars()
