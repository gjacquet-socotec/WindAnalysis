"""
Exemple d'utilisation du TopErrorCodeFrequencyVisualizer.

Ce script démontre comment utiliser le visualiseur pour générer
un graphique des top 10 codes d'erreur par fréquence et durée.
"""

import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.top_error_code_frequency_visualizer import (
    TopErrorCodeFrequencyVisualizer,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def create_sample_data():
    """Crée des données d'exemple réalistes."""
    return AnalysisResult(
        status="success",
        metadata={"timestamp": datetime.now()},
        requires_visuals=True,
        detailed_results={
            "E1": {
                "summary": {
                    "total_error_events": 125,
                    "unique_error_codes": 25,
                    "turbine_id": "E1",
                },
                "code_frequency": [
                    {
                        "code": "FM6-310",
                        "count": 35,
                        "frequency_percent": 28.0,
                        "description": "Grid fault - Voltage drop",
                        "criticality": "CRITICAL",
                    },
                    {
                        "code": "FM7-120",
                        "count": 22,
                        "frequency_percent": 17.6,
                        "description": "Generator temperature high",
                        "criticality": "HIGH",
                    },
                    {
                        "code": "FM2-050",
                        "count": 18,
                        "frequency_percent": 14.4,
                        "description": "Pitch system error",
                        "criticality": "MEDIUM",
                    },
                    {
                        "code": "FM1-015",
                        "count": 15,
                        "frequency_percent": 12.0,
                        "description": "Wind speed sensor anomaly",
                        "criticality": "LOW",
                    },
                    {
                        "code": "FM6-320",
                        "count": 12,
                        "frequency_percent": 9.6,
                        "description": "Grid frequency out of range",
                        "criticality": "CRITICAL",
                    },
                    {
                        "code": "FM3-080",
                        "count": 8,
                        "frequency_percent": 6.4,
                        "description": "Brake system warning",
                        "criticality": "MEDIUM",
                    },
                    {
                        "code": "FM5-200",
                        "count": 6,
                        "frequency_percent": 4.8,
                        "description": "Converter temperature",
                        "criticality": "HIGH",
                    },
                    {
                        "code": "FM4-110",
                        "count": 4,
                        "frequency_percent": 3.2,
                        "description": "Yaw system fault",
                        "criticality": "MEDIUM",
                    },
                    {
                        "code": "FM8-010",
                        "count": 3,
                        "frequency_percent": 2.4,
                        "description": "Communication error",
                        "criticality": "LOW",
                    },
                    {
                        "code": "FM2-051",
                        "count": 2,
                        "frequency_percent": 1.6,
                        "description": "Pitch angle deviation",
                        "criticality": "MEDIUM",
                    },
                ],
                "most_impactful_codes": [
                    {
                        "code": "FM6-310",
                        "occurrences": 35,
                        "total_duration_hours": 45.8,
                        "criticality": "CRITICAL",
                        "description": "Grid fault - Voltage drop",
                    },
                    {
                        "code": "FM7-120",
                        "occurrences": 22,
                        "total_duration_hours": 28.5,
                        "criticality": "HIGH",
                        "description": "Generator temperature high",
                    },
                    {
                        "code": "FM6-320",
                        "occurrences": 12,
                        "total_duration_hours": 18.2,
                        "criticality": "CRITICAL",
                        "description": "Grid frequency out of range",
                    },
                    {
                        "code": "FM2-050",
                        "occurrences": 18,
                        "total_duration_hours": 12.3,
                        "criticality": "MEDIUM",
                        "description": "Pitch system error",
                    },
                    {
                        "code": "FM5-200",
                        "occurrences": 6,
                        "total_duration_hours": 8.7,
                        "criticality": "HIGH",
                        "description": "Converter temperature",
                    },
                    {
                        "code": "FM1-015",
                        "occurrences": 15,
                        "total_duration_hours": 5.2,
                        "criticality": "LOW",
                        "description": "Wind speed sensor anomaly",
                    },
                    {
                        "code": "FM3-080",
                        "occurrences": 8,
                        "total_duration_hours": 4.1,
                        "criticality": "MEDIUM",
                        "description": "Brake system warning",
                    },
                    {
                        "code": "FM4-110",
                        "occurrences": 4,
                        "total_duration_hours": 2.8,
                        "criticality": "MEDIUM",
                        "description": "Yaw system fault",
                    },
                    {
                        "code": "FM8-010",
                        "occurrences": 3,
                        "total_duration_hours": 1.5,
                        "criticality": "LOW",
                        "description": "Communication error",
                    },
                    {
                        "code": "FM2-051",
                        "occurrences": 2,
                        "total_duration_hours": 0.8,
                        "criticality": "MEDIUM",
                        "description": "Pitch angle deviation",
                    },
                ],
            }
        },
    )


def main():
    """Fonction principale pour tester le visualiseur."""

    # Activer l'encodage UTF-8 pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    logger.info("=" * 80)
    logger.info("EXEMPLE : Top Error Code Frequency Visualizer")
    logger.info("=" * 80)

    # Créer des données d'exemple
    result = create_sample_data()

    # Afficher un résumé des données
    logger.info("\nRésumé des données de test:")
    for turbine_id, data in result.detailed_results.items():
        summary = data.get("summary", {})
        logger.info(f"  Turbine: {turbine_id}")
        logger.info(f"    Total error events: {summary.get('total_error_events', 0)}")
        logger.info(
            f"    Unique error codes: {summary.get('unique_error_codes', 0)}"
        )

        # Top 3 codes par fréquence
        top_freq = data.get("code_frequency", [])[:3]
        logger.info("\n    Top 3 codes par fréquence:")
        for code_info in top_freq:
            logger.info(
                f"      {code_info['code']}: {code_info['count']} occurrences "
                f"({code_info['frequency_percent']}%) - {code_info['description']}"
            )

    # Créer et générer le visualiseur
    logger.info("\n" + "-" * 80)
    logger.info("Génération du graphique...")
    logger.info("-" * 80)

    visualizer = TopErrorCodeFrequencyVisualizer()

    # Définir le répertoire de sortie
    output_dir = project_root / "output" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)
    visualizer.output_dir = output_dir

    output_paths = visualizer.generate(result)

    # Afficher les chemins des fichiers générés
    logger.info("\n✅ Visualisation générée avec succès :")
    for file_type, file_path in output_paths.items():
        logger.info(f"  {file_type}: {file_path}")

    logger.info("\n" + "-" * 80)
    logger.info("ANALYSE DES RÉSULTATS")
    logger.info("-" * 80)
    logger.info(
        """
Le graphique généré montre deux vues complémentaires:

1. GAUCHE - Top 10 par fréquence:
   - Montre les codes qui apparaissent le plus souvent
   - Utile pour identifier les problèmes récurrents
   - Les couleurs indiquent la criticité

2. DROITE - Top 10 par durée:
   - Montre les codes avec le plus d'impact temporel
   - Un code peut être rare mais avoir une longue durée
   - Aide à prioriser les actions de maintenance

CODES COULEURS:
   🔴 Rouge    = CRITICAL (pannes graves)
   🟠 Orange   = HIGH (problèmes importants)
   🟡 Jaune    = MEDIUM (avertissements)
   🟢 Vert     = LOW (informations)
   ⚫ Gris     = Unknown (codes non référencés)
"""
    )

    logger.info("-" * 80)
    logger.info("EXEMPLE TERMINÉ")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
