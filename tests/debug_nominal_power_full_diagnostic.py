"""
Script de diagnostic complet pour identifier les paramètres exacts du calcul de puissance nominale.

Ce script teste systématiquement différentes combinaisons de seuils et périodes
pour trouver lesquelles produisent les valeurs attendues (E1: 4.5h, E6: 5.83h, E8: 7.66h).
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from src.wind_turbine_analytics.application.utils.load_data import load_csv
from src.logger_config import get_logger

logger = get_logger(__name__)

# Configuration
TURBINES = {
    "E1": {
        "path": "./experiments/real_run_test/DATA/E1/tenMinTimeSeries-01WEA95986-Mean-1260206141902.csv",
        "power_col": "01WEA95986 GRD ActivePower",
        "expected": 4.5,
    },
    "E6": {
        "path": "./experiments/real_run_test/DATA/E6/tenMinTimeSeries-06WEA95990-Mean-1260206142342.csv",
        "power_col": "06WEA95990 GRD ActivePower",
        "expected": 5.83,
    },
    "E8": {
        "path": "./experiments/real_run_test/DATA/E8/tenMinTimeSeries-08WEA95991-Mean-1260206142403.csv",
        "power_col": "08WEA95991 GRD ActivePower",
        "expected": 7.66,
    },
}

NOMINAL_POWER_KW = 3780
TEST_START_CONFIG = pd.to_datetime("01.02.2026 00:00:00", dayfirst=True)
TEST_END_CONFIG = pd.to_datetime("05.02.2026 23:50:00", dayfirst=True)

# Seuils à tester (en pourcentage)
THRESHOLDS_PCT = [90, 92, 95, 96, 97, 97.33, 98, 99]

# Périodes à tester
PERIODS = {
    "Config (01-05 Feb)": (TEST_START_CONFIG, TEST_END_CONFIG),
    "Extended before (26 Jan-05 Feb)": (
        pd.to_datetime("26.01.2026 00:00:00", dayfirst=True),
        TEST_END_CONFIG,
    ),
    "Extended after (01-10 Feb)": (
        TEST_START_CONFIG,
        pd.to_datetime("10.02.2026 23:50:00", dayfirst=True),
    ),
}


def find_closest_matches(turbine_id, config, df):
    """Trouve les combinaisons de seuil/période qui donnent le résultat le plus proche"""
    results = []

    power_col = config["power_col"]
    expected = config["expected"]

    for period_name, (start, end) in PERIODS.items():
        # Filtrer sur la période
        mask_period = (df["Date"] >= start) & (df["Date"] <= end)
        df_period = df[mask_period].copy()

        if len(df_period) == 0:
            continue

        # Tester chaque seuil
        for threshold_pct in THRESHOLDS_PCT:
            threshold_kw = (threshold_pct / 100.0) * NOMINAL_POWER_KW

            # Compter les points au-dessus du seuil
            mask = df_period[power_col].fillna(0) >= threshold_kw
            count = mask.sum()
            hours = float(count) * (10.0 / 60.0)

            # Calculer l'écart
            error = abs(hours - expected)
            match_pct = (
                (min(hours, expected) / max(hours, expected)) * 100
                if max(hours, expected) > 0
                else 0
            )

            results.append(
                {
                    "turbine": turbine_id,
                    "period": period_name,
                    "threshold_pct": threshold_pct,
                    "threshold_kw": threshold_kw,
                    "count": count,
                    "hours": hours,
                    "expected": expected,
                    "error": error,
                    "match_pct": match_pct,
                }
            )

    # Trier par erreur croissante
    results.sort(key=lambda x: x["error"])
    return results


def main():
    logger.info("=" * 80)
    logger.info("DIAGNOSTIC COMPLET - CALCUL PUISSANCE NOMINALE")
    logger.info("=" * 80)

    all_results = {}

    for turbine_id, config in TURBINES.items():
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Turbine: {turbine_id} (Expected: {config['expected']}h)")
        logger.info(f"{'=' * 60}")

        # Charger les données
        df = load_csv(config["path"])
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
        df = df.sort_values("Date")

        power_col = config["power_col"]
        df[power_col] = pd.to_numeric(df[power_col], errors="coerce")

        # Analyser les données
        logger.info(f"\nData Overview:")
        logger.info(f"  Total records: {len(df)}")
        logger.info(
            f"  Date range: {df['Date'].min()} to {df['Date'].max()}"
        )
        logger.info(
            f"  Power stats: min={df[power_col].min():.2f}kW, "
            f"max={df[power_col].max():.2f}kW, mean={df[power_col].mean():.2f}kW"
        )

        # Trouver les meilleures correspondances
        matches = find_closest_matches(turbine_id, config, df)
        all_results[turbine_id] = matches

        # Afficher les 5 meilleures correspondances
        logger.info(f"\nTop 5 Closest Matches:")
        logger.info(
            f"{'Rank':<5} {'Period':<35} {'Threshold':<20} {'Hours':<10} "
            f"{'Error':<10} {'Match%':<8}"
        )
        logger.info("-" * 95)

        for idx, match in enumerate(matches[:5], 1):
            logger.info(
                f"{idx:<5} {match['period']:<35} "
                f"{match['threshold_pct']:>5.2f}% ({match['threshold_kw']:>7.2f}kW) "
                f"{match['hours']:>8.2f}h {match['error']:>8.2f}h "
                f"{match['match_pct']:>6.1f}%"
            )

            # Si match parfait ou très proche
            if match["error"] < 0.1:
                logger.info(f"  ⭐ EXCELLENT MATCH! Parameters found:")
                logger.info(f"     Period: {match['period']}")
                logger.info(
                    f"     Threshold: {match['threshold_pct']}% = "
                    f"{match['threshold_kw']:.2f}kW"
                )
                logger.info(
                    f"     Result: {match['hours']:.2f}h "
                    f"(expected {match['expected']}h)"
                )

    # Résumé global
    logger.info(f"\n{'=' * 80}")
    logger.info("SUMMARY - Best Match per Turbine")
    logger.info(f"{'=' * 80}")

    for turbine_id, matches in all_results.items():
        best = matches[0]
        logger.info(f"\n{turbine_id}:")
        logger.info(f"  Expected: {best['expected']:.2f}h")
        logger.info(
            f"  Best match: {best['hours']:.2f}h "
            f"(error: {best['error']:.2f}h, {best['match_pct']:.1f}%)"
        )
        logger.info(
            f"  Parameters: {best['period']}, "
            f"{best['threshold_pct']}% threshold"
        )

    # Vérifier si une combinaison unique fonctionne pour toutes les turbines
    logger.info(f"\n{'=' * 80}")
    logger.info("ANALYSIS - Common Parameters Across Turbines")
    logger.info(f"{'=' * 80}")

    # Pour chaque combinaison seuil/période, vérifier si elle est dans le top 3 de toutes les turbines
    common_params = {}
    for turbine_id, matches in all_results.items():
        for match in matches[:3]:  # Top 3 de chaque turbine
            key = (match["period"], match["threshold_pct"])
            if key not in common_params:
                common_params[key] = []
            common_params[key].append(
                {
                    "turbine": turbine_id,
                    "error": match["error"],
                    "match_pct": match["match_pct"],
                }
            )

    # Trouver les paramètres qui apparaissent dans le top 3 de toutes les turbines
    best_common = None
    best_common_avg_error = float("inf")

    for (period, threshold), turbines in common_params.items():
        if len(turbines) == 3:  # Présent pour les 3 turbines
            avg_error = sum(t["error"] for t in turbines) / 3
            if avg_error < best_common_avg_error:
                best_common_avg_error = avg_error
                best_common = {
                    "period": period,
                    "threshold_pct": threshold,
                    "turbines": turbines,
                    "avg_error": avg_error,
                }

    if best_common:
        logger.info(f"\n✅ Found common parameters that work well for all turbines:")
        logger.info(f"   Period: {best_common['period']}")
        logger.info(f"   Threshold: {best_common['threshold_pct']}%")
        logger.info(f"   Average error: {best_common['avg_error']:.2f}h")
        logger.info(f"\n   Per-turbine results:")
        for t in best_common["turbines"]:
            logger.info(
                f"     {t['turbine']}: error={t['error']:.2f}h, "
                f"match={t['match_pct']:.1f}%"
            )
    else:
        logger.info(
            "\n⚠️  No single parameter combination works well for all turbines."
        )
        logger.info("   Each turbine may require different parameters, or")
        logger.info("   the expected values may be based on different data/methods.")


if __name__ == "__main__":
    main()
