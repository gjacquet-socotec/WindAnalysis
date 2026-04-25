"""
Test rapide pour E6
"""

import sys
from pathlib import Path

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
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("TEST : E6 avec nouveau path_log_data corrige")
    print("=" * 80)
    print()

    # Configuration E6
    turbine_config = TurbineConfig(
        turbine_id="E6",
        general_information=TurbineGeneralInformation(
            model="Nordex N131 – 3.78MW",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data=(
                "experiments/real_run_test/DATA/E6/"
                "tenMinTimeSeries-06WEA95990-Mean-1260206142342.csv"
            ),
            path_log_data=(
                "experiments/real_run_test/DATA/E6/"
                "alarmLog-06WEA95990-1260206135808.csv"
            ),
        ),
        mapping_operation_data=TurbineMappingOperationData(
            timestamp="Date",
            wind_speed="06WEA95990 MET Wind Speed",
            activation_power="06WEA95990 GRD ActivePower",
            wind_direction="06WEA95990 MET Wind Dir",
            rpm="06WEA95990 GEN RPM Monitor",
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

    turbine_farm = TurbineFarm(farm={"E6": turbine_config})

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
    result = analysis_result.detailed_results["E6"]

    print("RESULTATS:")
    print(f"  Max duration: {result['max_net_duration_hours']}h")
    print(f"  Criterion met: {result['criterion_met']}")
    print(
        f"  Available periods: {len(result['available_periods'])}"
    )
    print(
        f"  Unavailable periods: "
        f"{len(result['unavailable_periods'])}"
    )
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
