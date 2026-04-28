"""
Exemple d'utilisation du EbaLossVisualizer.

Ce script démontre comment utiliser le visualiseur pour générer
un histogramme des pertes d'énergie mensuelles par turbine.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineFarmConfig,
)
from src.wind_turbine_analytics.application.utils.load_yaml_config import (
    load_yaml_config,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_manifacturer_analyzer import (
    EbaManufacturerAnalyzer,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_loss_visualizer import (
    EbaLossVisualizer,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def main():
    """Fonction principale pour tester le visualiseur EBA Loss."""

    # Activer l'encodage UTF-8 pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    logger.info("=" * 80)
    logger.info("EXEMPLE : EBA Loss Visualizer")
    logger.info("=" * 80)

    # Charger la configuration
    config_path = project_root / "config" / "config.yaml"

    if not config_path.exists():
        logger.error(f"Fichier de configuration introuvable : {config_path}")
        logger.info("Veuillez créer un fichier config.yaml avec les turbines à analyser.")
        return

    logger.info(f"Chargement de la configuration depuis : {config_path}")
    turbine_farm: TurbineFarmConfig = load_yaml_config(str(config_path))

    if not turbine_farm.turbines:
        logger.error("Aucune turbine configurée dans le fichier YAML")
        return

    logger.info(f"Nombre de turbines configurées : {len(turbine_farm.turbines)}")
    logger.info(
        f"Turbines : {', '.join([t.turbine_id for t in turbine_farm.turbines])}"
    )

    # Créer l'analyseur EBA Manufacturer
    analyzer = EbaManufacturerAnalyzer()

    # Analyser toutes les turbines
    logger.info("-" * 80)
    logger.info("ÉTAPE 1 : Analyse EBA Manufacturer")
    logger.info("-" * 80)

    result = analyzer.analyze(
        turbine_farm=turbine_farm,
        criteria=turbine_farm.validation_criteria,
    )

    # Afficher les résultats globaux
    if result.success:
        logger.info("✅ Analyse EBA Manufacturer réussie")
        logger.info(f"Performance globale : {result.value:.2f}%")
    else:
        logger.warning("⚠️ Analyse EBA Manufacturer terminée avec des avertissements")

    # Afficher les résultats par turbine
    if result.detailed_results:
        logger.info("\nRésultats par turbine :")
        for turbine_id, turbine_result in result.detailed_results.items():
            if "error" in turbine_result:
                logger.warning(f"  {turbine_id}: ERREUR - {turbine_result['error']}")
            else:
                perf = turbine_result.get("performance", 0)
                loss = 100.0 - perf
                logger.info(f"  {turbine_id}: Performance = {perf:.2f}%, Loss = {loss:.2f}%")

    # Créer et générer le visualiseur
    logger.info("-" * 80)
    logger.info("ÉTAPE 2 : Génération du graphique des pertes d'énergie")
    logger.info("-" * 80)

    visualizer = EbaLossVisualizer()
    output_paths = visualizer.generate(result)

    # Afficher les chemins des fichiers générés
    logger.info("✅ Visualisation générée avec succès :")
    for file_type, file_path in output_paths.items():
        logger.info(f"  {file_type}: {file_path}")

    logger.info("-" * 80)
    logger.info("EXEMPLE TERMINÉ")
    logger.info("-" * 80)


if __name__ == "__main__":
    main()
