"""
Exemple d'utilisation du DataAvailabilityAnalyzer optimisé
Démontre la réduction de taille du vecteur avec plages horaires.
"""

import sys
from pathlib import Path

# Ajouter le projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from datetime import datetime
from src.wind_turbine_analytics.data_processing.analyzer.logics.data_availability_analyzer import (
    DataAvailabilityAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    ValidationCriteria,
    TurbineMappingOperationData,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def create_sample_data(start, end, freq="5min", add_gaps=False):
    """
    Créer des données d'exemple avec gaps optionnels.

    Args:
        start: Date de début
        end: Date de fin
        freq: Fréquence des données
        add_gaps: Si True, ajoute des gaps aléatoires
    """
    timestamps = pd.date_range(start=start, end=end, freq=freq)

    data = pd.DataFrame({
        "timestamp": timestamps,
        "wind_speed": [10.5] * len(timestamps),
        "active_power": [2000.0] * len(timestamps),
        "temperature": [15.0] * len(timestamps),
        "wind_direction": [180.0] * len(timestamps),
    })

    if add_gaps:
        # Créer des gaps dans différentes heures
        # Heure 0 : gap à 00:15
        data.loc[3, "wind_speed"] = None
        # Heure 5 : gap à 05:30
        data.loc[66, "active_power"] = None
        # Heure 10 : gap à 10:45
        data.loc[129, "wind_direction"] = None

    return data


def main():
    """Exemple d'utilisation avec comparaison avant/après optimisation."""

    logger.info("🚀 Démonstration de l'optimisation DataAvailabilityAnalyzer")
    logger.info("=" * 80)

    # Configuration pour 5 jours de test
    test_start = datetime(2026, 1, 1, 0, 0, 0)
    test_end = datetime(2026, 1, 6, 0, 0, 0)  # 5 jours

    mapping = TurbineMappingOperationData(
        timestamp="timestamp",
        wind_speed="wind_speed",
        activation_power="active_power",
        temperature="temperature",
        wind_direction="wind_direction",
    )

    turbine_config = TurbineConfig(
        turbine_id="E1",
        test_start=test_start,
        test_end=test_end,
        mapping_operation_data=mapping,
    )

    # Créer des données avec gaps
    num_days = (test_end - test_start).days
    logger.info(f"\n📊 Création de données de test sur {num_days} jours")
    operation_data = create_sample_data(
        test_start, test_end, freq="5min", add_gaps=True
    )
    logger.info(f"   Nombre de lignes de données brutes : {len(operation_data)}")

    log_data = pd.DataFrame()

    # Analyser
    logger.info("\n🔍 Analyse de la disponibilité...")
    analyzer = DataAvailabilityAnalyzer()
    result = analyzer._compute(
        operation_data=operation_data,
        log_data=log_data,
        turbine_config=turbine_config,
        criteria=ValidationCriteria(),
    )

    # Récupérer les résultats
    availability_df = result["availability_table"]
    summary = result["summary"]

    # Afficher les statistiques
    logger.info("\n" + "=" * 80)
    logger.info("📈 RÉSULTATS DE L'OPTIMISATION")
    logger.info("=" * 80)

    logger.info("\n🎯 Taille du vecteur de sortie :")
    expected_old_size = (test_end - test_start).days * 24 * 6  # 10min intervals
    new_size = len(availability_df)
    compression_ratio = expected_old_size / new_size

    logger.info(f"   Ancienne approche (10min) : {expected_old_size} lignes")
    logger.info(f"   Nouvelle approche (1h)    : {new_size} lignes")
    logger.info(f"   Ratio de compression      : {compression_ratio:.1f}x")
    logger.info(f"   Réduction de taille       : {((expected_old_size - new_size) / expected_old_size * 100):.1f}%")

    logger.info("\n📊 Statistiques de disponibilité :")
    logger.info(f"   Wind Speed       : {summary['wind_speed_availability_pct']:.2f}%")
    logger.info(f"   Active Power     : {summary['active_power_availability_pct']:.2f}%")
    logger.info(f"   Wind Direction   : {summary['wind_direction_availability_pct']:.2f}%")
    logger.info(f"   Temperature      : {summary['temperature_availability_pct']:.2f}%")
    logger.info(f"   Overall          : {summary['overall_availability_pct']:.2f}%")

    # Afficher les heures avec indisponibilité
    logger.info("\n⚠️  Heures avec indisponibilité détectée :")
    unavailable_hours = availability_df[availability_df["overall"] == 0]

    if len(unavailable_hours) > 0:
        for _, row in unavailable_hours.iterrows():
            missing_vars = []
            if row["wind_speed"] == 0:
                missing_vars.append("wind_speed")
            if row["active_power"] == 0:
                missing_vars.append("active_power")
            if row["wind_direction"] == 0:
                missing_vars.append("wind_direction")
            if "temperature" in row and row["temperature"] == 0:
                missing_vars.append("temperature")

            logger.info(f"   {row['timestamp']} → {', '.join(missing_vars)}")
    else:
        logger.info("   Aucune indisponibilité détectée ✅")

    # Afficher un échantillon du DataFrame
    logger.info("\n📋 Échantillon du DataFrame de disponibilité (5 premières heures) :")
    logger.info("\n" + availability_df.head().to_string(index=False))

    logger.info("\n" + "=" * 80)
    logger.info("✅ Analyse terminée avec succès!")
    logger.info("=" * 80)

    # Explication de la logique
    logger.info("\n💡 Logique de l'algorithme :")
    logger.info("   1. Diviser la période en plages horaires (1h)")
    logger.info("   2. Pour chaque heure, vérifier toutes les plages de 5 minutes")
    logger.info("   3. Si UNE SEULE plage de 5 minutes est manquante → toute l'heure = 0")
    logger.info("   4. Si TOUTES les plages de 5 minutes sont présentes → l'heure = 1")
    logger.info("   5. Cela réduit drastiquement la taille du vecteur tout en gardant la précision")

    return availability_df, summary


if __name__ == "__main__":
    # Pour supporter les emojis sur Windows
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    availability_df, summary = main()
