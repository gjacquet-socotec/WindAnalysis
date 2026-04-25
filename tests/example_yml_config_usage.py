"""
Exemple : Utiliser les configurations YAML avec mapping flexible de colonnes.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.application.utils.load_data import (
    load_csv,
    prepare_log_dataframe_with_mapping,
)
from src.wind_turbine_analytics.application.configuration.config_models import (  # noqa: E501
    TurbineLogMapping,
)
from src.wind_turbine_analytics.data_processing.log_code.generator_type.nordex_n311_log_code_manager import (  # noqa: E501
    NordexN311LogCodeManager,
)
import pandas as pd


def main():
    # Configuration encodage Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("EXEMPLE : Configuration YAML avec colonnes date/time flexibles")
    print("=" * 80)
    print()

    # Cas 1: Fichier avec date et time séparés
    print("1. Fichier log avec colonnes date et time séparées:")
    print("-" * 80)

    # Charger le fichier réel
    log_file = 'experiments/real_run_test/DATA/E1/alarmLog-01WEA95986-1260206141836.csv'  # noqa: E501

    try:
        log_df = load_csv(log_file)
        print(f"Fichier chargé: {log_df.shape}")
        print(f"Colonnes: {list(log_df.columns)}")
        print()

        # Configuration YAML style 1: colonnes séparées date + time
        mapping_v1 = TurbineLogMapping(
            start_date=["date", "time"],  # LISTE de colonnes
            end_date=["date", "time"],
            name="name",
            oper="oper",
            status="status"
        )

        # Préparer le DataFrame
        log_prepared, start_col, end_col = prepare_log_dataframe_with_mapping(  # noqa: E501
            log_df, mapping_v1
        )

        print(f"Après préparation:")
        print(f"  - Colonne start: {start_col}")
        print(f"  - Colonne end: {end_col}")
        print(f"  - Colonnes disponibles: {list(log_prepared.columns)}")
        print()

        # Configuration YAML style 2: colonne timestamp unique
        print("2. Configuration alternative avec timestamp unique:")
        print("-" * 80)

        mapping_v2 = TurbineLogMapping(
            start_date="timestamp",  # STRING unique
            end_date="timestamp",
            name="name",
            oper="oper",
            status="status"
        )

        log_prepared2, start_col2, end_col2 = prepare_log_dataframe_with_mapping(  # noqa: E501
            log_df, mapping_v2
        )

        print(f"Après préparation:")
        print(f"  - Colonne start: {start_col2}")
        print(f"  - Colonne end: {end_col2}")
        print()

        # Utilisation avec create_time_mask
        print("3. Utilisation avec create_time_mask:")
        print("-" * 80)

        # Créer des données opérationnelles fictives
        operation_df = pd.DataFrame({
            'timestamp': pd.date_range(
                '2026-01-27 15:00:00', periods=100, freq='10min'
            ),
            'wind_speed': [5.0] * 100,
            'power': [1000.0] * 100,
        })

        manager = NordexN311LogCodeManager()

        # Utiliser la fonction de filtrage
        clean_data = manager.filter_by_codes(
            target_df=operation_df,
            log_df=log_prepared,
            code_column='oper',
            log_start_col=start_col,  # Utilise le nom de colonne préparé
            log_end_col=end_col,
            target_timestamp_col='timestamp',
            criticality_filter=[manager.get_codes_by_criticality],  # Exemple
            exclude_error_periods=True,
        )

        print(f"Données filtrées: {len(clean_data)} lignes")
        print()

    except FileNotFoundError:
        print("⚠️  Fichier de test non trouvé (normal en environnement test)")
        print()

    print("=" * 80)
    print("\n📋 Configuration YAML recommandée:")
    print()
    print("# Style 1: Date et time séparés (RECOMMANDÉ)")
    print("mapping_log_data:")
    print('  start_date: ["date", "time"]')
    print('  end_date: ["date", "time"]')
    print("  name: name")
    print("  oper: oper")
    print()
    print("# Style 2: Timestamp unique")
    print("mapping_log_data:")
    print("  start_date: timestamp")
    print("  end_date: timestamp")
    print("  name: name")
    print("  oper: oper")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
