from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from typing import Dict, Any


class BaseVisualizer:
    def generate(self, result: AnalysisResult) -> None:
        """Placeholder for the main visualization method."""
        for check_name, passed in result.detailed_results.items():
            if not passed:
                self._plot_failed_check(check_name, result.metadata)

    def _plot_failed_check(self, check_name: str, metadata: Dict[str, Any]) -> Any:
        """Placeholder for plotting logic for a failed check."""
        raise NotImplementedError(
            f"Visualization for failed check '{check_name}' is not implemented."
        )
