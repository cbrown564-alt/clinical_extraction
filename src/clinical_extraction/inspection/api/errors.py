from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse


class TraceExplorerError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        safe_details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.safe_details = safe_details or {}


async def trace_explorer_error_handler(
    request: Request,
    error: Exception,
) -> JSONResponse:
    del request
    if not isinstance(error, TraceExplorerError):
        raise error
    return JSONResponse(
        status_code=error.status_code,
        content={
            "schema_version": "trace.v1",
            "error": {
                "code": error.code,
                "message": error.message,
                "request_id": uuid4().hex,
                "details": error.safe_details,
            },
        },
    )


def not_found() -> TraceExplorerError:
    return TraceExplorerError(
        status_code=404,
        code="not_found",
        message="The requested resource was not found.",
    )


def aggregate_only() -> TraceExplorerError:
    return TraceExplorerError(
        status_code=403,
        code="aggregate_only",
        message="This run is aggregate-only; record inspection is unavailable.",
    )
