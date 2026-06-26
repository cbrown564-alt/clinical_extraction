"""Shared helpers for process-cached JSON Observatory endpoints."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException
from fastapi.responses import Response


def cached_json_route(
    cached_fn: Callable[[], str],
    *,
    error_detail: str,
) -> Callable[[], Response]:
    """Return a FastAPI handler that serves a process-cached JSON payload."""

    def endpoint() -> Response:
        try:
            return Response(content=cached_fn(), media_type="application/json")
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(status_code=500, detail=f"{error_detail}: {exc}") from exc

    return endpoint
