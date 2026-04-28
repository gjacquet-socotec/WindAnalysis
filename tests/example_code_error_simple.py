"""
Exemple simple d'utilisation du CodeErrorAnalyzer.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger_config import get_logger
from src.wind_turbine_analytics.data_processing.analyzer.logics.code_error_analyzer import CodeErrorAnalyzer
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineLogMapping,
    ValidationCriteria,
    Criterion,
    TurbineFarm,
)
import json

logger = get_logger(__name__)


def main():
    """Exemple simple d'analyse de codes d'erreur."""

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    logger.info("Démonstration du CodeErrorAnalyzer")
    logger.info("=" * 80)

    # Configuration manuelle d'une turbine (ou charger depuis YAML)
    turbine_config = TurbineConfig(
        turbine_id="LU09",
        general_information=TurbineGeneralInformation(
            model="Nordex N131 - 3.78MW",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data=str(project_root / "experiments" / "scada_analyse" / "DATA" / "LU09" / "WTG_LU09.csv"),
            path_log_data=str(project_root / "experiments" / "scada_analyse" / "DATA" / "LU09" / "WTG_message_LU09.csv"),
        ),
        mapping_operation_data=TurbineMappingOperationData(
            timestamp="date",
            wind_speed="Wind [m/s]",
            activation_power="Power [kW]",
        ),
        mapping_log_data=TurbineLogMapping(
            start_date="Start date",
            end_date="End date",
            oper="Error number",
            name="Code",
            status="Main status",
        ),
        test_start="01/04/2024 00:00:00",
        test_end="03/12/2025 11:35:00",
    )

    # Créer un TurbineFarm avec une seule turbine
    turbine_farm = TurbineFarm(
        farm={"LU09": turbine_config}
    )

    # Critères de validation
    criteria = ValidationCriteria(
        validation_criterion={
            "consecutive_hours": Criterion(value=120, unit="h"),
        }
    )

    # Analyser
    logger.info("Analyse des codes d'erreur en cours...")
    analyzer = CodeErrorAnalyzer()
    results = analyzer.analyze(turbine_farm, criteria)

    # Afficher les résultats
    for turbine_id, result in results.detailed_results.items():
        logger.info(f"\n{'='*70}")
        logger.info(f"TURBINE: {turbine_id}")
        logger.info(f"{'='*70}")

        if "error" in result:
            logger.warning(f"Erreur: {result['error']}")
            continue

        summary = result["summary"]
        logger.info(f"\nRESUME:")
        logger.info(f"  Total evenements: {summary['total_error_events']}")
        logger.info(f"  Codes uniques: {summary['unique_error_codes']}")
        logger.info(f"  Periode test: {summary['test_period_hours']:.2f}h")

        logger.info(f"\nTOP 5 CODES:")
        for i, code in enumerate(result["code_frequency"][:5], 1):
            logger.info(
                f"  {i}. {code['code']}: {code['count']} fois "
                f"({code['frequency_percent']}%) - {code['criticality']}"
            )

        logger.info(f"\nIMPACT PRODUCTION:")
        impact = result["production_impact"]
        logger.info(
            f"  Perte estimee: {impact['production_loss_percent']:.2f}%"
        )
        logger.info(
            f"  Puissance moyenne sans erreurs: "
            f"{impact['mean_power_without_errors_kW']:.2f} kW"
        )
        logger.info(
            f"  Puissance moyenne avec erreurs: "
            f"{impact['mean_power_with_errors_kW']:.2f} kW"
        )

        # Sauvegarder
        output_dir = project_root / "output" / "code_error_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{turbine_id}_analysis.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"\nResultats sauvegardes: {output_file}")

    logger.info(f"\n{'='*70}")
    logger.info("Analyse terminee!")


if __name__ == "__main__":
    main()
