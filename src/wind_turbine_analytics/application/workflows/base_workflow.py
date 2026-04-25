from __future__ import annotations
from typing import Dict, Any, Union
from src.wind_turbine_analytics.application.configuration.config_models import (
    GeneralInformation,
    ValidationCriteria,
    TurbineFarm,
    ScadaRunnerConfig,
    RunTestPipelineConfig,
)
from src.wind_turbine_analytics.application.configuration.config_client import ConfigClient


class BaseWorkflow:

    def __init__(
        self, config: Union[ScadaRunnerConfig, RunTestPipelineConfig], presenter
    ) -> None:
        self._config = config
        self._presenter = presenter
        self.client_config: Dict[str, Any] = {}

        self.general_information: GeneralInformation
        self.validation_criteria: ValidationCriteria
        self.turbine_sources: TurbineFarm

    def validation_step(self) -> None:
        """Placeholder for any setup steps need
        ed before running the workflow."""
        ConfigClient(self._config).validate(self)

    def dataprocessing_step(self) -> None:
        """Placeholder for data processing steps."""
        pass

    def chart_export_step(self) -> None:
        """Placeholder for chart export steps."""
        pass
