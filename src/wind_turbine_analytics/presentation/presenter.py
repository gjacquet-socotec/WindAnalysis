from __future__ import annotations
from typing import Any
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult


class PipelinePresenter:
    """Default no-op presenter implementation."""

    def show_test_results(self, result: Any) -> None:
        return None

    def show_test_park_summary(self, results: list[Any]) -> None:
        return None

    def info(self, message: str) -> None:
        return None

    def show_analysis_result(self, result: AnalysisResult, analysis_name: str) -> None:
        """Display analysis results in a structured way."""
        return None
