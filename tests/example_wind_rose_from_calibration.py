"""
Exemple montrant que WindRoseChartVisualizer fonctionne avec les données
provenant de WindDirectionCalibrationAnalyzer

Cet exemple démontre qu'une seule analyse (calibration) peut alimenter
plusieurs visualiseurs grâce au chart_data standardisé.
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
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.wind_rose_chart_visualizer import (
    WindRoseChartVisualizer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    ValidationCriteria,
    Criterion,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def create_synthetic_data(turbine_id: str, days: int = 7):
    """Crée des données synthétiques pour une turbine"""
    timestamps = pd.date_range(
        start="2024-01-01 00:00:00", end=f"2024-01-{days+1} 00:00:00", freq="h"
    )[:-1]

    n_samples = len(timestamps)
    hours = np.arange(n_samples)

    # Direction du vent variant de manière naturelle
    wind_direction = (180 + 120 * np.sin(hours * 2 * np.pi / 24)) % 360

    # Nacelle position avec décalage
    nacelle_position = (wind_direction + 3.0) % 360
    nacelle_position += np.random.normal(0, 1, n_samples)
    nacelle_position = nacelle_position % 360

    # Vitesse de vent variable
    wind_speed = 9 + 4 * np.sin(hours * 2 * np.pi / 48)

    # Puissance selon vitesse
    powers = []
    for ws in wind_speed:
        if ws < 3:
            power = 0
        elif ws < 25:
            power = min(ws**3 * 15, 3780)
        else:
            power = 3780
        powers.append(power)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_direction": wind_direction,
            "nacelle_position": nacelle_position,
            "wind_speed": wind_speed,
            "activation_power": powers,
        }
    )


def run_example():
    """Exécute l'exemple WindRoseChartVisualizer avec données de calibration"""

    logger.info("=" * 80)
    logger.info(
        "Exemple : WindRoseChartVisualizer avec données de WindDirectionCalibrationAnalyzer"
    )
    logger.info("=" * 80)

    # Créer des données pour 2 turbines
    logger.info("\nCréation des données synthétiques...")
    data_e01 = create_synthetic_data("E01", days=7)
    data_e02 = create_synthetic_data("E02", days=7)

    # Configuration commune
    criteria = ValidationCriteria(
        validation_criterion={
            "cut_in_to_cut_out": Criterion(specification=[3.0, 25.0])
        }
    )

    # Analyser la calibration pour chaque turbine
    analyzer = WindDirectionCalibrationAnalyzer()
    calibration_results = {}

    for turbine_id, operation_data in [("E01", data_e01), ("E02", data_e02)]:
        logger.info(f"\nAnalyse calibration {turbine_id}...")

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
                activation_power="activation_power",
            ),
        )

        log_data = pd.DataFrame()

        result = analyzer._compute(
            operation_data, log_data, turbine_config, criteria
        )
        calibration_results[turbine_id] = result

        logger.info(
            f"  Écart moyen: {result['overall_mean_angular_error']:.2f}°"
        )
        logger.info(f"  Critère satisfait: {result['criterion_met']}")
        logger.info(
            f"  chart_data rows: {len(result['chart_data'])} (colonnes: {list(result['chart_data'].columns)})"
        )

    # Créer l'AnalysisResult
    analysis_result = AnalysisResult(
        detailed_results=calibration_results,
        status="completed",
        requires_visuals=True,
    )

    # Générer la rose des vents
    logger.info("\n" + "=" * 80)
    logger.info("Génération de la rose des vents...")
    logger.info("=" * 80)

    wind_rose_visualizer = WindRoseChartVisualizer()
    output = wind_rose_visualizer.generate(analysis_result)

    logger.info(f"\nRose des vents générée :")
    logger.info(f"  PNG: {output['png_path']}")
    logger.info(f"  JSON: {output['json_path']}")

    # Résumé
    logger.info("\n" + "=" * 80)
    logger.info("RÉSUMÉ")
    logger.info("=" * 80)

    logger.info(
        "\n✅ WindRoseChartVisualizer fonctionne avec les données de WindDirectionCalibrationAnalyzer"
    )
    logger.info(
        "\n✅ Une seule analyse fournit les données pour plusieurs visualiseurs :"
    )
    logger.info("   - WindDirectionCalibrationVisualizer (utilise daily_calibration)")
    logger.info("   - PowerRoseChartVisualizer (utilise chart_data)")
    logger.info("   - WindRoseChartVisualizer (utilise chart_data)")

    logger.info(f"\n📊 Fichier généré : {output['png_path']}")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Configuration de l'encodage pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    run_example()
