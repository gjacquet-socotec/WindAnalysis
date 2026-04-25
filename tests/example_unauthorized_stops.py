"""
Exemple : Filtrage des arrêts non autorisés basé sur les données CSV.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.data_processing.log_code.generator_type.nordex_n311_log_code_manager import (  # noqa: E501
    NordexN311LogCodeManager,
)
import pandas as pd


def main():
    # Configuration encodage Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("FILTRAGE DES ARRÊTS NON AUTORISÉS")
    print("Basé sur les critères CSV : availability='yes' + dead_level>=270")
    print("=" * 80)
    print()

    # Initialiser le manager
    manager = NordexN311LogCodeManager()

    # 1. Récupérer les arrêts non autorisés
    print("1. Identification des arrêts non autorisés:")
    print("-" * 80)

    unauthorized = manager.get_unauthorized_stop_codes()
    print(f"Total: {len(unauthorized)} codes")
    print()
    print("Critères (basés sur CSV Nordex):")
    print("  - availability = 'yes'")
    print("  - dead_level >= 270")
    print()

    # Exemples
    print("Exemples (10 premiers):")
    for code in unauthorized[:10]:
        print(
            f"  {code.code} [Reset:{code.reset_mode}] "
            f"(DL={code.dead_level}, Avail={code.availability})"
        )
        print(f"    {code.description[:65]}...")
    print()

    # 2. Comparaison
    print("2. Statistiques:")
    print("-" * 80)
    critical_all = manager.get_critical_stop_codes()
    print(f"Arrêts critiques (dead_level>=270): {len(critical_all)}")
    print(f"Arrêts non autorisés (+ availability=yes): {len(unauthorized)}")
    print(
        f"Différence: {len(critical_all) - len(unauthorized)} codes "
        "critiques sans impact disponibilité"
    )
    print()

    # 3. Analyse par reset_mode
    print("3. Répartition par mode de réinitialisation:")
    print("-" * 80)
    reset_modes = {}
    for code in unauthorized:
        mode = code.reset_mode
        reset_modes[mode] = reset_modes.get(mode, 0) + 1

    for mode, count in sorted(reset_modes.items(), key=lambda x: -x[1]):
        print(f"  {mode}: {count} codes")
    print()

    # 4. Exemple de filtrage
    print("4. Exemple de filtrage des données:")
    print("-" * 80)

    # Créer des données de test
    operation_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='10min'),
        'wind_speed': [5.0] * 100,
        'power': [1000.0] * 100,
    })

    log_data = pd.DataFrame({
        'start_date': pd.to_datetime([
            '2024-01-01 02:00:00',
            '2024-01-01 05:00:00'
        ]),
        'end_date': pd.to_datetime([
            '2024-01-01 04:00:00',
            '2024-01-01 07:00:00'
        ]),
        'oper': ['FM104', 'FM51'],  # Deux arrêts non autorisés
    })

    print(f"Données opérationnelles: {len(operation_data)} lignes")
    print(f"Événements d'arrêt: {len(log_data)}")
    print()

    # Filtrer en excluant les arrêts non autorisés
    unauthorized_list = [c.code for c in unauthorized]
    clean_data = manager.filter_by_codes(
        target_df=operation_data,
        log_df=log_data,
        code_column='oper',
        log_start_col='start_date',
        log_end_col='end_date',
        target_timestamp_col='timestamp',
        codes_to_filter=unauthorized_list,
        exclude_error_periods=True,
    )

    print(f"Après filtrage: {len(clean_data)} lignes")
    print(f"Lignes filtrées: {len(operation_data) - len(clean_data)}")
    print()

    # 5. Alternative : utiliser les méthodes existantes
    print("5. Approche flexible (combinaison de filtres):")
    print("-" * 80)
    print("Vous pouvez aussi combiner les méthodes existantes:")
    print()
    print("# Filtrer par criticality + availability")
    print("mask = manager.create_time_mask(")
    print("    criticality_filter=[CodeCriticality.CRITICAL],")
    print("    # Puis filtrer manuellement sur availability")
    print(")")
    print()

    print("=" * 80)


if __name__ == "__main__":
    main()
