# """RunTest application workflow."""

# from __future__ import annotations

# from pathlib import Path

from src.wind_turbine_analytics.application.configuration.config_models import (
    RunTestPipelineConfig,
)
from typing import Any
from src.wind_turbine_analytics.application.workflows.base_workflow import BaseWorkflow
from src.logger_config import get_logger
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders import (
    PowerCurveChartVisualizer,
    WindRoseChartVisualizer,
    WindHistogramChartVisualizer,
    HeatmapChartVisualizer,
    CutInCutoutTimelineVisualizer,
)

logger = get_logger(__name__)

# Imports des analyzers pour RunTest
from src.wind_turbine_analytics.data_processing.analyzer.logics import (
    ConsecutiveHoursAnalyzer,
    TestCutInCutOutAnalyzer,
    NominalPowerAnalyzer,
    AutonomousOperationAnalyzer,
    TestAvailabilityAnalyzer,
)


# Import du DataProcessingStep
from src.wind_turbine_analytics.data_processing.data_processing import (
    DataProcessingStep,
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
    CsvFilesTabler,
)
from src.wind_turbine_analytics.presentation.word_presenter import WordPresenter


class RunTestWorkflow(BaseWorkflow):
    """Coordinates data loading, criteria evaluation, charts, and report rendering."""

    def __init__(self, config: RunTestPipelineConfig, presenter) -> None:
        super().__init__(config, presenter)

    def run(self) -> None:
        self.validation_step()
        self.process_step()
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
            visualizers=None,  # TODO: implement ConsecutiveHoursVisualizer
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
            visualizers=[CutInCutoutTimelineVisualizer()],
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
            visualizers=[
                PowerCurveChartVisualizer(),
                WindRoseChartVisualizer(),
                WindHistogramChartVisualizer(),
            ],
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
            visualizers=None,
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
            visualizers=[HeatmapChartVisualizer()],
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

            # Générer le tableau des fichiers CSV utilisés
            csv_files_tabler = CsvFilesTabler()
            csv_files_data = csv_files_tabler.generate_from_turbine_farm(
                self.turbine_sources
            )
            logger.info(
                f"CSV files table generated with {len(csv_files_data.get('csv_files_table', []))} rows"
            )
            context.update(csv_files_data)

            # Préparer les métadonnées à partir de turbine_sources
            turbine_list = list(self.turbine_sources.farm.keys())

            # Récupérer test_start et test_end de la première turbine
            first_turbine_config = None
            if turbine_list:
                first_turbine_config = self.turbine_sources.farm[turbine_list[0]]

            # Extraire les valeurs des critères depuis validation_criteria
            criteria = self.validation_criteria.validation_criterion

            # Créer la liste des fichiers CSV utilisés
            csv_files_list = self._get_csv_files_list()

            metadata = {
                "test_start": (
                    first_turbine_config.test_start if first_turbine_config else "N/A"
                ),
                "test_end": (
                    first_turbine_config.test_end if first_turbine_config else "N/A"
                ),
                "turbines": turbine_list,
                # Informations sur le parc (depuis general_information)
                "park_name": (
                    self.general_information.park_name
                    if self.general_information
                    else "N/A"
                ),
                "model_wtg": (
                    self.general_information.model_wtg
                    if self.general_information
                    else "N/A"
                ),
                "nominal_power": (
                    self.general_information.nominal_power
                    if self.general_information
                    else "N/A"
                ),
                # Liste des fichiers CSV
                "csv_files": csv_files_list,
                # Valeurs des critères de validation
                "consecutive_hours_h": (
                    criteria.get("consecutive_hours").value
                    if "consecutive_hours" in criteria
                    else 120
                ),
                "cut_in_to_cut_out_h": (
                    criteria.get("cut_in_to_cut_out").value
                    if "cut_in_to_cut_out" in criteria
                    else 72
                ),
                # Cut-in/cut-out vitesses min/max depuis specification
                "cut_in_v_min": (
                    criteria.get("cut_in_to_cut_out").specification[0]
                    if "cut_in_to_cut_out" in criteria
                    and criteria.get("cut_in_to_cut_out").specification
                    else 3
                ),
                "cut_in_v_max": (
                    criteria.get("cut_in_to_cut_out").specification[1]
                    if "cut_in_to_cut_out" in criteria
                    and criteria.get("cut_in_to_cut_out").specification
                    else 25
                ),
                "nominal_power_h": (
                    criteria.get("nominal_power_hours").value
                    if "nominal_power_hours" in criteria
                    else 3
                ),
                "nominal_power_pct": (
                    criteria.get("nominal_power_hours").specification
                    if "nominal_power_hours" in criteria
                    else 97
                ),
                "local_restarts_max": (
                    criteria.get("local_restarts").value
                    if "local_restarts" in criteria
                    else 3
                ),
                "availability_min_pct": (
                    criteria.get("availability").value
                    if "availability" in criteria
                    else 92
                ),
            }

            # Rendre le rapport Word
            # Le template optimisé sera créé automatiquement s'il n'existe pas
            presenter = WordPresenter(
                template_path=self._config.template_path,
                output_path=self._config.output_path,
                auto_create_template=False,
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

    def _get_csv_files_list(self) -> list:
        """
        Récupère la liste des fichiers CSV utilisés pour l'analyse.

        Returns:
            Liste de dictionnaires avec les informations des fichiers
            Format: [{'turbine': 'E1', 'type': 'Operation', 'filename': 'xxx.csv'}, ...]
        """
        from pathlib import Path

        files_list = []

        for turbine_id, turbine_config in self.turbine_sources.farm.items():
            # Fichier de données d'opération
            if (
                turbine_config.general_information
                and turbine_config.general_information.path_operation_data
            ):
                operation_path = Path(
                    turbine_config.general_information.path_operation_data
                )
                files_list.append(
                    {
                        "turbine": turbine_id,
                        "type": "Données SCADA",
                        "filename": operation_path.name,
                    }
                )

            # Fichier de logs
            if (
                turbine_config.general_information
                and turbine_config.general_information.path_log_data
            ):
                log_path = Path(turbine_config.general_information.path_log_data)
                files_list.append(
                    {
                        "turbine": turbine_id,
                        "type": "Logs alarmes",
                        "filename": log_path.name,
                    }
                )

        return files_list


def run_runtest_pipeline(config: RunTestPipelineConfig, presenter) -> Any:
    return RunTestWorkflow(config=config, presenter=presenter).run()
