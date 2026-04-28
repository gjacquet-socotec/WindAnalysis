"""
Exemple d'utilisation du CodeErrorAnalyzer.

Ce script illustre comment analyser les codes d'erreur présents dans les logs
et voir leur impact sur la production.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger_config import get_logger
from src.wind_turbine_analytics.application.utils.yaml_tools import load_config
from src.wind_turbine_analytics.data_processing.analyzer.logics.code_error_analyzer import (
    CodeErrorAnalyzer,
)
import json

logger = get_logger(__name__)


def main():
    """Exemple d'utilisation du CodeErrorAnalyzer."""

    # Charger la configuration
    config_path = project_root / "experiments" / "scada_analyse" / "config.yml"
    logger.info(f"Chargement de la configuration depuis {config_path}")

    turbine_farm, criteria, general_info = load_config(str(config_path))

    # Créer l'analyseur
    analyzer = CodeErrorAnalyzer()

    # Analyser les codes d'erreur
    logger.info("Analyse des codes d'erreur...")
    results = analyzer.analyze(turbine_farm, criteria)

    # Afficher les résultats pour chaque turbine
    for turbine_id, result in results.detailed_results.items():
        logger.info(f"\n{'='*80}")
        logger.info(f"TURBINE: {turbine_id}")
        logger.info(f"{'='*80}")

        if "error" in result:
            logger.warning(f"Erreur: {result['error']}")
            continue

        # Résumé
        summary = result["summary"]
        logger.info(f"\n📊 RÉSUMÉ:")
        logger.info(f"  - Période de test: {summary['test_period_hours']} heures")
        logger.info(f"  - Total d'événements d'erreur: {summary['total_error_events']}")
        logger.info(f"  - Codes d'erreur uniques: {summary['unique_error_codes']}")

        # Top 5 codes les plus fréquents
        logger.info(f"\n🔢 TOP 5 CODES LES PLUS FRÉQUENTS:")
        for i, code_info in enumerate(result["code_frequency"][:5], 1):
            logger.info(
                f"  {i}. Code {code_info['code']}: {code_info['count']} fois "
                f"({code_info['frequency_percent']}%) - "
                f"Criticité: {code_info['criticality']}"
            )
            logger.info(f"     Description: {code_info['description'][:60]}...")

        # Répartition par criticité
        logger.info(f"\n⚠️  RÉPARTITION PAR CRITICITÉ:")
        crit_dist = result["criticality_distribution"]
        for crit_level in ["critical", "high", "medium", "low", "unknown"]:
            if crit_level in crit_dist and crit_dist[crit_level]["total_occurrences"] > 0:
                stats = crit_dist[crit_level]
                logger.info(
                    f"  - {crit_level.upper()}: {stats['total_occurrences']} occurrences "
                    f"({stats['percent_of_total']}%) - "
                    f"{stats['unique_codes']} codes uniques"
                )

        # Répartition par système
        logger.info(f"\n🔧 RÉPARTITION PAR SYSTÈME FONCTIONNEL:")
        sys_dist = result["system_distribution"]
        for system, stats in sorted(
            sys_dist.items(),
            key=lambda x: x[1]["total_occurrences"],
            reverse=True
        )[:5]:
            logger.info(
                f"  - {system}: {stats['total_occurrences']} occurrences "
                f"({stats['percent_of_total']}%)"
            )

        # Impact sur la production
        logger.info(f"\n📉 IMPACT SUR LA PRODUCTION:")
        impact = result["production_impact"]
        logger.info(
            f"  - Puissance moyenne SANS erreurs critiques: "
            f"{impact['mean_power_without_errors_kW']:.2f} kW"
        )
        logger.info(
            f"  - Puissance moyenne AVEC erreurs critiques: "
            f"{impact['mean_power_with_errors_kW']:.2f} kW"
        )
        logger.info(
            f"  - Perte de production estimée: "
            f"{impact['production_loss_percent']:.2f}%"
        )
        logger.info(
            f"  - Périodes avec erreurs critiques: "
            f"{impact['periods_with_critical_errors_count']}"
        )

        # Corrélation avec le vent
        logger.info(f"\n🌬️  CORRÉLATION AVEC LA VITESSE DE VENT:")
        wind = result["wind_correlation"]
        logger.info(
            f"  - Vent moyen pendant erreurs: {wind['mean_wind_with_errors_ms']:.2f} m/s"
        )
        logger.info(
            f"  - Vent moyen hors erreurs: {wind['mean_wind_without_errors_ms']:.2f} m/s"
        )
        logger.info(f"  - Taux d'erreur par plage de vent:")
        for wind_range, stats in wind["wind_ranges"].items():
            logger.info(
                f"    • {wind_range}: {stats['error_rate_percent']:.2f}% "
                f"({stats['error_periods']}/{stats['total_periods']} périodes)"
            )

        # Top 5 codes les plus impactants
        logger.info(f"\n💥 TOP 5 CODES LES PLUS IMPACTANTS (durée totale):")
        for i, code_info in enumerate(result["most_impactful_codes"][:5], 1):
            logger.info(
                f"  {i}. Code {code_info['code']}: "
                f"{code_info['total_duration_hours']:.2f}h totales "
                f"({code_info['occurrences']} occurrences) - "
                f"Criticité: {code_info['criticality']}"
            )
            logger.info(f"     {code_info['description'][:60]}...")

        # Sauvegarder les résultats détaillés en JSON
        output_dir = project_root / "output" / "code_error_analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{turbine_id}_code_error_analysis.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"\n💾 Résultats détaillés sauvegardés: {output_file}")

    logger.info(f"\n{'='*80}")
    logger.info("✅ Analyse terminée avec succès!")


if __name__ == "__main__":
    # Encoder UTF-8 pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    main()
