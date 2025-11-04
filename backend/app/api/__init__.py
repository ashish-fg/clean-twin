"""API package for CleanTwin application."""

from .inspections import router as inspections_router

__all__ = [
    "inspections_router",
]
