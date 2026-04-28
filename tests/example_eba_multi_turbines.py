"""
Exemple : Visualisation EBA avec plusieurs turbines.

Démontre le grid layout avec 3 turbines LU09, LU10, LU11.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger_config import get_logger
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_cut_in_cut_out_analyzer import (
    EbACutInCutOutAnalyzer,
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
                project_root / "experiments" / "scada_analyse" / "DATA" / turbine_id / f"WTG_{turbine_id}.csv"
            ),
            path_log_data=str(
                project_root / "experiments" / "scada_analyse" / "DATA" / turbine_id / f"WTG_message_{turbine_id}.csv"
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
    """Exemple avec 3 turbines."""

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    logger.info("=" * 80)
    logger.info("EXEMPLE : EBA Multi-Turbines (Grid Layout)")
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

    # Analyser
    logger.info(f"\nAnalyse de {len(turbine_ids)} turbines...")
    analyzer = EbACutInCutOutAnalyzer()
    results = analyzer.analyze(turbine_farm, criteria)

    # Afficher résumé
    logger.info("\n" + "=" * 80)
    logger.info("RESULTATS")
    logger.info("=" * 80)

    for turbine_id, result in results.detailed_results.items():
        if "error" not in result:
            perf = result.get("performance", 0)
            months = len(result.get("monthly_performance", []))
            logger.info(
                f"{turbine_id}: {perf:.2f}% sur {months} mois"
            )

    # Visualiser
    logger.info("\n" + "=" * 80)
    logger.info("GENERATION DE LA VISUALISATION")
    logger.info("=" * 80)

    visualizer = EbaCutInCutOutVisualizer()
    output_paths = visualizer.generate(results)

    logger.info(f"\nFichiers generes:")
    logger.info(f"  PNG: {output_paths['png_path']}")
    logger.info(f"  JSON: {output_paths['json_path']}")

    # Vérifier taille
    png_path = Path(output_paths["png_path"])
    if png_path.exists():
        size_kb = png_path.stat().st_size / 1024
        logger.info(f"\n✓ PNG genere: {size_kb:.1f} KB")
        logger.info(f"  Ouvrir avec: {png_path.absolute()}")

    logger.info("\n" + "=" * 80)
    logger.info("TERMINE - Grid layout avec 3 turbines genere !")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
