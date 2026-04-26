"""
Exemple d'utilisation de l'AutonomousOperationAnalyzer.

Vérifie l'autonomie d'exploitation des turbines E1, E6, E8.
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.data_processing.analyzer.logics.autonomous_operation import (
    AutonomousOperationAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineLogMapping,
    ValidationCriteria,
    Criterion,
)
from src.wind_turbine_analytics.application.utils.load_data import load_csv
from src.logger_config import get_logger

logger = get_logger(__name__)


def main():
    """Test l'analyseur d'autonomie d'exploitation sur les 3 turbines."""

    turbines_data = {
        "E1": {
            "operation_path": "./experiments/real_run_test/DATA/E1/tenMinTimeSeries-01WEA95986-Mean-1260206141902.csv",
            "log_path": "./experiments/real_run_test/DATA/E1/alarmLog-01WEA95986-1260206141836.csv",
            "power_col": "01WEA95986 GRD ActivePower",
            "wind_col": "01WEA95986 MET Wind Speed",
        },
        "E6": {
            "operation_path": "./experiments/real_run_test/DATA/E6/tenMinTimeSeries-06WEA95990-Mean-1260206142342.csv",
            "log_path": "./experiments/real_run_test/DATA/E6/alarmLog-06WEA95990-1260206135808.csv",
            "power_col": "06WEA95990 GRD ActivePower",
            "wind_col": "06WEA95990 MET Wind Speed",
        },
        "E8": {
            "operation_path": "./experiments/real_run_test/DATA/E8/tenMinTimeSeries-08WEA95991-Mean-1260206142403.csv",
            "log_path": "./experiments/real_run_test/DATA/E8/alarmLog-08WEA95991-1260206133630.csv",
            "power_col": "08WEA95991 GRD ActivePower",
            "wind_col": "08WEA95991 MET Wind Speed",
        },
    }

    analyzer = AutonomousOperationAnalyzer()
    validation_criteria = ValidationCriteria(
        validation_criterion={
            "local_restarts": Criterion(
                value=3,
                unit="nb",
                specification=None,
                description="Nombre maximal de redémarrages manuels autorisés",
            )
        }
    )

    logger.info("=" * 80)
    logger.info("TEST - Autonomie d'exploitation des turbines")
    logger.info("=" * 80)

    results = {}

    for turbine_id, turbine_data in turbines_data.items():
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Turbine: {turbine_id}")
        logger.info(f"{'=' * 60}")

        config = TurbineConfig(
            turbine_id=turbine_id,
            general_information=TurbineGeneralInformation(
                model="Nordex N131 - 3.78MW",
                nominal_power=3.78,
                constructor="Nordex",
                path_operation_data=turbine_data["operation_path"],
                path_log_data=turbine_data["log_path"],
            ),
            mapping_operation_data=TurbineMappingOperationData(
                timestamp="Date",
                wind_speed=turbine_data["wind_col"],
                activation_power=turbine_data["power_col"],
            ),
            mapping_log_data=TurbineLogMapping(
                start_date=["date", "time"],
                end_date=["date", "time"],
                name="oper",
                oper="name",
                status="status",
            ),
            test_start="01.02.2026 00:00:00",
            test_end="05.02.2026 23:50:00",
        )

        # Charger les données d'opération
        operation_data = load_csv(turbine_data["operation_path"])

        # Exécuter l'analyse
        result = analyzer._compute(
            operation_data=operation_data,
            turbine_config=config,
            criteria=validation_criteria,
        )

        results[turbine_id] = result

    # Afficher le résumé
    logger.info("\n" + "=" * 80)
    logger.info("RÉSUMÉ - Autonomie d'exploitation")
    logger.info("=" * 80)

    all_passed = True

    for turbine_id, result in results.items():
        status_icon = "✅" if result["criterion_met"] else "❌"

        logger.info(f"\n{turbine_id}: {status_icon}")
        logger.info(f"  Redémarrages manuels: {result['manual_restart_count']}")
        logger.info(f"  Seuil maximal: {result['required_threshold']}")
        logger.info(f"  Critère validé: {result['criterion_met']}")

        if result["manual_restart_events"]:
            logger.warning(f"  Événements détectés:")
            for event in result["manual_restart_events"]:
                logger.warning(
                    f"    - {event['timestamp']}: {event['code']} ({event['name']})"
                )

        if not result["criterion_met"]:
            all_passed = False

    logger.info("\n" + "=" * 80)
    if all_passed:
        logger.info("✅ TOUTES LES TURBINES PASSENT LE CRITÈRE D'AUTONOMIE")
    else:
        logger.error("❌ CERTAINES TURBINES NE PASSENT PAS LE CRITÈRE")
    logger.info("=" * 80)

    # Vérification selon les attentes du client
    logger.info("\n" + "=" * 80)
    logger.info("VÉRIFICATION selon les données du client")
    logger.info("=" * 80)

    client_expectations = {
        "E1": 0,  # Code requiring local repair/manual_start: NONE
        "E6": 0,  # Code requiring local repair/manual_start: NONE
        "E8": 0,  # Code requiring local repair/manual_start: NONE
    }

    for turbine_id, expected_count in client_expectations.items():
        actual_count = results[turbine_id]["manual_restart_count"]
        matches = actual_count == expected_count

        if matches:
            logger.info(
                f"✅ {turbine_id}: {actual_count} redémarrages (attendu: {expected_count})"
            )
        else:
            logger.error(
                f"❌ {turbine_id}: {actual_count} redémarrages (attendu: {expected_count})"
            )


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
