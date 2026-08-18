import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging_config import request_id_var

logger = logging.getLogger("app.request")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assigns a request ID, times the request, and logs one structured
    event per request — the request's outcome, not a narrated string.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get("x-request-id")
        request_id = incoming or str(uuid.uuid4())
        token = request_id_var.set(request_id)

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "request_failed",
                extra={
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)
