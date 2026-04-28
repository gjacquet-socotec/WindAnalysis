"""
Exemple d'utilisation du WindDirectionCalibrationVisualizer

Cet exemple démontre comment générer des visualisations de l'analyse
de calibration de la nacelle.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np

from src.wind_turbine_analytics.data_processing.analyzer.logics.wind_direction_calibration_analyzer import (
    WindDirectionCalibrationAnalyzer,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.wind_direction_calibration_visualizer import (
    WindDirectionCalibrationVisualizer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineFarm,
    ValidationCriteria,
    Criterion,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def create_synthetic_data_for_turbine(
    turbine_id: str, mean_offset: float, days: int = 7
):
    """
    Crée des données synthétiques pour une turbine.

    Args:
        turbine_id: Identifiant de la turbine
        mean_offset: Décalage moyen entre wind_direction et nacelle
        days: Nombre de jours de données
    """
    timestamps = pd.date_range(
        start="2024-01-01 00:00:00",
        end=f"2024-01-{days+1} 00:00:00",
        freq="h",
    )[:-1]

    hours = np.arange(len(timestamps))
    wind_direction = (180 + 120 * np.sin(hours * 2 * np.pi / 24)) % 360
    nacelle_position = (wind_direction + mean_offset) % 360
    nacelle_position += np.random.normal(0, 1, len(timestamps))
    nacelle_position = nacelle_position % 360
    wind_speed = 9 + 4 * np.sin(hours * 2 * np.pi / 48)
    active_power = np.minimum(wind_speed**3 * 15, 3780)

    operation_data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_direction": wind_direction,
            "nacelle_position": nacelle_position,
            "wind_speed": wind_speed,
            "active_power": active_power,
        }
    )

    return operation_data


def run_example():
    """Exécute l'exemple de visualisation"""

    logger.info("=" * 80)
    logger.info("Exemple de visualisation de calibration de direction du vent")
    logger.info("=" * 80)

    # Créer des données synthétiques pour 3 turbines
    # E01: Bonne calibration (3°)
    # E02: Calibration limite (5°)
    # E03: Mauvaise calibration (8°)

    turbines_data = {
        "E01": create_synthetic_data_for_turbine("E01", mean_offset=3.0, days=7),
        "E02": create_synthetic_data_for_turbine("E02", mean_offset=5.0, days=7),
        "E03": create_synthetic_data_for_turbine("E03", mean_offset=8.0, days=7),
    }

    # Configuration commune
    criteria = ValidationCriteria(
        validation_criterion={"cut_in_to_cut_out": Criterion(specification=[3.0, 25.0])}
    )

    # Analyser chaque turbine
    analyzer = WindDirectionCalibrationAnalyzer()
    detailed_results = {}

    for turbine_id, operation_data in turbines_data.items():
        logger.info(f"\nAnalyse de {turbine_id}...")

        turbine_config = TurbineConfig(
            turbine_id=turbine_id,
            test_start=pd.Timestamp("2024-01-01 00:00:00"),
            test_end=pd.Timestamp("2024-01-08 00:00:00"),
            general_information=TurbineGeneralInformation(
                model="N131",
                nominal_power=3780.0,
                constructor="Nordex",
            ),
            mapping_operation_data=TurbineMappingOperationData(
                timestamp="timestamp",
                wind_speed="wind_speed",
                wind_direction="wind_direction",
                nacelle_position="nacelle_position",
                activation_power="active_power",
            ),
        )

        log_data = pd.DataFrame()  # Pas de log pour cet exemple

        result = analyzer._compute(
            operation_data, log_data, turbine_config, criteria
        )
        detailed_results[turbine_id] = result

        logger.info(
            f"  Écart moyen: {result['overall_mean_angular_error']:.2f}°"
        )
        logger.info(f"  Critère satisfait: {result['criterion_met']}")

    # Créer l'objet AnalysisResult
    analysis_result = AnalysisResult(
        detailed_results=detailed_results,
        status="completed",
        requires_visuals=True,
    )

    # Générer la visualisation
    logger.info("\n" + "=" * 80)
    logger.info("Génération de la visualisation...")
    logger.info("=" * 80)

    visualizer = WindDirectionCalibrationVisualizer()
    output_paths = visualizer.generate(analysis_result)

    logger.info("\n--- Fichiers générés ---")
    logger.info(f"PNG: {output_paths['png_path']}")
    logger.info(f"JSON: {output_paths['json_path']}")

    logger.info("\n--- Résumé des résultats ---")
    for turbine_id, result in detailed_results.items():
        status = "✓ OK" if result["criterion_met"] else "✗ À REVOIR"
        logger.info(
            f"{turbine_id}: {status} - Écart moyen = {result['overall_mean_angular_error']:.2f}° "
            f"(seuil: {result['threshold_degrees']}°)"
        )

    logger.info("\n--- Interprétation du graphique ---")
    logger.info("Subplot supérieur (par turbine): Écart angulaire moyen journalier")
    logger.info("  - Ligne bleue: Écarts mesurés chaque jour")
    logger.info("  - Ligne rouge pointillée: Seuil acceptable (5°)")
    logger.info(
        "  - Zone verte/rouge: Indique si le critère est globalement respecté"
    )
    logger.info("")
    logger.info("Subplot inférieur (par turbine): Corrélation journalière")
    logger.info(
        "  - Ligne verte: Corrélation wind_direction vs nacelle_position"
    )
    logger.info("  - Ligne orange: Référence 0.95 (bonne corrélation)")
    logger.info("  - Plus proche de 1.0 = meilleur suivi du vent")

    logger.info("\n" + "=" * 80)
    logger.info("Exemple terminé avec succès !")
    logger.info(f"Ouvrez le fichier PNG pour voir le résultat: {output_paths['png_path']}")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Configuration de l'encodage pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    run_example()
