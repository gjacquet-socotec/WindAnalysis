"""
Exemple d'utilisation de TestAvailabilityAnalyzer.

Vérifie la disponibilité des turbines E1, E6, E8 pendant la période de test.

Résultats attendus (selon le client):
- E1 : Test duration = 120h, Tnordex stop[h] = 0h, availability 100%
- E6 : Test duration = 120h, Tnordex stop[h] = 0h, availability 100%
- E8 : Test duration = 120h, Tnordex stop[h] = 0h, availability 100%
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.data_processing.analyzer.logics.test_availability_analyzer import (
    TestAvailabilityAnalyzer,
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
    """Test l'analyseur de disponibilité sur les 3 turbines."""

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

    analyzer = TestAvailabilityAnalyzer()
    validation_criteria = ValidationCriteria(
        validation_criterion={
            "availability": Criterion(
                value=92.0,
                unit="%",
                specification=None,
                description="Seuil minimal de disponibilité",
            )
        }
    )

    logger.info("=" * 80)
    logger.info("TEST - Disponibilité des turbines")
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

        # Charger les données
        operation_data = load_csv(turbine_data["operation_path"])
        log_data = load_csv(turbine_data["log_path"])

        # Exécuter l'analyse
        result = analyzer._compute(
            operation_data=operation_data,
            log_data=log_data,
            turbine_config=config,
            criteria=validation_criteria,
        )

        results[turbine_id] = result

    # Afficher le résumé
    logger.info("\n" + "=" * 80)
    logger.info("RÉSUMÉ - Disponibilité")
    logger.info("=" * 80)

    all_passed = True

    for turbine_id, result in results.items():
        status_icon = "✅" if result["criterion_met"] else "❌"

        logger.info(f"\n{turbine_id}: {status_icon}")
        logger.info(f"  Durée totale: {result['total_hours']}h")
        logger.info(
            f"  Arrêts non autorisés: {result['unauthorized_downtime_hours']}h"
        )
        logger.info(f"  Disponibilité: {result['availability_percent']}%")
        logger.info(f"  Seuil: >={result['required_threshold']}%")
        logger.info(f"  Critère validé: {result['criterion_met']}")

        if result["unauthorized_events"]:
            logger.warning(f"  Événements d'arrêt détectés:")
            for event in result["unauthorized_events"]:
                logger.warning(
                    f"    - {event['start']} → {event['end']}: "
                    f"{event['duration_hours']}h ({event['codes']})"
                )

        if not result["criterion_met"]:
            all_passed = False

    # Vérification selon les attentes du client
    logger.info("\n" + "=" * 80)
    logger.info("VÉRIFICATION selon les données du client")
    logger.info("=" * 80)

    client_expectations = {
        "E1": {"duration": 120.0, "downtime": 0.0, "availability": 100.0},
        "E6": {"duration": 120.0, "downtime": 0.0, "availability": 100.0},
        "E8": {"duration": 120.0, "downtime": 0.0, "availability": 100.0},
    }

    all_match = True

    for turbine_id, expected in client_expectations.items():
        result = results[turbine_id]

        # Tolérance de 0.2h pour la durée (119.83h attendu vs 120h client)
        duration_ok = abs(result["total_hours"] - expected["duration"]) <= 0.2
        downtime_ok = result["unauthorized_downtime_hours"] == expected["downtime"]
        availability_ok = result["availability_percent"] == expected["availability"]

        if duration_ok and downtime_ok and availability_ok:
            logger.info(
                f"✅ {turbine_id}: "
                f"{result['availability_percent']}% "
                f"(attendu: {expected['availability']}%)"
            )
        else:
            logger.error(
                f"❌ {turbine_id}: "
                f"{result['availability_percent']}% "
                f"(attendu: {expected['availability']}%)"
            )
            if not duration_ok:
                logger.error(
                    f"   Durée: {result['total_hours']}h vs {expected['duration']}h"
                )
            if not downtime_ok:
                logger.error(
                    f"   Arrêts: {result['unauthorized_downtime_hours']}h "
                    f"vs {expected['downtime']}h"
                )
            all_match = False

    logger.info("\n" + "=" * 80)
    if all_passed and all_match:
        logger.info("✅ TOUTES LES TURBINES PASSENT LE CRITÈRE DE DISPONIBILITÉ")
        logger.info("✅ RÉSULTATS CONFORMES AUX ATTENTES DU CLIENT")
    else:
        if not all_passed:
            logger.error("❌ CERTAINES TURBINES NE PASSENT PAS LE CRITÈRE")
        if not all_match:
            logger.error("❌ RÉSULTATS DIFFÉRENTS DES ATTENTES DU CLIENT")
    logger.info("=" * 80)


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
