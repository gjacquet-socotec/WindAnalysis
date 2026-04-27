# """RunTest application workflow."""

# from __future__ import annotations

# from pathlib import Path

from src.wind_turbine_analytics.application.configuration.config_models import (
    RunTestPipelineConfig,
)
from typing import Any
from src.wind_turbine_analytics.application.workflows.base_workflow import BaseWorkflow
from src.logger_config import get_logger

logger = get_logger(__name__)
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

# Imports des tablers pour génération de rapports Word
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest import (
    ConsecutiveHoursTabler,
    CutInCutOutTabler,
    NominalPowerValuesTabler,
    NominalPowerDurationTabler,
    AutonomousOperationTabler,
    AvailabilityTabler,
    RunTestSummaryTabler,
)
from src.wind_turbine_analytics.presentation.word_presenter import WordPresenter


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
        """Traite toutes les analyses et génère le rapport Word si activé."""
        # Créer un summary_tabler pour agréger tous les résultats
        summary_tabler = RunTestSummaryTabler()

        # Stocker tous les résultats pour génération du rapport
        all_results = {}

        # Criteria 1: Minimum of 120 consecutive hours
        consecutive_hours_results = DataProcessingStep(
            analyzer=ConsecutiveHoursAnalyzer(),
            visualizer=ConseccutiveHoursVisualizer(),
            tabler=ConsecutiveHoursTabler(),
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            consecutive_hours_results, "Consecutive Hours Analysis (Criterion 1)"
        )
        all_results["consecutive_hours"] = consecutive_hours_results
        summary_tabler.add_analysis_result(
            "consecutive_hours", consecutive_hours_results
        )

        # Criteria 2: 72 hours within cut-in to cut-out wind speed range
        test_cut_in_cut_out_results = DataProcessingStep(
            analyzer=TestCutInCutOutAnalyzer(),
            visualizer=None,
            tabler=CutInCutOutTabler(),
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            test_cut_in_cut_out_results, "Test Cut-In/Cut-Out Analysis (Criterion 2)"
        )
        all_results["cut_in_cut_out"] = test_cut_in_cut_out_results
        summary_tabler.add_analysis_result(
            "cut_in_cut_out", test_cut_in_cut_out_results
        )

        # Criteria 3: 3 hours at or above 98% of nominal power
        # Note: 2 tableaux pour ce critère (valeurs + durée)
        nominal_power_result = DataProcessingStep(
            analyzer=NominalPowerAnalyzer(),
            visualizer=None,
            tabler=[NominalPowerValuesTabler(), NominalPowerDurationTabler()],
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            nominal_power_result, "Nominal Power Analysis (Criterion 3)"
        )
        all_results["nominal_power"] = nominal_power_result
        summary_tabler.add_analysis_result("nominal_power", nominal_power_result)

        # Criteria 4: Local acknowledgements / restarts (<=3)
        autonomous_operation_result = DataProcessingStep(
            analyzer=AutonomousOperationAnalyzer(),
            visualizer=None,
            tabler=AutonomousOperationTabler(),
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            autonomous_operation_result, "Autonomous Operation Analysis (Criterion 4)"
        )
        all_results["autonomous_operation"] = autonomous_operation_result
        summary_tabler.add_analysis_result(
            "autonomous_operation", autonomous_operation_result
        )

        # Criteria 5: Availability (>=92%)
        availability_result = DataProcessingStep(
            analyzer=TestAvailabilityAnalyzer(),
            visualizer=None,
            tabler=AvailabilityTabler(),
        ).execute(self.turbine_sources, self.validation_criteria)
        self._presenter.show_analysis_result(
            availability_result, "Availability Analysis (Criterion 5)"
        )
        all_results["availability"] = availability_result
        summary_tabler.add_analysis_result("availability", availability_result)

        # Générer le rapport Word si activé dans la config
        self._render_report(all_results, summary_tabler)

    def _render_report(
        self, all_results: dict, summary_tabler: RunTestSummaryTabler
    ) -> None:
        """
        Génère le rapport Word si activé dans la config.

        Args:
            all_results: Dict des résultats d'analyse par critère
            summary_tabler: Tableau récapitulatif avec tous les résultats accumulés
        """
        if not self._config.render_template:
            logger.info("Template rendering disabled in config (render_template=False)")
            return

        logger.info("Rendering Word report...")

        try:
            # Agréger toutes les table_data des résultats
            context = {}
            for analysis_name, result in all_results.items():
                if result.metadata and "table_data" in result.metadata:
                    context.update(result.metadata["table_data"])

            # Générer le tableau récapitulatif et l'ajouter au contexte
            summary_data = summary_tabler.generate()
            context.update(summary_data)

            # Préparer les métadonnées à partir de turbine_sources
            turbine_list = list(self.turbine_sources.farm.keys())

            # Récupérer test_start et test_end de la première turbine
            first_turbine_config = None
            if turbine_list:
                first_turbine_config = self.turbine_sources.farm[turbine_list[0]]

            metadata = {
                "test_start": (
                    first_turbine_config.test_start if first_turbine_config else "N/A"
                ),
                "test_end": (
                    first_turbine_config.test_end if first_turbine_config else "N/A"
                ),
                "turbines": turbine_list,
            }

            # Rendre le rapport Word
            presenter = WordPresenter(
                template_path=self._config.template_path,
                output_path=self._config.output_path,
            )
            presenter.render_report(context, metadata=metadata)

        except FileNotFoundError as e:
            logger.error(f"Template file not found: {e}")
            logger.info(
                "Please create a Word template with docxtpl tags at: "
                f"{self._config.template_path}"
            )
        except Exception as e:
            logger.error(f"Failed to render Word report: {e}")


def run_runtest_pipeline(config: RunTestPipelineConfig, presenter) -> Any:
    return RunTestWorkflow(config=config, presenter=presenter).run()
