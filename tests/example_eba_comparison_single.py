"""
Exemple simple montrant la différence entre Cut-In/Cut-Out et Manufacturer.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger_config import get_logger
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_manifacturer_analyzer import (
    EbaManufacturerAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_cut_in_cut_out_analyzer import (
    EbACutInCutOutAnalyzer,
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

logger = get_logger(__name__)


def main():
    """Exemple simple sur une turbine."""

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    logger.info("=" * 80)
    logger.info("Comparaison EBA : Cut-In/Cut-Out vs Manufacturer (LU09)")
    logger.info("=" * 80)

    # Configuration LU09
    turbine_config = TurbineConfig(
        turbine_id="LU09",
        general_information=TurbineGeneralInformation(
            model="Nordex N131 - 3.78MW",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data=str(
                project_root
                / "experiments"
                / "scada_analyse"
                / "DATA"
                / "LU09"
                / "WTG_LU09.csv"
            ),
            path_log_data=str(
                project_root
                / "experiments"
                / "scada_analyse"
                / "DATA"
                / "LU09"
                / "WTG_message_LU09.csv"
            ),
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
        test_end="31/10/2024 23:59:59",
    )

    turbine_farm = TurbineFarm(farm={"LU09": turbine_config})

    criteria = ValidationCriteria(
        validation_criterion={
            "cut_in_to_cut_out": Criterion(
                value=72, unit="h", specification=[3, 25], description="plage de vitesse"
            )
        }
    )

    # Analyse Cut-In/Cut-Out
    logger.info("\n1. EBA Cut-In/Cut-Out (exclut codes d'erreur critiques)")
    analyzer_cutout = EbACutInCutOutAnalyzer()
    results_cutout = analyzer_cutout.analyze(turbine_farm, criteria)

    cutout_result = results_cutout.detailed_results["LU09"]
    logger.info(f"\nResultat Cut-In/Cut-Out:")
    logger.info(f"  Performance: {cutout_result['performance']:.2f}%")
    logger.info(f"  Energie reelle: {cutout_result['total_real_energy']:,.0f} kWh")
    logger.info(f"  Energie theorique: {cutout_result['total_theoretical_energy']:,.0f} kWh")
    logger.info(f"  Pertes: {cutout_result['total_loss_energy']:,.0f} kWh")

    # Analyse Manufacturer
    logger.info("\n" + "-" * 80)
    logger.info("2. EBA Manufacturer (inclut TOUS les downtimes)")
    analyzer_manuf = EbaManufacturerAnalyzer()
    results_manuf = analyzer_manuf.analyze(turbine_farm, criteria)

    manuf_result = results_manuf.detailed_results["LU09"]
    logger.info(f"\nResultat Manufacturer:")
    logger.info(f"  Performance: {manuf_result['performance']:.2f}%")
    logger.info(f"  Energie reelle: {manuf_result['total_real_energy']:,.0f} kWh")
    logger.info(f"  Energie theorique: {manuf_result['total_theoretical_energy']:,.0f} kWh")
    logger.info(f"  Pertes: {manuf_result['total_loss_energy']:,.0f} kWh")

    # Comparaison
    logger.info("\n" + "=" * 80)
    logger.info("COMPARAISON")
    logger.info("=" * 80)

    perf_diff = cutout_result["performance"] - manuf_result["performance"]
    energy_diff = manuf_result["total_theoretical_energy"] - cutout_result["total_theoretical_energy"]
    loss_diff = manuf_result["total_loss_energy"] - cutout_result["total_loss_energy"]

    logger.info(f"\nDifference de performance: {perf_diff:+.2f} points")
    logger.info(f"  -> Cut-In/Cut-Out: {cutout_result['performance']:.2f}%")
    logger.info(f"  -> Manufacturer:   {manuf_result['performance']:.2f}%")

    logger.info(f"\nEnergie theorique additionnelle (Manufacturer):")
    logger.info(f"  {energy_diff:+,.0f} kWh")
    logger.info(f"  -> Periodes de downtime incluses dans le calcul")

    logger.info(f"\nPertes additionnelles (Manufacturer):")
    logger.info(f"  {loss_diff:+,.0f} kWh")
    logger.info(f"  -> Manque a gagner pendant les downtimes")

    logger.info("\n" + "=" * 80)
    logger.info("INTERPRETATION")
    logger.info("=" * 80)

    logger.info(f"""
L'EBA Manufacturer est plus bas car il inclut :
  - Les periodes de maintenance
  - Les pannes et arretes
  - Les problemes reseau
  - Tout downtime ou la turbine ne peut pas produire

Pendant ces periodes :
  - Energie reelle = 0 (ou tres faible)
  - Energie theorique = calculee selon le vent
  => Impact negatif sur la performance globale

Difference observee : {perf_diff:.2f} points
  => Environ {perf_diff:.1f}% de perte de performance due aux downtimes
""")

    logger.info("=" * 80)


if __name__ == "__main__":
    main()
