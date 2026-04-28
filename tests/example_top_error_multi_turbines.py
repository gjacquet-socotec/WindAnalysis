"""
Exemple d'utilisation du TopErrorCodeFrequencyVisualizer avec plusieurs turbines.

Ce script démontre l'affichage par turbine (une ligne par turbine).
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


def create_multi_turbine_data():
    """Crée des données pour 4 turbines avec différents profils d'erreur."""
    return AnalysisResult(
        status="success",
        metadata={"timestamp": datetime.now()},
        requires_visuals=True,
        detailed_results={
            "E1": {
                "code_frequency": [
                    {"code": "1005", "count": 2495, "description": "Grid voltage drop", "criticality": "CRITICAL"},
                    {"code": "1002", "count": 714, "description": "Generator overheat", "criticality": "HIGH"},
                    {"code": "0", "count": 488, "description": "Normal operation", "criticality": "LOW"},
                    {"code": "615", "count": 274, "description": "Pitch error", "criticality": "MEDIUM"},
                    {"code": "10769", "count": 249, "description": "Communication timeout", "criticality": "MEDIUM"},
                    {"code": "270", "count": 206, "description": "Emergency stop", "criticality": "CRITICAL"},
                    {"code": "1008", "count": 182, "description": "Converter temperature", "criticality": "HIGH"},
                    {"code": "431", "count": 170, "description": "Wind speed sensor", "criticality": "LOW"},
                    {"code": "1301", "count": 115, "description": "Brake system", "criticality": "MEDIUM"},
                    {"code": "6", "count": 94, "description": "Yaw system", "criticality": "LOW"},
                ],
                "most_impactful_codes": [
                    {"code": "0", "occurrences": 488, "total_duration_hours": 10922.5, "criticality": "LOW", "description": "Normal operation"},
                    {"code": "1005", "occurrences": 2495, "total_duration_hours": 1605.4, "criticality": "CRITICAL", "description": "Grid voltage drop"},
                    {"code": "1002", "occurrences": 714, "total_duration_hours": 1209.3, "criticality": "HIGH", "description": "Generator overheat"},
                    {"code": "615", "occurrences": 274, "total_duration_hours": 677.7, "criticality": "MEDIUM", "description": "Pitch error"},
                    {"code": "6", "occurrences": 94, "total_duration_hours": 199.6, "criticality": "LOW", "description": "Yaw system"},
                    {"code": "270", "occurrences": 206, "total_duration_hours": 8.4, "criticality": "CRITICAL", "description": "Emergency stop"},
                    {"code": "431", "occurrences": 170, "total_duration_hours": 7.3, "criticality": "LOW", "description": "Wind speed sensor"},
                    {"code": "1301", "occurrences": 115, "total_duration_hours": 1.0, "criticality": "MEDIUM", "description": "Brake system"},
                    {"code": "10769", "occurrences": 249, "total_duration_hours": 0.5, "criticality": "MEDIUM", "description": "Communication timeout"},
                    {"code": "1008", "occurrences": 182, "total_duration_hours": 0.5, "criticality": "HIGH", "description": "Converter temperature"},
                ],
            },
            "E6": {
                "code_frequency": [
                    {"code": "1005", "count": 2311, "description": "Grid voltage drop", "criticality": "CRITICAL"},
                    {"code": "1002", "count": 1721, "description": "Generator overheat", "criticality": "HIGH"},
                    {"code": "0", "count": 513, "description": "Normal operation", "criticality": "LOW"},
                    {"code": "615", "count": 291, "description": "Pitch error", "criticality": "MEDIUM"},
                    {"code": "10769", "count": 269, "description": "Communication timeout", "criticality": "MEDIUM"},
                    {"code": "270", "count": 185, "description": "Emergency stop", "criticality": "CRITICAL"},
                    {"code": "1008", "count": 174, "description": "Converter temperature", "criticality": "HIGH"},
                    {"code": "431", "count": 163, "description": "Wind speed sensor", "criticality": "LOW"},
                    {"code": "1301", "count": 99, "description": "Brake system", "criticality": "MEDIUM"},
                    {"code": "6", "count": 93, "description": "Yaw system", "criticality": "LOW"},
                ],
                "most_impactful_codes": [
                    {"code": "0", "occurrences": 513, "total_duration_hours": 11212.4, "criticality": "LOW", "description": "Normal operation"},
                    {"code": "1002", "occurrences": 1721, "total_duration_hours": 1272.2, "criticality": "HIGH", "description": "Generator overheat"},
                    {"code": "1005", "occurrences": 2311, "total_duration_hours": 1043.3, "criticality": "CRITICAL", "description": "Grid voltage drop"},
                    {"code": "615", "occurrences": 291, "total_duration_hours": 671.8, "criticality": "MEDIUM", "description": "Pitch error"},
                    {"code": "6", "occurrences": 93, "total_duration_hours": 195.6, "criticality": "LOW", "description": "Yaw system"},
                    {"code": "270", "occurrences": 185, "total_duration_hours": 7.6, "criticality": "CRITICAL", "description": "Emergency stop"},
                    {"code": "431", "occurrences": 163, "total_duration_hours": 7.1, "criticality": "LOW", "description": "Wind speed sensor"},
                    {"code": "1301", "occurrences": 99, "total_duration_hours": 0.9, "criticality": "MEDIUM", "description": "Brake system"},
                    {"code": "10769", "occurrences": 269, "total_duration_hours": 0.5, "criticality": "MEDIUM", "description": "Communication timeout"},
                    {"code": "1008", "occurrences": 174, "total_duration_hours": 0.2, "criticality": "HIGH", "description": "Converter temperature"},
                ],
            },
            "E8": {
                "code_frequency": [
                    {"code": "1005", "count": 2324, "description": "Grid voltage drop", "criticality": "CRITICAL"},
                    {"code": "0", "count": 872, "description": "Normal operation", "criticality": "LOW"},
                    {"code": "615", "count": 273, "description": "Pitch error", "criticality": "MEDIUM"},
                    {"code": "270", "count": 245, "description": "Emergency stop", "criticality": "CRITICAL"},
                    {"code": "10769", "count": 230, "description": "Communication timeout", "criticality": "MEDIUM"},
                    {"code": "431", "count": 150, "description": "Wind speed sensor", "criticality": "LOW"},
                    {"code": "1002", "count": 120, "description": "Generator overheat", "criticality": "HIGH"},
                    {"code": "1008", "count": 212, "description": "Converter temperature", "criticality": "HIGH"},
                ],
                "most_impactful_codes": [
                    {"code": "0", "occurrences": 872, "total_duration_hours": 12051.0, "criticality": "LOW", "description": "Normal operation"},
                    {"code": "1005", "occurrences": 2324, "total_duration_hours": 1369.5, "criticality": "CRITICAL", "description": "Grid voltage drop"},
                    {"code": "1002", "occurrences": 120, "total_duration_hours": 91.9, "criticality": "HIGH", "description": "Generator overheat"},
                    {"code": "615", "occurrences": 273, "total_duration_hours": 31.8, "criticality": "MEDIUM", "description": "Pitch error"},
                    {"code": "270", "occurrences": 245, "total_duration_hours": 8.4, "criticality": "CRITICAL", "description": "Emergency stop"},
                ],
            },
        },
    )


def main():
    """Fonction principale."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    logger.info("=" * 80)
    logger.info("EXEMPLE : Top Error Codes avec plusieurs turbines")
    logger.info("=" * 80)

    # Créer des données
    result = create_multi_turbine_data()

    logger.info("\nNombre de turbines: %d", len(result.detailed_results))
    logger.info("Turbines: %s", ", ".join(result.detailed_results.keys()))

    # Générer le visualiseur
    logger.info("\n" + "-" * 80)
    logger.info("Génération du graphique...")
    logger.info("-" * 80)

    visualizer = TopErrorCodeFrequencyVisualizer()

    output_dir = project_root / "output" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)
    visualizer.output_dir = output_dir

    output_paths = visualizer.generate(result)

    logger.info("\n✅ Visualisation générée avec succès :")
    for file_type, file_path in output_paths.items():
        logger.info(f"  {file_type}: {file_path}")

    logger.info("\n" + "-" * 80)
    logger.info("ANALYSE")
    logger.info("-" * 80)
    logger.info("""
PRÉSENTATION PAR TURBINE:
- Chaque ligne = 1 turbine
- Colonne gauche = Fréquence (codes les plus fréquents)
- Colonne droite = Durée (codes avec le plus d'impact temporel)

AVANTAGES:
✅ Comparaison directe entre turbines
✅ Identification des problèmes spécifiques par turbine
✅ Vue d'ensemble de la santé du parc éolien
""")

    logger.info("=" * 80)
    logger.info("EXEMPLE TERMINÉ")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
