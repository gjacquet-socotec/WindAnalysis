"""
Entry point for launching the Wind Turbine Analytics FastAPI application.

Usage:
    python main.py

Or with uvicorn directly:
    uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300 --reload
"""
import sys
from pathlib import Path

# Add project root to PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.api.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable hot reload in development
        timeout_keep_alive=300,  # 5 minutes for long-running analyses
        log_level="info",
    )
