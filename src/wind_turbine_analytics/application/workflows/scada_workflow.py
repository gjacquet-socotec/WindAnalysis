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
from src.wind_turbine_analytics.data_processing.analyzer.logics import (
    EbACutInCutOutAnalyzer,
    EbaManufacturerAnalyzer,
    DataAvailabilityAnalyzer,
    CodeErrorAnalyzer,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_cut_in_cut_out_visualizer import (
    EbaCutInCutOutVisualizer,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_manifacturer_visualizer import (
    EbaManufacturerVisualizer,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_loss_visualizer import (
    EbaLossVisualizer,
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
        # EBA Cut-In/Cut-Out Analysis
        eba_cut_in_cut_out_results = DataProcessingStep(
            analyzer=EbACutInCutOutAnalyzer(),
            visualizers=[EbaCutInCutOutVisualizer()],
            tabler=None,  # [TODO] add tabler for cut-in/cut-out analysis
        ).execute(self.turbine_sources, self.validation_criteria)

        # EBA Manufacturer Analysis
        eba_manufacturer_results = DataProcessingStep(
            analyzer=EbaManufacturerAnalyzer(),
            visualizers=[
                EbaManufacturerVisualizer(),
                EbaLossVisualizer(),
            ],  # [TODO] add visualizer for manufacturer EBA analysis
        ).execute(self.turbine_sources, self.validation_criteria)

        code_error_results = DataProcessingStep(
            analyzer=CodeErrorAnalyzer(),
            visualizers=None,  # [TODO] add visualizer for code error analysis
        ).execute(self.turbine_sources, self.validation_criteria)

        # Data Availability Analysis
        # data_availability_results = DataProcessingStep(
        #     analyzer=DataAvailabilityAnalyzer(),
        #     visualizers=None,  # [TODO] add visualizer for data availability analysis
        # ).execute(self.turbine_sources, self.validation_criteria)
        # self._presenter.show_analysis_result(
        #     data_availability_results, "Data Availability Analysis"
        # )


def run_scada_pipeline(config: ScadaRunnerConfig, presenter) -> Any:
    return ScadaWorkflow(config=config, presenter=presenter).run()
