from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request

from clinical_extraction.trace_explorer.api.errors import (
    TraceExplorerError,
    trace_explorer_error_handler,
)
from clinical_extraction.trace_explorer.api.routes_catalog import router as catalog_router
from clinical_extraction.trace_explorer.api.routes_frontend import router as frontend_router
from clinical_extraction.trace_explorer.api.routes_traces import router as traces_router
from clinical_extraction.trace_explorer.frontend_data import FrontendDataStore
from clinical_extraction.trace_explorer.index import TraceIndex, build_index
from clinical_extraction.trace_explorer.review_store import ReviewStore

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _fixture_path() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "syn_014.json"


def create_app(
    *,
    index_dir: Path | None = None,
    host: str = "127.0.0.1",
    frontend_fixture_root: Path | None = None,
    review_db_path: Path | None = None,
) -> FastAPI:
    if host not in LOOPBACK_HOSTS:
        raise ValueError("trace explorer must bind to a loopback address")

    resolved_index_dir = index_dir or (_repository_root() / ".trace_explorer")
    index = TraceIndex(resolved_index_dir)
    if not index.ready:
        build_index(
            artifacts=[_fixture_path()],
            output=resolved_index_dir,
            approved_roots=[_repository_root()],
        )
        index = TraceIndex(resolved_index_dir)

    resolved_frontend_data = frontend_fixture_root or (
        _repository_root() / "frontend" / "frontend" / "public" / "mock-data"
    )
    frontend_data = FrontendDataStore(resolved_frontend_data)
    review_store = ReviewStore(review_db_path or (resolved_index_dir / "reviews.sqlite3"))

    app = FastAPI(
        title="Clinical Extraction Explorer API",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
    )
    app.state.trace_index = index
    app.state.frontend_data = frontend_data
    app.state.review_store = review_store
    app.add_exception_handler(TraceExplorerError, trace_explorer_error_handler)
    app.include_router(frontend_router)
    app.include_router(catalog_router)
    app.include_router(traces_router)

    @app.middleware("http")
    async def local_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'self'"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return app


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the local clinical trace explorer.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--index", default=".trace_explorer")
    arguments = parser.parse_args(argv)
    app = create_app(index_dir=Path(arguments.index), host=arguments.host)
    uvicorn.run(app, host=arguments.host, port=arguments.port, access_log=False)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI entry point
    raise SystemExit(main())
