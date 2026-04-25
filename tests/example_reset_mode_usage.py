"""
Exemple d'utilisation des modes de réinitialisation (Reset Mode).
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
    # Configuration de l'encodage pour Windows
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    # Initialiser le manager
    manager = NordexN311LogCodeManager()

    print("=" * 80)
    print("EXEMPLE D'UTILISATION DES MODES DE RÉINITIALISATION")
    print("=" * 80)
    print()

    # 1. Récupérer les codes par mode de reset
    print("1️⃣  Codes par mode de réinitialisation:")
    print("-" * 80)

    manual_codes = manager.get_codes_by_reset_mode("M")
    print(f"Codes nécessitant intervention manuelle (M): {len(manual_codes)}")
    for code in manual_codes[:10]:
        print(f"   - {code.code}: {code.description[:60]}...")

    print()
    auto_codes = manager.get_codes_by_reset_mode("A")
    print(f"Codes avec reset automatique (A): {len(auto_codes)}")

    print()
    print()

    # 2. Codes nécessitant intervention humaine
    print("2️⃣  Codes nécessitant une intervention humaine (M, SL, M(A)):")
    print("-" * 80)

    intervention_codes = manager.get_manual_intervention_codes()
    print(f"Total: {len(intervention_codes)} codes")

    print()
    print()

    # 3. Codes réinitialisables à distance
    print("3️⃣  Codes réinitialisables à distance (A, SR):")
    print("-" * 80)

    remote_codes = manager.get_remote_resettable_codes()
    print(f"Total: {len(remote_codes)} codes")

    print()
    print()

    # 4. Codes nécessitant déplacement sur site
    print("4️⃣  Codes nécessitant un déplacement sur site:")
    print("-" * 80)

    site_visit_codes = manager.get_codes_requiring_site_visit()
    print(f"Total: {len(site_visit_codes)} codes nécessitant visite sur site")
    for code in site_visit_codes[:5]:
        print(f"   - {code.code} [{code.reset_mode}]: {code.description[:60]}...")

    print()
    print()

    # 5. Exemple de filtrage combiné
    print("5️⃣  Filtrage combiné (Criticité + Reset Mode):")
    print("-" * 80)
    print(
        "Exemple: Créer un masque pour exclure les erreurs CRITIQUES "
        "nécessitant intervention manuelle"
    )
    print()

    # Simuler des données
    operation_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='10min'),
        'wind_speed': [5.0] * 100,
        'power': [1000.0] * 100,
    })

    log_data = pd.DataFrame({
        'start_date': ['2024-01-01 02:00:00'],
        'end_date': ['2024-01-01 04:00:00'],
        'oper': ['FM104'],  # Code manuel critique
    })

    print(f"Données opérationnelles: {len(operation_data)} lignes")
    print(f"Logs d'erreur: {len(log_data)} événements")
    print()

    # Créer un masque avec filtre reset_mode
    mask = manager.create_time_mask(
        log_df=log_data,
        target_df=operation_data,
        code_column='oper',
        log_start_col='start_date',
        log_end_col='end_date',
        target_timestamp_col='timestamp',
        reset_mode_filter=["M", "SL"],  # Filtrer seulement les manuels
    )

    clean_data = operation_data[mask]
    print(f"Après filtrage des codes manuels: {len(clean_data)} lignes restantes")
    print(f"Lignes filtrées: {len(operation_data) - len(clean_data)}")

    print()
    print()

    # 6. Analyse d'impact opérationnel (si des logs existent)
    print("6️⃣  Analyse d'impact opérationnel:")
    print("-" * 80)

    if not log_data.empty:
        impact_analysis = manager.analyze_operational_impact(
            log_data, 'oper'
        )
        site_visit = impact_analysis['site_visit_codes_count']
        total_occurrences = impact_analysis['total_site_visit_occurrences']
        auto_count = impact_analysis['automatic_codes_count']
        remote_count = impact_analysis['remote_resettable_count']

        print(f"Codes nécessitant visite site: {site_visit}")
        print(f"Occurrences totales nécessitant visite: {total_occurrences}")
        print(f"Codes automatiques: {auto_count}")
        print(f"Codes réinitialisables à distance: {remote_count}")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
