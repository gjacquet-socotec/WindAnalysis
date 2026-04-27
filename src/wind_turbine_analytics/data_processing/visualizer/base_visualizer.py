from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from typing import Dict, Any, Optional


class BaseVisualizer:
    def __init__(self, chart_name: Optional[str] = None):
        self.chart_name = chart_name

    def generate(self, result: AnalysisResult) -> None:
        """Placeholder for the main visualization method."""
        raise NotImplementedError(
            f"Visualization for failed check '{self.chart_name}' is not implemented."
        )
