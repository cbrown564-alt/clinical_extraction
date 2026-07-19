from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from clinical_extraction.trace_explorer.frontend_data import FrontendDataStore
from clinical_extraction.trace_explorer.index import TraceIndex
from clinical_extraction.trace_explorer.review_store import ReviewStore


def get_trace_index(request: Request) -> TraceIndex:
    return request.app.state.trace_index


TraceIndexDependency = Annotated[TraceIndex, Depends(get_trace_index)]


def get_frontend_data(request: Request) -> FrontendDataStore:
    return request.app.state.frontend_data


def get_review_store(request: Request) -> ReviewStore:
    return request.app.state.review_store


FrontendDataDependency = Annotated[FrontendDataStore, Depends(get_frontend_data)]
ReviewStoreDependency = Annotated[ReviewStore, Depends(get_review_store)]
