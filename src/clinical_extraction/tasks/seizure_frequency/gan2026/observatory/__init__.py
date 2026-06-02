"""FastAPI backend for the Gan 2026 clinical-extraction Observatory."""

from .api import app, create_app

__all__ = ["app", "create_app"]
