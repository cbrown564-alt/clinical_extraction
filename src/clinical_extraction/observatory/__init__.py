"""FastAPI backend for the clinical-extraction Observatory (Gan 2026 + ExECTv2)."""

from .api import app, create_app

__all__ = ["app", "create_app"]
