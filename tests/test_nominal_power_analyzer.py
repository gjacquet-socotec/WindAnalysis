"""
Test de NominalPowerAnalyzer
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import direct pour éviter circular import via application/__init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "nominal_power_analyzer",
    project_root
    / "src/wind_turbine_analytics/data_processing/analyzer/logics/nominal_power_analyzer.py"
)
nominal_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nominal_module)
NominalPowerAnalyzer = nominal_module.NominalPowerAnalyzer

from src.wind_turbine_analytics.application.utils.load_data import load_csv
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    ValidationCriteria,
    Criterion,
    TurbineFarm,
)


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("TEST : NominalPowerAnalyzer avec E1")
    print("=" * 80)
    print()

    # Configuration E1
    turbine_config = TurbineConfig(
        turbine_id="E1",
        general_information=TurbineGeneralInformation(
            model="Nordex N131 – 3.78MW",
            nominal_power=3.78,  # MW
            constructor="Nordex",
            path_operation_data=(
                "experiments/real_run_test/DATA/E1/"
                "tenMinTimeSeries-01WEA95986-Mean-1260206142049.csv"
            ),
        ),
        mapping_operation_data=TurbineMappingOperationData(
            timestamp="Date",
            activation_power="01WEA95986 GRD ActivePower",
        ),
        test_start="27.01.2026 15:30:00",
        test_end="31.01.2026 23:50:00",
    )

    turbine_farm = TurbineFarm(farm={"E1": turbine_config})

    # Critère: >= 98% de P_nom pendant au moins 3h
    criteria = ValidationCriteria(
        validation_criterion={
            "nominal_power_hours": Criterion(
                value=3,  # 3 heures minimum
                specification=98,  # 98% de P_nom
                unit="h",
            )
        }
    )

    # Analyser
    analyzer = NominalPowerAnalyzer()
    analysis_result = analyzer.analyze(turbine_farm, criteria)
    result = analysis_result.detailed_results["E1"]

    print("RESULTATS:")
    print("=" * 80)
    print(f"P_nom: {result['nominal_power_kW']} kW")
    print(
        f"Seuil: {result['power_threshold_percent']}% = "
        f"{result['power_threshold_kW']} kW"
    )
    print()
    print(
        f"Duree totale >= seuil: {result['total_duration_hours']}h"
    )
    print(f"Duree requise: {result['required_hours']}h")
    print(f"Critere satisfait: {result['criterion_met']}")
    print()

    print(
        f"Nombre de periodes >= seuil: "
        f"{len(result['nominal_power_periods'])}"
    )
    print()

    if result['nominal_power_periods']:
        print("Premieres periodes (max 5):")
        for i, period in enumerate(
            result['nominal_power_periods'][:5], 1
        ):
            print(f"  Periode {i}:")
            print(f"    Debut: {period['start']}")
            print(f"    Fin: {period['end']}")
            print(f"    Duree: {period['duration_hours']}h")

        if len(result['nominal_power_periods']) > 5:
            remaining = len(result['nominal_power_periods']) - 5
            print(f"  ... et {remaining} autres periodes")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
