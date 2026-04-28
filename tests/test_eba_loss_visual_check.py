"""
Test visuel pour EbaLossVisualizer avec des données réalistes.
Génère un graphique pour vérifier visuellement les barres.
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
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_loss_visualizer import (
    EbaLossVisualizer,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def create_test_result():
    """Crée un résultat de test avec des performances très élevées (pertes faibles)."""
    return AnalysisResult(
        status="success",
        metadata={"timestamp": datetime.now()},
        requires_visuals=True,
        detailed_results={
            "LU09": {
                "performance": 99.5,  # Perte de 0.5%
                "monthly_performance": [
                    {"month": "2024-04", "performance": 99.6},
                    {"month": "2024-05", "performance": 99.4},
                    {"month": "2024-06", "performance": 99.5},
                ],
            },
            "LU10": {
                "performance": 99.3,  # Perte de 0.7%
                "monthly_performance": [
                    {"month": "2024-04", "performance": 99.2},
                    {"month": "2024-05", "performance": 99.4},
                    {"month": "2024-06", "performance": 99.3},
                ],
            },
            "LU11": {
                "performance": 99.7,  # Perte de 0.3%
                "monthly_performance": [
                    {"month": "2024-04", "performance": 99.8},
                    {"month": "2024-05", "performance": 99.6},
                    {"month": "2024-06", "performance": 99.7},
                ],
            },
            "LU12": {
                "performance": 99.4,  # Perte de 0.6%
                "monthly_performance": [
                    {"month": "2024-04", "performance": 99.3},
                    {"month": "2024-05", "performance": 99.5},
                    {"month": "2024-06", "performance": 99.4},
                ],
            },
        },
    )


def main():
    """Fonction principale pour générer le graphique de test."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    logger.info("=" * 80)
    logger.info("TEST VISUEL : EbaLossVisualizer avec pertes faibles")
    logger.info("=" * 80)

    # Créer le résultat de test
    result = create_test_result()

    # Afficher les pertes calculées
    logger.info("\nPertes calculées par turbine:")
    for turbine_id, data in result.detailed_results.items():
        perf = data["performance"]
        loss = 100.0 - perf
        logger.info(f"  {turbine_id}: Performance={perf:.2f}%, Loss={loss:.2f}%")

    # Créer le visualiseur
    visualizer = EbaLossVisualizer()

    # Changer le répertoire de sortie pour ce test
    output_dir = project_root / "output" / "test_charts"
    output_dir.mkdir(parents=True, exist_ok=True)
    visualizer.output_dir = output_dir

    # Générer le graphique
    output_paths = visualizer.generate(result)

    logger.info("\n" + "-" * 80)
    logger.info("Graphique généré avec succès !")
    logger.info("-" * 80)
    for file_type, file_path in output_paths.items():
        logger.info(f"  {file_type}: {file_path}")

    logger.info("\n" + "=" * 80)
    logger.info("TEST TERMINÉ - Vérifiez le fichier PNG généré")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
