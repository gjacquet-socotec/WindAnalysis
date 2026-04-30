"""
API module for Wind Turbine Analytics.

This module provides a FastAPI-based REST API to trigger RunTest and SCADA workflows
and retrieve analysis results (charts, tables, metadata) as JSON responses.
"""
from .main import app

__all__ = ["app"]
