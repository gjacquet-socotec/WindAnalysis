"""
Exemple d'utilisation du DataAvailabilityVisualizer
Génère un graphique de disponibilité des données SCADA.
"""

import sys
from pathlib import Path

# Ajouter le projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from datetime import datetime, timedelta
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.data_availability_visualizer import (
    DataAvailabilityVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def create_sample_availability_data(
    turbine_id: str, start_date: datetime, days: int, availability_pattern: str
):
    """
    Crée des données de disponibilité d'exemple.

    Args:
        turbine_id: ID de la turbine (ex: 'E1')
        start_date: Date de début
        days: Nombre de jours
        availability_pattern: 'good', 'partial', ou 'poor'
    """
    timestamps = pd.date_range(
        start=start_date, periods=days * 24, freq="1h"
    )

    if availability_pattern == "good":
        # Bonne disponibilité (95%+)
        wind_speed = [1] * len(timestamps)
        active_power = [1] * len(timestamps)
        wind_direction = [1] * len(timestamps)
        temperature = [1] * len(timestamps)

        # Quelques gaps mineurs
        wind_speed[10:12] = [0, 0]  # 2h de gap
        active_power[50:52] = [0, 0]

    elif availability_pattern == "partial":
        # Disponibilité partielle (70-80%)
        wind_speed = [1] * len(timestamps)
        active_power = [1] * len(timestamps)
        wind_direction = [1] * len(timestamps)
        temperature = [1] * len(timestamps)

        # Plusieurs gaps
        wind_speed[5:15] = [0] * 10  # 10h de gap
        active_power[20:30] = [0] * 10
        wind_direction[40:45] = [0] * 5

    else:  # 'poor'
        # Mauvaise disponibilité (<70%)
        wind_speed = [1] * len(timestamps)
        active_power = [1] * len(timestamps)
        wind_direction = [1] * len(timestamps)
        temperature = [1] * len(timestamps)

        # Nombreux gaps
        wind_speed[5:25] = [0] * 20  # 20h de gap
        active_power[10:30] = [0] * 20
        wind_direction[35:55] = [0] * 20
        temperature[60:70] = [0] * 10

    # Calculer overall (ET logique)
    overall = [
        1 if (ws and ap and wd and temp) else 0
        for ws, ap, wd, temp in zip(
            wind_speed, active_power, wind_direction, temperature
        )
    ]

    # Calculer les statistiques
    total_hours = len(timestamps)
    overall_pct = (sum(overall) / total_hours) * 100
    ws_pct = (sum(wind_speed) / total_hours) * 100
    ap_pct = (sum(active_power) / total_hours) * 100
    wd_pct = (sum(wind_direction) / total_hours) * 100
    temp_pct = (sum(temperature) / total_hours) * 100

    availability_df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_speed": wind_speed,
            "active_power": active_power,
            "wind_direction": wind_direction,
            "temperature": temperature,
            "overall": overall,
        }
    )

    summary = {
        "total_hours": total_hours,
        "overall_availability_pct": overall_pct,
        "wind_speed_availability_pct": ws_pct,
        "active_power_availability_pct": ap_pct,
        "wind_direction_availability_pct": wd_pct,
        "temperature_availability_pct": temp_pct,
    }

    return availability_df, summary


def main():
    """Exemple d'utilisation du visualiseur."""

    logger.info("🎨 Démonstration du DataAvailabilityVisualizer")
    logger.info("=" * 80)

    # Configuration
    start_date = datetime(2024, 9, 1, 0, 0, 0)
    days = 3  # 3 jours de données

    logger.info(f"\n📅 Période: {days} jours")
    logger.info(f"   Du: {start_date}")
    logger.info(f"   Au: {start_date + timedelta(days=days)}")

    # Créer des données pour plusieurs turbines avec différents patterns
    logger.info("\n🏗️  Création des données d'exemple...")

    turbines_data = {
        "E12": ("good", "Excellente disponibilité"),
        "E11": ("good", "Bonne disponibilité"),
        "E10": ("partial", "Disponibilité partielle"),
        "E9": ("partial", "Disponibilité partielle"),
    }

    detailed_results = {}

    for turbine_id, (pattern, description) in turbines_data.items():
        logger.info(f"   {turbine_id}: {description} ({pattern})")
        availability_df, summary = create_sample_availability_data(
            turbine_id, start_date, days, pattern
        )

        detailed_results[turbine_id] = {
            "availability_table": availability_df,
            "summary": summary,
        }

        logger.info(
            f"      → Overall: {summary['overall_availability_pct']:.1f}%"
        )

    # Créer le résultat d'analyse
    result = AnalysisResult(
        detailed_results=detailed_results,
        status="completed",
        requires_visuals=True,
    )

    # Créer le répertoire de sortie
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    # Initialiser les métadonnées
    if result.metadata is None:
        result.metadata = {}

    result.metadata["output_dir"] = str(output_dir)
    result.metadata["charts"] = {}

    # Générer le graphique
    logger.info("\n📊 Génération du graphique...")
    visualizer = DataAvailabilityVisualizer()
    output_paths = visualizer.generate(result)

    # Afficher les résultats
    logger.info("\n" + "=" * 80)
    logger.info("✅ VISUALISATION GÉNÉRÉE")
    logger.info("=" * 80)

    logger.info(f"\n📁 Fichiers générés:")
    logger.info(f"   PNG: {output_paths['png_path']}")
    logger.info(f"   JSON: {output_paths['json_path']}")

    logger.info("\n📋 Statistiques par turbine:")
    for turbine_id in sorted(detailed_results.keys()):
        summary = detailed_results[turbine_id]["summary"]
        logger.info(f"\n   {turbine_id}:")
        logger.info(
            f"      Wind Speed       : "
            f"{summary['wind_speed_availability_pct']:.1f}%"
        )
        logger.info(
            f"      Active Power     : "
            f"{summary['active_power_availability_pct']:.1f}%"
        )
        logger.info(
            f"      Wind Direction   : "
            f"{summary['wind_direction_availability_pct']:.1f}%"
        )
        logger.info(
            f"      Temperature      : "
            f"{summary['temperature_availability_pct']:.1f}%"
        )
        logger.info(
            f"      Overall          : "
            f"{summary['overall_availability_pct']:.1f}%"
        )

    logger.info("\n" + "=" * 80)
    logger.info("💡 Interprétation du graphique:")
    logger.info("=" * 80)
    logger.info("   - Axe X: Temps (périodes horaires)")
    logger.info("   - Axe Y: Variables par turbine (ws, power, dir, temp)")
    logger.info("   - Vert: Données disponibles (100%)")
    logger.info("   - Orange: Données indisponibles (0%)")
    logger.info("   - Les barres horizontales montrent la continuité")
    logger.info("   - Format de date adapté à la durée de la période")

    logger.info("\n" + "=" * 80)
    logger.info("🎯 Format similaire à l'image de référence SCADA")
    logger.info("=" * 80)

    return output_paths


if __name__ == "__main__":
    # Pour supporter les emojis sur Windows
    import sys

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    output_paths = main()
    print(f"\n✅ Visualisation disponible: {output_paths['png_path']}")
