from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from typing import Any


class RPMChartVisualizer(BaseVisualizer):
    def __init__(self):
        super().__init__(chart_name="rpm_chart")

    def generate(self, result: AnalysisResult) -> None:
        # Implement visualization logic here
        pass
