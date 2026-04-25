"""
Tests unitaires pour les fonctionnalités de mode de réinitialisation (Reset Mode).
"""

import pytest
import pandas as pd
from pathlib import Path

from src.wind_turbine_analytics.data_processing.log_code.generator_type.nordex_n311_log_code_manager import (
    NordexN311LogCodeManager,
)
from src.wind_turbine_analytics.data_processing.log_code import (
    ResetMode,
    CodeCriticality,
)


class TestResetModeEnum:
    """Tests pour l'énumération ResetMode"""

    def test_reset_mode_values(self):
        """Vérifie que toutes les valeurs de ResetMode sont définies"""
        assert ResetMode.AUTOMATIC.value == "A"
        assert ResetMode.MANUAL.value == "M"
        assert ResetMode.SAFETY_LOCAL.value == "SL"
        assert ResetMode.SAFETY_REMOTE.value == "SR"
        assert ResetMode.MANUAL_AUTO.value == "M(A)"


class TestNordexN311ResetMode:
    """Tests pour les fonctionnalités Reset Mode dans NordexN311LogCodeManager"""

    @pytest.fixture
    def manager(self):
        """Fixture pour créer un manager"""
        return NordexN311LogCodeManager()

    def test_get_codes_by_reset_mode_manual(self, manager):
        """Test récupération des codes manuels"""
        manual_codes = manager.get_codes_by_reset_mode("M")
        assert isinstance(manual_codes, list)
        assert len(manual_codes) > 0

        # Vérifier que tous les codes retournés ont bien reset_mode = "M"
        for code in manual_codes:
            assert code.reset_mode == "M"

    def test_get_codes_by_reset_mode_automatic(self, manager):
        """Test récupération des codes automatiques"""
        auto_codes = manager.get_codes_by_reset_mode("A")
        assert isinstance(auto_codes, list)
        assert len(auto_codes) > 0

        for code in auto_codes:
            assert code.reset_mode == "A"

    def test_get_manual_intervention_codes(self, manager):
        """Test récupération de tous les codes nécessitant intervention manuelle"""
        intervention_codes = manager.get_manual_intervention_codes()
        assert isinstance(intervention_codes, list)
        assert len(intervention_codes) > 0

        # Vérifier que tous ont reset_mode dans ["M", "SL", "M(A)"]
        for code in intervention_codes:
            assert code.reset_mode in ["M", "SL", "M(A)"]

    def test_get_remote_resettable_codes(self, manager):
        """Test récupération des codes réinitialisables à distance"""
        remote_codes = manager.get_remote_resettable_codes()
        assert isinstance(remote_codes, list)
        assert len(remote_codes) > 0

        # Vérifier que tous ont reset_mode dans ["A", "SR"]
        for code in remote_codes:
            assert code.reset_mode in ["A", "SR"]

    def test_get_codes_requiring_site_visit(self, manager):
        """Test récupération des codes nécessitant visite sur site"""
        site_visit_codes = manager.get_codes_requiring_site_visit()
        assert isinstance(site_visit_codes, list)

        # Vérifier que tous ont reset_mode dans ["M", "SL"]
        for code in site_visit_codes:
            assert code.reset_mode in ["M", "SL"]

    def test_reset_mode_severity_mapping(self, manager):
        """Test que le mapping de sévérité est correct"""
        assert hasattr(manager, "RESET_MODE_SEVERITY")
        assert ResetMode.AUTOMATIC in manager.RESET_MODE_SEVERITY
        assert manager.RESET_MODE_SEVERITY[ResetMode.AUTOMATIC] == 0
        assert manager.RESET_MODE_SEVERITY[ResetMode.MANUAL] == 4

    def test_specific_code_reset_mode(self, manager):
        """Test le reset_mode de codes spécifiques connus"""
        # FM104 est connu pour être un code manuel critique
        code_fm104 = manager.get_code("FM104")
        assert code_fm104 is not None
        assert code_fm104.reset_mode in ["M", "M(A)"]

        # FM0 est "System OK" donc automatique
        code_fm0 = manager.get_code("FM0")
        assert code_fm0 is not None
        assert code_fm0.reset_mode == "A"


class TestResetModeFiltering:
    """Tests pour le filtrage par reset mode"""

    @pytest.fixture
    def manager(self):
        """Fixture pour créer un manager"""
        return NordexN311LogCodeManager()

    @pytest.fixture
    def sample_data(self):
        """Fixture pour créer des données de test"""
        operation_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='10min'),
            'wind_speed': [5.0] * 100,
            'power': [1000.0] * 100,
        })

        log_data = pd.DataFrame({
            'start_date': pd.to_datetime(['2024-01-01 02:00:00', '2024-01-01 05:00:00']),
            'end_date': pd.to_datetime(['2024-01-01 04:00:00', '2024-01-01 07:00:00']),
            'oper': ['FM104', 'FM0'],  # Manuel et automatique
        })

        return operation_data, log_data

    def test_create_time_mask_with_reset_mode_filter(self, manager, sample_data):
        """Test création d'un masque avec filtre reset_mode"""
        operation_data, log_data = sample_data

        # Filtrer uniquement les codes manuels
        mask = manager.create_time_mask(
            log_df=log_data,
            target_df=operation_data,
            code_column='oper',
            log_start_col='start_date',
            log_end_col='end_date',
            target_timestamp_col='timestamp',
            reset_mode_filter=["M", "M(A)"],
        )

        assert isinstance(mask, pd.Series)
        assert len(mask) == len(operation_data)
        assert mask.dtype == bool

        # Il devrait y avoir des False (périodes filtrées)
        assert not mask.all()

    def test_filter_by_codes_with_reset_mode(self, manager, sample_data):
        """Test filtrage d'un DataFrame avec reset_mode_filter"""
        operation_data, log_data = sample_data

        # Exclure les périodes avec codes manuels
        clean_data = manager.filter_by_codes(
            target_df=operation_data,
            log_df=log_data,
            code_column='oper',
            log_start_col='start_date',
            log_end_col='end_date',
            target_timestamp_col='timestamp',
            reset_mode_filter=["M", "M(A)"],
            exclude_error_periods=True,
        )

        assert isinstance(clean_data, pd.DataFrame)
        assert len(clean_data) < len(operation_data)

    def test_combined_filters(self, manager, sample_data):
        """Test filtrage combiné criticité + reset_mode"""
        operation_data, log_data = sample_data

        # Filtrer les codes CRITIQUES ET manuels
        mask = manager.create_time_mask(
            log_df=log_data,
            target_df=operation_data,
            code_column='oper',
            log_start_col='start_date',
            log_end_col='end_date',
            target_timestamp_col='timestamp',
            criticality_filter=[CodeCriticality.CRITICAL],
            reset_mode_filter=["M"],
        )

        assert isinstance(mask, pd.Series)
        assert len(mask) == len(operation_data)


class TestOperationalImpactAnalysis:
    """Tests pour l'analyse d'impact opérationnel"""

    @pytest.fixture
    def manager(self):
        """Fixture pour créer un manager"""
        return NordexN311LogCodeManager()

    @pytest.fixture
    def sample_log_data(self):
        """Fixture pour créer des logs de test"""
        return pd.DataFrame({
            'start_date': pd.to_datetime(['2024-01-01 02:00:00', '2024-01-01 05:00:00']),
            'end_date': pd.to_datetime(['2024-01-01 04:00:00', '2024-01-01 07:00:00']),
            'oper': ['FM104', 'FM6'],  # Codes manuels
        })

    def test_analyze_operational_impact(self, manager, sample_log_data):
        """Test analyse d'impact opérationnel"""
        impact = manager.analyze_operational_impact(sample_log_data, 'oper')

        assert isinstance(impact, dict)
        assert 'reset_mode_distribution' in impact
        assert 'site_visit_codes_count' in impact
        assert 'total_site_visit_occurrences' in impact
        assert 'automatic_codes_count' in impact
        assert 'remote_resettable_count' in impact

        # Vérifier la structure de reset_mode_distribution
        distribution = impact['reset_mode_distribution']
        assert 'automatic' in distribution
        assert 'remote_reset' in distribution
        assert 'manual_possible' in distribution
        assert 'site_visit_required' in distribution

    def test_site_visit_count(self, manager, sample_log_data):
        """Test comptage des visites sur site nécessaires"""
        impact = manager.analyze_operational_impact(sample_log_data, 'oper')

        # FM104 et FM6 sont des codes manuels
        assert impact['site_visit_codes_count'] >= 0
        assert impact['total_site_visit_occurrences'] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
