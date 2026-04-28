"""
Exemple d'utilisation de WindDirectionCalibrationAnalyzer

Cet exemple démontre comment utiliser l'analyseur pour vérifier
la calibration de la nacelle par rapport à la direction du vent.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from datetime import datetime

from src.wind_turbine_analytics.data_processing.analyzer.logics.wind_direction_calibration_analyzer import (
    WindDirectionCalibrationAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineFarm,
    ValidationCriteria,
    Criterion,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def create_synthetic_data():
    """
    Crée des données synthétiques pour la démonstration.

    Scénario simulé :
    - 5 jours de données (2024-01-01 à 2024-01-05)
    - Mesure toutes les heures
    - Direction du vent variant naturellement
    - Nacelle avec un décalage de calibration de 3° (acceptable)
    - Quelques points avec wraparound 360°/0°
    """
    timestamps = pd.date_range(
        start="2024-01-01 00:00:00", end="2024-01-06 00:00:00", freq="1H"
    )[:-1]

    # Direction du vent variant de manière sinusoïdale entre 0° et 360°
    # Simule une rotation du vent typique
    hours = np.arange(len(timestamps))
    wind_direction = (180 + 120 * np.sin(hours * 2 * np.pi / 24)) % 360

    # Nacelle suit le vent avec un décalage constant de 3°
    nacelle_position = (wind_direction + 3) % 360

    # Ajouter un peu de bruit réaliste (±1°)
    nacelle_position += np.random.normal(0, 1, len(timestamps))
    nacelle_position = nacelle_position % 360

    # Vitesse de vent variable (entre 4 et 15 m/s)
    wind_speed = 9 + 4 * np.sin(hours * 2 * np.pi / 48)

    # Puissance active corrélée à la vitesse de vent
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

    # Log vide pour cet exemple
    log_data = pd.DataFrame()

    return operation_data, log_data


def create_poor_calibration_data():
    """
    Crée des données avec une mauvaise calibration (écart > 5°).
    Utile pour tester le cas où le critère n'est PAS satisfait.
    """
    timestamps = pd.date_range(
        start="2024-01-01 00:00:00", end="2024-01-03 00:00:00", freq="1H"
    )[:-1]

    hours = np.arange(len(timestamps))
    wind_direction = (180 + 120 * np.sin(hours * 2 * np.pi / 24)) % 360

    # Nacelle mal calibrée : décalage de 8°
    nacelle_position = (wind_direction + 8) % 360
    nacelle_position += np.random.normal(0, 2, len(timestamps))  # Plus de bruit
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

    log_data = pd.DataFrame()

    return operation_data, log_data


def run_example():
    """Exécute l'exemple d'analyse de calibration"""

    logger.info("=" * 80)
    logger.info("Exemple d'analyse de calibration de direction du vent")
    logger.info("=" * 80)

    # Configuration de la turbine
    turbine_config = TurbineConfig(
        turbine_id="E01",
        test_start=pd.Timestamp("2024-01-01 00:00:00"),
        test_end=pd.Timestamp("2024-01-06 00:00:00"),
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

    # Critères de validation
    criteria = ValidationCriteria(
        validation_criterion={"cut_in_to_cut_out": Criterion(specification=[3.0, 25.0])}
    )

    # === SCÉNARIO 1 : Bonne calibration (écart ~3°) ===
    logger.info("\n" + "=" * 80)
    logger.info("SCÉNARIO 1 : Bonne calibration (écart ~3°)")
    logger.info("=" * 80)

    operation_data, log_data = create_synthetic_data()
    logger.info(f"Données générées : {len(operation_data)} mesures")

    analyzer = WindDirectionCalibrationAnalyzer()
    result = analyzer._compute(operation_data, log_data, turbine_config, criteria)

    logger.info("\n--- Résultats globaux ---")
    logger.info(f"Écart angulaire moyen : {result['overall_mean_angular_error']:.2f}°")
    logger.info(f"Écart-type : {result['overall_std_angular_error']:.2f}°")
    logger.info(f"Écart maximum : {result['overall_max_angular_error']:.2f}°")
    logger.info(f"Corrélation : {result['overall_correlation']:.3f}")
    logger.info(f"Seuil requis : {result['threshold_degrees']}°")
    logger.info(f"Critère satisfait : {'✓ OUI' if result['criterion_met'] else '✗ NON'}")
    logger.info(f"Nombre de mesures : {result['total_measurements']}")

    logger.info("\n--- Détails journaliers (premiers 3 jours) ---")
    for day_result in result["daily_calibration"][:3]:
        logger.info(
            f"  {day_result['date']} : "
            f"mean={day_result['mean_angular_error']}°, "
            f"std={day_result['std_angular_error']}°, "
            f"max={day_result['max_angular_error']}°, "
            f"corr={day_result['correlation']}, "
            f"n={day_result['num_measurements']}"
        )

    # === SCÉNARIO 2 : Mauvaise calibration (écart ~8°) ===
    logger.info("\n" + "=" * 80)
    logger.info("SCÉNARIO 2 : Mauvaise calibration (écart ~8°)")
    logger.info("=" * 80)

    operation_data_bad, log_data_bad = create_poor_calibration_data()
    turbine_config.test_end = pd.Timestamp("2024-01-03 00:00:00")

    result_bad = analyzer._compute(
        operation_data_bad, log_data_bad, turbine_config, criteria
    )

    logger.info("\n--- Résultats globaux ---")
    logger.info(
        f"Écart angulaire moyen : {result_bad['overall_mean_angular_error']:.2f}°"
    )
    logger.info(f"Écart-type : {result_bad['overall_std_angular_error']:.2f}°")
    logger.info(f"Écart maximum : {result_bad['overall_max_angular_error']:.2f}°")
    logger.info(f"Corrélation : {result_bad['overall_correlation']:.3f}")
    logger.info(f"Seuil requis : {result_bad['threshold_degrees']}°")
    logger.info(
        f"Critère satisfait : {'✓ OUI' if result_bad['criterion_met'] else '✗ NON'}"
    )

    logger.info("\n--- Interprétation ---")
    if result_bad["criterion_met"]:
        logger.info("✓ La nacelle est correctement calibrée.")
    else:
        logger.info(
            f"✗ PROBLÈME DÉTECTÉ : L'écart moyen de {result_bad['overall_mean_angular_error']}° "
            f"dépasse le seuil acceptable de {result_bad['threshold_degrees']}°."
        )
        logger.info(
            "  → Recommandation : Recalibrer la nacelle pour améliorer la performance."
        )

    # === SCÉNARIO 3 : Test de la fonction wraparound ===
    logger.info("\n" + "=" * 80)
    logger.info("SCÉNARIO 3 : Test du calcul d'écart avec wraparound 360°/0°")
    logger.info("=" * 80)

    # Test manuel de la fonction _calculate_angular_difference
    test_cases = [
        (10, 20, 10),  # Cas normal
        (359, 1, 2),  # Wraparound 359→1
        (1, 359, 2),  # Wraparound inverse 1→359
        (180, 0, 180),  # Limite 180°
        (10, 350, 20),  # 10→350 par le chemin court
    ]

    logger.info("\nTests de calcul d'écart angulaire :")
    for angle1, angle2, expected in test_cases:
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            pd.Series([angle1]), pd.Series([angle2])
        )
        status = "✓" if abs(result[0] - expected) < 0.1 else "✗"
        logger.info(
            f"  {status} angle1={angle1}°, angle2={angle2}° → écart={result[0]:.1f}° "
            f"(attendu: {expected}°)"
        )

    logger.info("\n" + "=" * 80)
    logger.info("Exemple terminé avec succès !")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Configuration de l'encodage pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    run_example()
