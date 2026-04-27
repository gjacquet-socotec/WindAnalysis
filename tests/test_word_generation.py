"""
Test de génération du rapport Word complet avec tous les tableaux.

Ce script exécute tous les analyseurs RunTest et génère un rapport Word.
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.application import (
    RunTestPipelineConfig,
    run_runtest_pipeline,
)
from src.wind_turbine_analytics.presentation.console_presenter import (
    ConsolePipelinePresenter,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


def main():
    """Test complet de génération du rapport Word."""

    logger.info("=" * 80)
    logger.info("TEST - Génération du rapport Word RunTest")
    logger.info("=" * 80)

    # Créer la config
    config = RunTestPipelineConfig(
        root_path="./experiments/real_run_test",
        template_path="./assets/templates/template_runtest.docx",
        output_path="./outputs/runtest_report.docx",
        render_template=True,
    )

    # Créer le présentateur console
    presenter = ConsolePipelinePresenter()

    # Exécuter le pipeline (inclut génération Word)
    logger.info("\nExécution du pipeline RunTest...")
    run_runtest_pipeline(config=config, presenter=presenter)

    logger.info("\n" + "=" * 80)
    logger.info("✅ TEST TERMINÉ")
    logger.info("=" * 80)

    # Vérifier que le fichier a été généré
    output_path = Path(config.output_path)
    if output_path.exists():
        logger.info(f"✅ Rapport Word généré: {output_path}")
        logger.info(f"   Taille: {output_path.stat().st_size / 1024:.2f} KB")
    else:
        logger.error(f"❌ Rapport Word NON généré: {output_path}")


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    main()
