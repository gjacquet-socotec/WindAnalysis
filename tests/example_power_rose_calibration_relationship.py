"""
Exemple montrant la relation entre PowerRoseChartVisualizer et
WindDirectionCalibrationVisualizer

Cet exemple démontre comment un problème de calibration de nacelle
(détecté par WindDirectionCalibrationVisualizer) se traduit par une
sous-performance directionnelle (visible dans PowerRoseChartVisualizer).
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
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.power_rose_chart_visualizer import (
    PowerRoseChartVisualizer,
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


def create_turbine_with_calibration_issue(
    turbine_id: str, calibration_offset: float, problematic_sector: tuple = None
):
    """
    Crée des données synthétiques pour une turbine avec un problème de calibration.

    Args:
        turbine_id: Identifiant de la turbine
        calibration_offset: Décalage de calibration global (degrés)
        problematic_sector: Tuple (start_deg, end_deg) du secteur problématique
                          où le décalage est plus important
    """
    # 7 jours de données, une mesure par heure
    timestamps = pd.date_range(
        start="2024-01-01 00:00:00", end="2024-01-08 00:00:00", freq="h"
    )[:-1]

    n_samples = len(timestamps)

    # Direction du vent variant de manière naturelle
    hours = np.arange(n_samples)
    wind_direction = (180 + 120 * np.sin(hours * 2 * np.pi / 24)) % 360

    # Nacelle position avec décalage de calibration
    nacelle_position = (wind_direction + calibration_offset) % 360

    # Si secteur problématique spécifié, augmenter le décalage dans ce secteur
    if problematic_sector:
        start_deg, end_deg = problematic_sector
        for i, wd in enumerate(wind_direction):
            # Vérifier si dans le secteur problématique
            if start_deg <= end_deg:
                in_sector = start_deg <= wd <= end_deg
            else:  # Cas wraparound (ex: 330-30)
                in_sector = (wd >= start_deg) or (wd <= end_deg)

            if in_sector:
                # Augmenter le décalage dans le secteur problématique
                additional_offset = 5.0
                nacelle_position[i] = (
                    wind_direction[i] + calibration_offset + additional_offset
                ) % 360

    # Ajouter du bruit réaliste
    nacelle_position += np.random.normal(0, 1, n_samples)
    nacelle_position = nacelle_position % 360

    # Vitesse de vent variable
    wind_speed = 9 + 4 * np.sin(hours * 2 * np.pi / 48)

    # Puissance calculée selon la vitesse ET la qualité de calibration
    # La puissance est réduite si le décalage nacelle/vent est important
    powers = []
    for i in range(n_samples):
        # Puissance théorique selon vitesse de vent
        ws = wind_speed[i]
        if ws < 3:
            base_power = 0
        elif ws < 25:
            base_power = min(ws**3 * 15, 3780)
        else:
            base_power = 3780

        # Calculer l'écart angulaire réel
        angular_diff = abs(wind_direction[i] - nacelle_position[i])
        if angular_diff > 180:
            angular_diff = 360 - angular_diff

        # Réduire la puissance si mauvais alignement
        # Écart de 0° = 100% puissance, écart de 20° = 70% puissance
        efficiency = max(0.7, 1.0 - (angular_diff / 20) * 0.3)
        actual_power = base_power * efficiency

        powers.append(actual_power)

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
    """Exécute l'exemple de relation entre calibration et rose des puissances"""

    logger.info("=" * 80)
    logger.info(
        "Exemple : Relation entre Calibration et Rose des Puissances"
    )
    logger.info("=" * 80)

    # === TURBINE 1 : Bonne calibration (3°) ===
    logger.info("\n--- TURBINE E01 : Bonne calibration globale (3°) ---")
    data_e01 = create_turbine_with_calibration_issue(
        "E01", calibration_offset=3.0
    )

    # === TURBINE 2 : Calibration correcte globalement mais problème secteur Nord ===
    logger.info(
        "\n--- TURBINE E02 : Problème secteur Nord (330-30°) ---"
    )
    data_e02 = create_turbine_with_calibration_issue(
        "E02", calibration_offset=3.0, problematic_sector=(330, 30)
    )

    # === TURBINE 3 : Mauvaise calibration globale (8°) ===
    logger.info("\n--- TURBINE E03 : Mauvaise calibration globale (8°) ---")
    data_e03 = create_turbine_with_calibration_issue(
        "E03", calibration_offset=8.0
    )

    # Configuration commune
    criteria = ValidationCriteria(
        validation_criterion={
            "cut_in_to_cut_out": Criterion(specification=[3.0, 25.0])
        }
    )

    # Analyser la calibration pour chaque turbine
    analyzer = WindDirectionCalibrationAnalyzer()
    calibration_results = {}
    chart_data_for_rose = {}

    for turbine_id, operation_data in [
        ("E01", data_e01),
        ("E02", data_e02),
        ("E03", data_e03),
    ]:
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

        # Stocker les données pour la rose des puissances
        chart_data_for_rose[turbine_id] = operation_data

        logger.info(
            f"  Écart moyen: {result['overall_mean_angular_error']:.2f}°"
        )
        logger.info(f"  Critère satisfait: {result['criterion_met']}")

    # === GÉNÉRATION DES VISUALISATIONS ===

    logger.info("\n" + "=" * 80)
    logger.info("Génération des visualisations...")
    logger.info("=" * 80)

    # 1. Visualisation de la calibration
    logger.info("\n1. Génération du graphique de calibration...")
    calibration_analysis_result = AnalysisResult(
        detailed_results=calibration_results,
        status="completed",
        requires_visuals=True,
    )

    calibration_visualizer = WindDirectionCalibrationVisualizer()
    cal_output = calibration_visualizer.generate(calibration_analysis_result)

    logger.info(f"   PNG: {cal_output['png_path']}")
    logger.info(f"   JSON: {cal_output['json_path']}")

    # 2. Visualisation de la rose des puissances
    logger.info("\n2. Génération de la rose des puissances...")
    rose_analysis_result = AnalysisResult(
        detailed_results={
            tid: {"chart_data": data} for tid, data in chart_data_for_rose.items()
        },
        status="completed",
        requires_visuals=True,
    )

    power_rose_visualizer = PowerRoseChartVisualizer()
    rose_output = power_rose_visualizer.generate(rose_analysis_result)

    logger.info(f"   PNG: {rose_output['png_path']}")
    logger.info(f"   JSON: {rose_output['json_path']}")

    # === RÉSUMÉ ET INTERPRÉTATION ===

    logger.info("\n" + "=" * 80)
    logger.info("RÉSUMÉ DES RÉSULTATS")
    logger.info("=" * 80)

    for turbine_id, result in calibration_results.items():
        status = "OK" if result["criterion_met"] else "À REVOIR"
        logger.info(
            f"\n{turbine_id}: [{status}] - Écart moyen = "
            f"{result['overall_mean_angular_error']:.2f}° "
            f"(seuil: {result['threshold_degrees']}°)"
        )

    logger.info("\n" + "=" * 80)
    logger.info("INTERPRÉTATION - RELATION ENTRE LES DEUX GRAPHIQUES")
    logger.info("=" * 80)

    logger.info("\n1. WindDirectionCalibrationVisualizer (Diagnostic)")
    logger.info("   - Montre les écarts angulaires entre nacelle et vent")
    logger.info("   - Permet d'identifier SI il y a un problème de calibration")
    logger.info("   - Indique la QUALITÉ globale de l'alignement")

    logger.info("\n2. PowerRoseChartVisualizer (Impact)")
    logger.info("   - Montre la puissance produite par secteur directionnel")
    logger.info("   - Permet de voir l'IMPACT du problème de calibration")
    logger.info("   - Identifie les SECTEURS affectés")

    logger.info("\n3. Corrélation entre les deux :")

    logger.info(
        "\n   E01 (Bonne calibration 3°):"
    )
    logger.info(
        "   → Calibration : Écarts faibles et uniformes"
    )
    logger.info(
        "   → Rose : Puissance élevée et uniforme dans toutes les directions"
    )

    logger.info(
        "\n   E02 (Problème secteur Nord):"
    )
    logger.info(
        "   → Calibration : Écart moyen global acceptable, mais pics dans certains secteurs"
    )
    logger.info(
        "   → Rose : Puissance réduite dans le secteur Nord (330-30°)"
    )
    logger.info(
        "   → DIAGNOSTIC : Problème de calibration localisé au secteur Nord"
    )

    logger.info(
        "\n   E03 (Mauvaise calibration 8°):"
    )
    logger.info(
        "   → Calibration : Écarts élevés dans tous les secteurs"
    )
    logger.info(
        "   → Rose : Puissance globalement réduite dans toutes les directions"
    )
    logger.info(
        "   → DIAGNOSTIC : Recalibration complète nécessaire"
    )

    logger.info("\n" + "=" * 80)
    logger.info("4. Utilisation pratique :")
    logger.info("=" * 80)
    logger.info(
        "\n   a) Consulter d'abord WindDirectionCalibrationVisualizer"
    )
    logger.info("      → Identifier si problème de calibration global ou local")
    logger.info(
        "\n   b) Puis consulter PowerRoseChartVisualizer"
    )
    logger.info("      → Quantifier l'impact sur la production")
    logger.info("      → Identifier les secteurs prioritaires à corriger")
    logger.info(
        "\n   c) Secteurs avec faible puissance + écart élevé = Action prioritaire"
    )

    logger.info("\n" + "=" * 80)
    logger.info("Exemple terminé avec succès !")
    logger.info(f"Graphique calibration : {cal_output['png_path']}")
    logger.info(f"Rose des puissances   : {rose_output['png_path']}")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Configuration de l'encodage pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    run_example()
