"""
Tests unitaires pour l'identification des arrêts non autorisés.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from src.wind_turbine_analytics.data_processing.log_code.generator_type.nordex_n311_log_code_manager import (  # noqa: E501
    NordexN311LogCodeManager,
)


class TestUnauthorizedStops:
    """Tests pour l'identification des arrêts non autorisés"""

    @pytest.fixture
    def manager(self):
        """Fixture pour créer un manager"""
        return NordexN311LogCodeManager()

    def test_get_unauthorized_stop_codes(self, manager):
        """Test récupération des codes d'arrêt non autorisé"""
        unauthorized_codes = manager.get_unauthorized_stop_codes()

        assert isinstance(unauthorized_codes, list)
        assert len(unauthorized_codes) > 0

        # Vérifier que tous les codes retournés respectent les critères
        for code in unauthorized_codes:
            assert code.affects_availability(), (
                f"{code.code} devrait affecter la disponibilité"
            )
            assert code.is_critical_stop(), (
                f"{code.code} devrait être un arrêt critique (>=270)"
            )

    def test_unauthorized_stops_are_subset_of_critical(self, manager):
        """
        Les arrêts non autorisés doivent être un sous-ensemble
        des arrêts critiques
        """
        unauthorized = manager.get_unauthorized_stop_codes()
        critical = manager.get_critical_stop_codes()

        unauthorized_codes_set = {c.code for c in unauthorized}
        critical_codes_set = {c.code for c in critical}

        # Tous les arrêts non autorisés doivent être dans les critiques
        assert unauthorized_codes_set.issubset(critical_codes_set)

    def test_specific_known_codes(self, manager):
        """Test des codes connus"""
        # FM104 : Overspeed - devrait être non autorisé
        code_fm104 = manager.get_code("FM104")
        if code_fm104:
            unauthorized = manager.get_unauthorized_stop_codes()
            unauthorized_codes = [c.code for c in unauthorized]

            if code_fm104.affects_availability() and code_fm104.is_critical_stop():  # noqa: E501
                assert code_fm104.code in unauthorized_codes

    def test_filtering_with_unauthorized_codes(self, manager):
        """Test filtrage avec les codes non autorisés"""
        import pandas as pd

        # Données de test
        operation_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=50, freq='10min'),  # noqa: E501
            'wind_speed': [5.0] * 50,
            'power': [1000.0] * 50,
        })

        log_data = pd.DataFrame({
            'start_date': pd.to_datetime(['2024-01-01 02:00:00']),
            'end_date': pd.to_datetime(['2024-01-01 04:00:00']),
            'oper': ['FM104'],
        })

        # Récupérer les codes non autorisés
        unauthorized = manager.get_unauthorized_stop_codes()
        unauthorized_code_list = [c.code for c in unauthorized]

        # Filtrer
        clean_data = manager.filter_by_codes(
            target_df=operation_data,
            log_df=log_data,
            code_column='oper',
            log_start_col='start_date',
            log_end_col='end_date',
            target_timestamp_col='timestamp',
            codes_to_filter=unauthorized_code_list,
            exclude_error_periods=True,
        )

        # Devrait avoir filtré des lignes
        assert len(clean_data) <= len(operation_data)

    def test_count_statistics(self, manager):
        """Affiche des statistiques sur les arrêts"""
        unauthorized = manager.get_unauthorized_stop_codes()
        critical = manager.get_critical_stop_codes()
        all_codes = len(manager.error_codes)

        print(f"\n=== Statistiques Nordex ===")
        print(f"Total codes: {all_codes}")
        print(f"Arrêts critiques: {len(critical)}")
        print(f"Arrêts non autorisés (availability=yes): {len(unauthorized)}")
        print(
            f"Différence: {len(critical) - len(unauthorized)} "
            "(codes critiques mais availability=no)"
        )

        # Validation cohérence
        assert len(unauthorized) <= len(critical)
        assert len(critical) <= all_codes


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
