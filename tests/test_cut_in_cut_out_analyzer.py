"""
Test de TestCutInCutOutAnalyzer avec fichiers réels E1
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.application.utils.load_data import load_csv
from src.wind_turbine_analytics.data_processing.analyzer.logics.test_cut_in_cut_out_analyzer import (
    TestCutInCutOutAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineLogMapping,
    ValidationCriteria,
    Criterion,
    TurbineFarm,
)


def main():
    # Configuration encodage Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("TEST : TestCutInCutOutAnalyzer avec données réelles E1")
    print("=" * 80)
    print()

    # Chemins des fichiers
    operation_file = (
        "experiments/real_run_test/DATA/E1/"
        "tenMinTimeSeries-01WEA95986-Mean-1260206142049.csv"
    )
    log_file = (
        "experiments/real_run_test/DATA/E1/"
        "alarmLog-01WEA95986-1260206141836.csv"
    )

    # Vérifier que les fichiers existent
    operation_data = load_csv(operation_file)
    print(f"✅ Données opérationnelles: {operation_data.shape}")
    print(f"   Colonnes: {list(operation_data.columns[:3])}...")
    print()

    # Configuration de la turbine
    turbine_config = TurbineConfig(
        turbine_id="E1",
        general_information=TurbineGeneralInformation(
            model="Nordex N131 – 3.78MW",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data=operation_file,
            path_log_data=log_file,
        ),
        mapping_operation_data=TurbineMappingOperationData(
            timestamp="Date",
            wind_speed="01WEA95986 MET Wind Speed",
            activation_power="01WEA95986 GRD ActivePower",
            wind_direction="01WEA95986 MET Wind Dir",
            rpm="01WEA95986 GEN RPM Monitor",
        ),
        mapping_log_data=TurbineLogMapping(
            start_date=["date", "time"],
            end_date=["date", "time"],
            name="name",
            oper="oper",
            status="status",
        ),
        test_start="27.01.2026 15:30:00",
        test_end="31.01.2026 23:50:00",
    )

    # Créer une turbine farm
    turbine_farm = TurbineFarm(farm={"E1": turbine_config})

    # Critères de validation
    criteria = ValidationCriteria(
        validation_criterion={
            "cut_in_to_cut_out": Criterion(
                value=72,
                unit="h",
                specification=[3, 25],
            )
        }
    )

    # Analyser
    analyzer = TestCutInCutOutAnalyzer()
    analysis_result = analyzer.analyze(turbine_farm, criteria)
    result = analysis_result.detailed_results["E1"]

    print("=" * 80)
    print("RÉSULTATS DE L'ANALYSE")
    print("=" * 80)
    print()

    print(f"Critère requis: {result['required_hours']}h")
    print(f"Vitesse cut-in: {result['cut_in_speed']} m/s")
    print(f"Vitesse cut-out: {result['cut_out_speed']} m/s")
    print()

    print(
        f"Durée max continue (nette): "
        f"{result['max_net_duration_hours']}h"
    )
    print(f"Critère satisfait: {result['criterion_met']}")
    print()

    print("PÉRIODES DISPONIBLES (conditions OK):")
    print("-" * 80)
    if result['available_periods']:
        for i, period in enumerate(result['available_periods'], 1):
            print(f"  Période {i}:")
            print(f"    Début: {period['start']}")
            print(f"    Fin: {period['end']}")
            print(f"    Durée brute: {period['gross_duration_hours']}h")
            print(
                f"    Arrêts non autorisés: "
                f"{period['unauthorized_stop_hours']}h"
            )
            print(f"    Durée nette: {period['net_duration_hours']}h")

            # Afficher les détails des arrêts si présents
            if period.get('unauthorized_stops'):
                print("    Détails des arrêts:")
                for stop in period['unauthorized_stops']:
                    print(f"      - Code: {stop['code']}")
                    print(f"        Description: {stop['description']}")
                    print(
                        f"        Période: {stop['start']} → {stop['end']}"
                    )
                    print(f"        Durée: {stop['duration_hours']}h")
            print()
    else:
        print("  Aucune période disponible détectée")
        print()

    print("PÉRIODES INDISPONIBLES (conditions NON OK):")
    print("-" * 80)
    if result['unavailable_periods']:
        for i, period in enumerate(result['unavailable_periods'][:5], 1):
            print(f"  Période {i}:")
            print(f"    Début: {period['start']}")
            print(f"    Fin: {period['end']}")
            print(f"    Durée brute: {period['gross_duration_hours']}h")
            print(
                f"    Arrêts non autorisés: "
                f"{period['unauthorized_stop_hours']}h"
            )
            print(f"    Durée nette: {period['net_duration_hours']}h")

            # Afficher les détails des arrêts si présents
            if period.get('unauthorized_stops'):
                print("    Détails des arrêts:")
                for stop in period['unauthorized_stops']:
                    print(f"      - Code: {stop['code']}")
                    print(f"        Description: {stop['description']}")
                    print(
                        f"        Période: {stop['start']} → {stop['end']}"
                    )
                    print(f"        Durée: {stop['duration_hours']}h")
            print()
        if len(result['unavailable_periods']) > 5:
            remaining = len(result['unavailable_periods']) - 5
            print(f"  ... et {remaining} autres périodes")
            print()
    else:
        print("  Aucune période indisponible détectée")
        print()

    print("=" * 80)


if __name__ == "__main__":
    main()
