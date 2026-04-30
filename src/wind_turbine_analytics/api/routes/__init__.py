"""
API route handlers.
"""
from .analyze import router as analyze_router
from .health import router as health_router
from .config import router as config_router

__all__ = ["analyze_router", "health_router", "config_router"]
