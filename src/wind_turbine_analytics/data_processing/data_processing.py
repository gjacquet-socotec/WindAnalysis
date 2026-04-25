from src.wind_turbine_analytics.application.workflows.base_workflow import BaseWorkflow
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.analyzer.base_analyzer import (
    BaseAnalyzer,
)
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineFarm,
    ValidationCriteria,
)
from typing import Any, Optional


class DataProcessingStep:
    def __init__(
        self, analyzer: BaseAnalyzer, visualizer: Optional[BaseVisualizer] = None
    ) -> None:
        self.analyzer: BaseAnalyzer = analyzer
        self.visualizer: Optional[BaseVisualizer] = visualizer

    def execute(self, context: TurbineFarm, criteria: ValidationCriteria) -> Any:
        result = self.analyzer.analyze(context, criteria)
        if result.requires_visuals:
            if self.visualizer is not None:
                self.visualizer.generate(result)
        return result
