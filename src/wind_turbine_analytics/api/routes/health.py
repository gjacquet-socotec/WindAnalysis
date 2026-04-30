"""
Health check endpoint.
"""
from fastapi import APIRouter
from src.wind_turbine_analytics.api.models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse with status and version information
    """
    return HealthResponse(status="healthy", version="1.0.0")
