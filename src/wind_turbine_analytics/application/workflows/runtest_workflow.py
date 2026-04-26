# """RunTest application workflow."""

# from __future__ import annotations

# from pathlib import Path

from src.wind_turbine_analytics.application.configuration.config_models import (
    RunTestPipelineConfig,
)
from typing import Any
from src.wind_turbine_analytics.application.workflows.base_workflow import BaseWorkflow
from src.wind_turbine_analytics.data_processing.analyzer.logics.consecutive_hours_analyzer import (
    ConsecutiveHoursAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.test_cut_in_cut_out_analyzer import (
    TestCutInCutOutAnalyzer,
)
from src.wind_turbine_analytics.data_processing.chart_builders.consecutive_hours_visualizer import (
    ConseccutiveHoursVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_processing import (
    DataProcessingStep,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.nominal_power_analyzer import (
    NominalPowerAnalyzer,
)

# Import de AutonomousOperationAnalyzer
# Note: Cet import peut causer un import circulaire si autonomous_operation.py
# importe depuis application.utils. Si c'est le cas, il faut déplacer load_data
# hors du package application.
from src.wind_turbine_analytics.data_processing.analyzer.logics.autonomous_operation import (
    AutonomousOperationAnalyzer,
)

from src.wind_turbine_analytics.data_processing.analyzer.logics.test_availability_analyzer import (
    TestAvailabilityAnalyzer,
)


class RunTestWorkflow(BaseWorkflow):
    """Coordinates data loading, criteria evaluation, charts, and report rendering."""

    def __init__(self, config: RunTestPipelineConfig, presenter) -> None:
        super().__init__(config, presenter)

    def run(self) -> None:
        self.validation_step()
        # [TODO] comptue analysis per turbine
        self.process_step()
        # [TODO] gather those information per turbine
        return

    def process_step(self) -> None:
        """Placeholder for data processing steps."""
        # [TODO] Data availability
        # [TODO] Data availability table,
        # For each row :
        # | WTG | RT Start [date] | RT End [date] | Duration [h]| Data Available (%) |

        # Criteria 1: Minimum of 120 consecutive hours
        # The WTG must be in continuous operation for a minimum of 120 consecutive hours.
        # For each row :
        # | WTG | Data hours[h] | Criterion (>=120h) [True/False] |
        consecutive_hours_results = DataProcessingStep(
            analyzer=ConsecutiveHoursAnalyzer(),
            visualizer=ConseccutiveHoursVisualizer(),
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            consecutive_hours_results, "Consecutive Hours Analysis (Criterion 1)"
        )

        # Criteria 2: 72 hours within cut-in to cut-out wind speed range (3-25 m/s)
        # 10-minute intervals with hub-height wind speed between 3 m/s and 25 m/s are counted from the SCADA file (each = 0.167 h).
        # For each row :
        # | WTG | Data hours[h] | Criterion (>=72h) [True/False] |
        test_cut_in_cut_out_results = DataProcessingStep(
            analyzer=TestCutInCutOutAnalyzer(),
            visualizer=None,  # [TODO] create visualizer for this analyzer
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            test_cut_in_cut_out_results, "Test Cut-In/Cut-Out Analysis (Criterion 2)"
        )

        # Criteria 3: 3 hours at or above 98% of nominal power
        # SCADA records with active power >= 3704.4 kW are counted and converted to hours (each 10-min record = 0.167 h).
        # For each row :
        # | WTG | Data hours[h] | Criterion (>=3h) and P>= 98% of P_nominal [True/False] |
        nominal_power_result = DataProcessingStep(
            analyzer=NominalPowerAnalyzer(),
            visualizer=None,  # [TODO] create visualizer for this analyzer
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            nominal_power_result, "Nominal Power Analysis (Criterion 3)"
        )

        # [TODO] Criteria 4 :  Local acknowledgements / restarts (<=3)
        # The number of local acknowledgements and restarts during the RT must be less than or equal to 3.
        # Local acknowledgements are identified from unauthorised stop codes in the alarm log (FM3, FM300, FM615, FM954, FE1613, FE1208)
        # For each row :
        # | WTG | Local Acknowledgements / Restarts | Criterion (<=3) [True/False] |
        autonomous_operation_result = DataProcessingStep(
            analyzer=AutonomousOperationAnalyzer(),
            visualizer=None,  # [TODO] create visualizer for this analyzer
        ).execute(self.turbine_sources, self.validation_criteria)

        self._presenter.show_analysis_result(
            autonomous_operation_result, "Autonomous Operation Analysis (Criterion 4)"
        )
        # [TODO] Criteria 5 :  Availability (>=92%)
        # Local acknowledgements are identified from unauthorised stop codes in the alarm log (FM3, FM300, FM615, FM954, FE1613, FE1208)
        # For each row :
        # | WTG | Availability (%) | WTG OK [h] | Warning [h] | Criterion (>=92%) [True/False] |
        availability_result = DataProcessingStep(
            analyzer=TestAvailabilityAnalyzer(),
            visualizer=None,  # [TODO] create visualizer for this analyzer
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            availability_result, "Availability Analysis (Criterion 5)"
        )


def run_runtest_pipeline(config: RunTestPipelineConfig, presenter) -> Any:
    return RunTestWorkflow(config=config, presenter=presenter).run()
