"""
Exemple d'utilisation du EbaManufacturerVisualizer.

Compare l'EBA avec filtrage (Cut-In/Cut-Out) vs sans filtrage (Manufacturer).
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
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_manifacturer_visualizer import (
    EbaManufacturerVisualizer,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_cut_in_cut_out_visualizer import (
    EbaCutInCutOutVisualizer,
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


def create_turbine_config(turbine_id: str) -> TurbineConfig:
    """Crée une configuration pour une turbine donnée."""
    return TurbineConfig(
        turbine_id=turbine_id,
        general_information=TurbineGeneralInformation(
            model="Nordex N131 - 3.78MW",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data=str(
                project_root
                / "experiments"
                / "scada_analyse"
                / "DATA"
                / turbine_id
                / f"WTG_{turbine_id}.csv"
            ),
            path_log_data=str(
                project_root
                / "experiments"
                / "scada_analyse"
                / "DATA"
                / turbine_id
                / f"WTG_message_{turbine_id}.csv"
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
        test_end="31/10/2024 23:59:59",  # 7 mois
    )


def main():
    """Exemple comparatif : EBA avec et sans filtrage."""

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    logger.info("=" * 80)
    logger.info("EXEMPLE : Comparaison EBA Cut-In/Cut-Out vs Manufacturer")
    logger.info("=" * 80)

    # Créer les configurations pour 3 turbines
    turbine_ids = ["LU09", "LU10", "LU11"]
    farm = {tid: create_turbine_config(tid) for tid in turbine_ids}
    turbine_farm = TurbineFarm(farm=farm)

    # Critères
    criteria = ValidationCriteria(
        validation_criterion={
            "cut_in_to_cut_out": Criterion(
                value=72,
                unit="h",
                specification=[3, 25],
                description="plage de vitesse",
            )
        }
    )

    # ANALYSE 1 : EBA avec filtrage (Cut-In/Cut-Out)
    logger.info("\n" + "=" * 80)
    logger.info("ANALYSE 1 : EBA Cut-In/Cut-Out (avec filtrage des erreurs)")
    logger.info("=" * 80)

    analyzer_cutout = EbACutInCutOutAnalyzer()
    results_cutout = analyzer_cutout.analyze(turbine_farm, criteria)

    logger.info("\nPerformances Cut-In/Cut-Out:")
    for turbine_id, result in results_cutout.detailed_results.items():
        if "error" not in result:
            perf = result.get("performance", 0)
            logger.info(f"  {turbine_id}: {perf:.2f}%")

    # ANALYSE 2 : EBA Manufacturer (sans filtrage)
    logger.info("\n" + "=" * 80)
    logger.info("ANALYSE 2 : EBA Manufacturer (SANS filtrage, tous downtimes inclus)")
    logger.info("=" * 80)

    analyzer_manuf = EbaManufacturerAnalyzer()
    results_manuf = analyzer_manuf.analyze(turbine_farm, criteria)

    logger.info("\nPerformances Manufacturer:")
    for turbine_id, result in results_manuf.detailed_results.items():
        if "error" not in result:
            perf = result.get("performance", 0)
            logger.info(f"  {turbine_id}: {perf:.2f}%")

    # COMPARAISON
    logger.info("\n" + "=" * 80)
    logger.info("COMPARAISON DES PERFORMANCES")
    logger.info("=" * 80)

    for turbine_id in turbine_ids:
        perf_cutout = results_cutout.detailed_results[turbine_id].get("performance", 0)
        perf_manuf = results_manuf.detailed_results[turbine_id].get("performance", 0)
        diff = perf_cutout - perf_manuf

        logger.info(f"\n{turbine_id}:")
        logger.info(f"  Cut-In/Cut-Out: {perf_cutout:.2f}%")
        logger.info(f"  Manufacturer:   {perf_manuf:.2f}%")
        logger.info(f"  Difference:     {diff:+.2f}%")
        logger.info(
            f"  -> Impact des downtimes: "
            f"{diff:.2f} points de pourcentage"
        )

    # VISUALISATIONS
    logger.info("\n" + "=" * 80)
    logger.info("GENERATION DES VISUALISATIONS")
    logger.info("=" * 80)

    # Visualisation Cut-In/Cut-Out
    logger.info("\n1. Graphique EBA Cut-In/Cut-Out...")
    viz_cutout = EbaCutInCutOutVisualizer()
    paths_cutout = viz_cutout.generate(results_cutout)
    logger.info(f"   PNG: {paths_cutout['png_path']}")
    logger.info(f"   JSON: {paths_cutout['json_path']}")

    # Visualisation Manufacturer
    logger.info("\n2. Graphique EBA Manufacturer...")
    viz_manuf = EbaManufacturerVisualizer()
    paths_manuf = viz_manuf.generate(results_manuf)
    logger.info(f"   PNG: {paths_manuf['png_path']}")
    logger.info(f"   JSON: {paths_manuf['json_path']}")

    # Résumé
    logger.info("\n" + "=" * 80)
    logger.info("RESUME")
    logger.info("=" * 80)

    png_cutout = Path(paths_cutout["png_path"])
    png_manuf = Path(paths_manuf["png_path"])

    if png_cutout.exists() and png_manuf.exists():
        size_cutout = png_cutout.stat().st_size / 1024
        size_manuf = png_manuf.stat().st_size / 1024

        logger.info(f"\nFichiers generes:")
        logger.info(f"  1. EBA Cut-In/Cut-Out: {size_cutout:.1f} KB")
        logger.info(f"     {png_cutout.absolute()}")
        logger.info(f"\n  2. EBA Manufacturer: {size_manuf:.1f} KB")
        logger.info(f"     {png_manuf.absolute()}")

        logger.info(f"\nDifference cle:")
        logger.info(
            f"  - Cut-In/Cut-Out: EXCLUT les periodes avec codes d'erreur critiques"
        )
        logger.info(
            f"  - Manufacturer: INCLUT TOUS les downtimes (maintenance, pannes, reseau)"
        )
        logger.info(
            f"  => Les performances Manufacturer sont donc generalement plus basses"
        )

    logger.info("\n" + "=" * 80)
    logger.info("EXEMPLE TERMINE AVEC SUCCES !")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
