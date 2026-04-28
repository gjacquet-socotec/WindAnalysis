"""
Script de diagnostic pour identifier le problème avec EbaLossVisualizer.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineFarm,
)
from src.wind_turbine_analytics.application.utils.load_yaml_config import (
    load_yaml_config,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_manifacturer_analyzer import (
    EbaManufacturerAnalyzer,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def main():
    """Fonction principale pour diagnostiquer les données EBA Loss."""

    # Activer l'encodage UTF-8 pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    logger.info("=" * 80)
    logger.info("DIAGNOSTIC : Données EBA Loss")
    logger.info("=" * 80)

    # Charger la configuration
    config_path = project_root / "config" / "config.yaml"

    if not config_path.exists():
        logger.error(f"Fichier de configuration introuvable : {config_path}")
        return

    logger.info(f"Chargement de la configuration depuis : {config_path}")
    turbine_farm: TurbineFarm = load_yaml_config(str(config_path))

    if not turbine_farm.turbines:
        logger.error("Aucune turbine configurée dans le fichier YAML")
        return

    # Créer l'analyseur EBA Manufacturer
    analyzer = EbaManufacturerAnalyzer()

    # Analyser toutes les turbines
    result = analyzer.analyze(
        turbine_farm=turbine_farm,
        criteria=turbine_farm.validation_criteria,
    )

    # Analyser les données détaillées
    logger.info("-" * 80)
    logger.info("ANALYSE DES DONNÉES DÉTAILLÉES")
    logger.info("-" * 80)

    if not result.detailed_results:
        logger.error("Aucun résultat détaillé disponible !")
        return

    for turbine_id, turbine_data in result.detailed_results.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"TURBINE: {turbine_id}")
        logger.info(f"{'='*60}")

        if "error" in turbine_data:
            logger.error(f"Erreur : {turbine_data['error']}")
            continue

        # Performance globale
        performance = turbine_data.get("performance", 0)
        loss_global = 100.0 - performance
        logger.info(f"Performance globale : {performance:.2f}%")
        logger.info(f"Perte globale : {loss_global:.2f}%")

        # Données mensuelles
        monthly_data = turbine_data.get("monthly_performance", [])
        if not monthly_data:
            logger.warning("Pas de données mensuelles")
            continue

        logger.info(f"\nDonnées mensuelles ({len(monthly_data)} mois):")
        logger.info("-" * 60)

        for month_info in monthly_data:
            month = month_info.get("month", "N/A")
            perf = month_info.get("performance", 0)
            loss = 100.0 - perf

            logger.info(f"  {month}: Performance={perf:.2f}%, Loss={loss:.2f}%")

    logger.info("\n" + "=" * 80)
    logger.info("DIAGNOSTIC TERMINÉ")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
