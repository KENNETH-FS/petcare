import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import AppError

logger = logging.getLogger(__name__)

_HTTP_CODES = {
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
}


def _envelope(code: str, message: str, details: list | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or []}}


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(exc.code, exc.message),
    )


async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(p) for p in err["loc"][1:]) or "body",
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_envelope(
            "VALIDATION_ERROR", "The request payload failed validation.", details
        ),
    )


async def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(
            _HTTP_CODES.get(exc.status_code, "HTTP_ERROR"),
            str(exc.detail),
        ),
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_envelope("INTERNAL_ERROR", "An internal error occurred."),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
