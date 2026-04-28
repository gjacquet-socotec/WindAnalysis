"""
Exemple d'utilisation du EbaCutInCutOutVisualizer.

Ce script illustre comment générer le graphique de disponibilité énergétique
à partir des résultats de l'analyseur EBA.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
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


def main():
    """Exemple complet : analyse + visualisation EBA."""

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    logger.info("=" * 80)
    logger.info("EXEMPLE : Visualisation EBA Cut-In to Cut-Out")
    logger.info("=" * 80)

    # Configuration d'une turbine
    turbine_config = TurbineConfig(
        turbine_id="LU09",
        general_information=TurbineGeneralInformation(
            model="Nordex N131 - 3.78MW",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data=str(
                project_root / "experiments" / "scada_analyse" / "DATA" / "LU09" / "WTG_LU09.csv"
            ),
            path_log_data=str(
                project_root / "experiments" / "scada_analyse" / "DATA" / "LU09" / "WTG_message_LU09.csv"
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
        test_end="31/12/2024 23:59:59",  # Période d'un an pour avoir plusieurs mois
    )

    # Créer un TurbineFarm
    turbine_farm = TurbineFarm(farm={"LU09": turbine_config})

    # Critères de validation
    criteria = ValidationCriteria(
        validation_criterion={
            "cut_in_to_cut_out": Criterion(
                value=72,
                unit="h",
                specification=[3, 25],  # Plage de vent 3-25 m/s
                description="plage de vitesse",
            )
        }
    )

    # ÉTAPE 1 : Analyser avec EbACutInCutOutAnalyzer
    logger.info("\nETAPE 1 : Analyse EBA en cours...")
    analyzer = EbACutInCutOutAnalyzer()
    results = analyzer.analyze(turbine_farm, criteria)

    # Afficher les résultats
    for turbine_id, result in results.detailed_results.items():
        logger.info(f"\nRESULTATS pour {turbine_id}:")
        logger.info(f"  - Performance globale: {result.get('performance', 0):.2f}%")
        logger.info(f"  - Energie reelle: {result.get('total_real_energy', 0):.2f} kWh")
        logger.info(
            f"  - Energie theorique: {result.get('total_theoretical_energy', 0):.2f} kWh"
        )

        monthly = result.get("monthly_performance", [])
        logger.info(f"  - Nombre de mois analyses: {len(monthly)}")

        if monthly:
            logger.info("\n  Performances mensuelles:")
            for month_data in monthly[:5]:  # Afficher les 5 premiers mois
                logger.info(
                    f"    {month_data['month']}: {month_data['performance']:.2f}%"
                )

    # ÉTAPE 2 : Générer la visualisation
    logger.info("\n" + "=" * 80)
    logger.info("ETAPE 2 : Generation de la visualisation...")

    visualizer = EbaCutInCutOutVisualizer()
    output_paths = visualizer.generate(results)

    logger.info(f"\nFichiers generes:")
    logger.info(f"  - PNG: {output_paths['png_path']}")
    logger.info(f"  - JSON: {output_paths['json_path']}")

    # Vérifier que les fichiers existent
    png_path = Path(output_paths["png_path"])
    json_path = Path(output_paths["json_path"])

    if png_path.exists():
        logger.info(f"\n✓ PNG genere avec succes ({png_path.stat().st_size} bytes)")
    else:
        logger.error(f"\n✗ Erreur: PNG non genere")

    if json_path.exists():
        logger.info(f"✓ JSON genere avec succes ({json_path.stat().st_size} bytes)")
        logger.info("  (Ce fichier JSON peut etre utilise pour un dashboard web)")
    else:
        logger.error(f"✗ Erreur: JSON non genere")

    # Afficher les métadonnées
    if results.metadata and "charts" in results.metadata:
        logger.info(f"\nMetadonnees stockees dans result.metadata:")
        for chart_name, chart_info in results.metadata["charts"].items():
            logger.info(f"  - {chart_name}:")
            for key, value in chart_info.items():
                logger.info(f"    {key}: {value}")

    logger.info("\n" + "=" * 80)
    logger.info("EXEMPLE TERMINE AVEC SUCCES !")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
