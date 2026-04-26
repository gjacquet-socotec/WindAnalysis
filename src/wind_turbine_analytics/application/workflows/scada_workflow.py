"""SCADA application workflow."""

from __future__ import annotations


import pandas as pd
from typing import Dict, Any
from src.wind_turbine_analytics.application.configuration.config_models import (
    ScadaRunnerConfig,
)
from src.wind_turbine_analytics.application.workflows.base_workflow import BaseWorkflow
from src.wind_turbine_analytics.data_processing.data_processing import (
    DataProcessingStep,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_cut_in_cut_out_analyzer import (
    EbACutInCutOutAnalyzer,
)

from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_manifacturer_analyzer import (
    EbaManufacturerAnalyzer,
)

from src.wind_turbine_analytics.data_processing.analyzer.logics.data_availability_analyzer import (
    DataAvailabilityAnalyzer,
)


class ScadaWorkflow(BaseWorkflow):
    """Coordinates SCADA data ingestion, criteria evaluation, and chart exports."""

    def __init__(self, config: ScadaRunnerConfig, presenter) -> None:
        super().__init__(config, presenter)

    def run(self) -> None:

        # this should be done in the main logic, since this is common for scada and runtest
        self.validation_step()
        # [TODO] comptue analysis per turbine
        self.process_step()
        # [TODO] gather those information per turbine
        return

    def process_step(self) -> None:
        eba_cut_in_cut_out_results = DataProcessingStep(
            analyzer=EbACutInCutOutAnalyzer(),
            visualizer=None,  # [TODO] add visualizer for cut-in/cut-out analysis
        ).execute(self.turbine_sources, self.validation_criteria)
        eba_manufacturer_results = DataProcessingStep(
            analyzer=EbaManufacturerAnalyzer(),
            visualizer=None,  # [TODO] add visualizer for manufacturer EBA analysis
        ).execute(self.turbine_sources, self.validation_criteria)
        data_availability_results = DataProcessingStep(
            analyzer=DataAvailabilityAnalyzer(),
            visualizer=None,  # [TODO] add visualizer for data availability analysis
        ).execute(self.turbine_sources, self.validation_criteria)


def run_scada_pipeline(config: ScadaRunnerConfig, presenter) -> Any:
    return ScadaWorkflow(config=config, presenter=presenter).run()
