from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class AppException(Exception):
    def __init__(
        self,
        code: str = "APP_ERROR",
        message: str = "An error occurred",
        status_code: int = 500,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str, message: str | None = None) -> None:
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=message or f"{resource} not found",
            status_code=404,
        )


class DuplicateError(AppException):
    def __init__(self, code: str = "DUPLICATE_ERROR", message: str = "Resource already exists") -> None:
        super().__init__(code=code, message=message, status_code=409)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class ValidationError(AppException):
    def __init__(
        self,
        message: str = "Validation error",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.details = details or []
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=422)


def _error_response(status_code: int, code: str, message: str, path: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat(),
            "path": path,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        response = _error_response(exc.status_code, exc.code, exc.message, str(request.url.path))
        if isinstance(exc, ValidationError) and exc.details:
            response_body = response.body
            import json

            body = json.loads(response_body)
            body["details"] = exc.details
            return JSONResponse(status_code=exc.status_code, content=body)
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
                "type": err["type"],
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "timestamp": datetime.now(UTC).isoformat(),
                "path": str(request.url.path),
                "details": details,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", exc_type=type(exc).__name__, path=str(request.url.path))
        return _error_response(
            500, "INTERNAL_ERROR", "Internal server error", str(request.url.path)
        )
