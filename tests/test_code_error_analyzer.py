"""
Tests unitaires pour CodeErrorAnalyzer.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
from datetime import datetime, timedelta

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.data_processing.analyzer.logics.code_error_analyzer import (
    CodeErrorAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineLogMapping,
    ValidationCriteria,
    Criterion,
    TurbineFarm,
)


@pytest.fixture
def sample_operation_data():
    """Génère des données d'opération factices."""
    start = datetime(2024, 1, 1, 0, 0, 0)
    timestamps = [start + timedelta(minutes=10 * i) for i in range(500)]

    return pd.DataFrame({
        "timestamp": timestamps,
        "wind_speed": [5.5 + i % 10 for i in range(500)],
        "power": [1000 + i % 3000 for i in range(500)],
    })


@pytest.fixture
def sample_log_data():
    """Génère des logs d'erreur factices."""
    start = datetime(2024, 1, 1, 0, 0, 0)

    return pd.DataFrame({
        "start_date": [
            start + timedelta(hours=2),
            start + timedelta(hours=5),
            start + timedelta(hours=10),
            start + timedelta(hours=15),
            start + timedelta(hours=20),
        ],
        "end_date": [
            start + timedelta(hours=2, minutes=30),
            start + timedelta(hours=5, minutes=15),
            start + timedelta(hours=10, minutes=45),
            start + timedelta(hours=15, minutes=20),
            start + timedelta(hours=20, minutes=10),
        ],
        "code": ["FM6", "FM7", "FM615", "FM6", "FM920"],
        "name": [
            "Grid fault",
            "Grid fault",
            "Manual stop",
            "Grid fault",
            "High wind",
        ],
        "status": ["ON", "ON", "ON", "ON", "ON"],
    })


@pytest.fixture
def turbine_config():
    """Configuration de turbine factice."""
    return TurbineConfig(
        turbine_id="TEST_TURBINE",
        general_information=TurbineGeneralInformation(
            model="Nordex N131",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data="dummy.csv",
            path_log_data="dummy_log.csv",
        ),
        mapping_operation_data=TurbineMappingOperationData(
            timestamp="timestamp",
            wind_speed="wind_speed",
            activation_power="power",
        ),
        mapping_log_data=TurbineLogMapping(
            start_date="start_date",
            end_date="end_date",
            oper="code",
            name="name",
            status="status",
        ),
        test_start="01/01/2024 00:00:00",
        test_end="03/01/2024 00:00:00",
    )


@pytest.fixture
def criteria():
    """Critères de validation factices."""
    return ValidationCriteria(
        validation_criterion={
            "consecutive_hours": Criterion(value=120, unit="h"),
        }
    )


def test_code_error_analyzer_initialization():
    """Test l'initialisation du CodeErrorAnalyzer."""
    analyzer = CodeErrorAnalyzer()
    assert analyzer is not None


def test_compute_with_sample_data(
    sample_operation_data, sample_log_data, turbine_config, criteria
):
    """Test la méthode _compute avec des données factices."""
    analyzer = CodeErrorAnalyzer()

    result = analyzer._compute(
        sample_operation_data, sample_log_data, turbine_config, criteria
    )

    # Vérifier la structure du résultat
    assert "summary" in result
    assert "code_frequency" in result
    assert "criticality_distribution" in result
    assert "system_distribution" in result
    assert "production_impact" in result
    assert "wind_correlation" in result
    assert "most_impactful_codes" in result

    # Vérifier le résumé
    summary = result["summary"]
    assert summary["turbine_id"] == "TEST_TURBINE"
    assert summary["total_error_events"] > 0
    assert summary["unique_error_codes"] > 0
    assert summary["test_period_hours"] > 0


def test_code_frequency_analysis(
    sample_operation_data, sample_log_data, turbine_config, criteria
):
    """Test l'analyse de fréquence des codes."""
    analyzer = CodeErrorAnalyzer()

    result = analyzer._compute(
        sample_operation_data, sample_log_data, turbine_config, criteria
    )

    code_freq = result["code_frequency"]

    # Vérifier que les codes sont présents
    assert len(code_freq) > 0

    # Vérifier la structure de chaque code
    for code_info in code_freq:
        assert "code" in code_info
        assert "count" in code_info
        assert "frequency_percent" in code_info
        assert "description" in code_info
        assert "criticality" in code_info
        assert "system" in code_info

    # Vérifier que les codes sont triés par fréquence décroissante
    counts = [c["count"] for c in code_freq]
    assert counts == sorted(counts, reverse=True)


def test_criticality_distribution(
    sample_operation_data, sample_log_data, turbine_config, criteria
):
    """Test la répartition par criticité."""
    analyzer = CodeErrorAnalyzer()

    result = analyzer._compute(
        sample_operation_data, sample_log_data, turbine_config, criteria
    )

    crit_dist = result["criticality_distribution"]

    # Vérifier que chaque niveau de criticité a la bonne structure
    for crit_level, stats in crit_dist.items():
        assert "unique_codes" in stats
        assert "total_occurrences" in stats
        assert "percent_of_total" in stats
        assert "codes" in stats

        # Vérifier que les pourcentages sont valides
        assert 0 <= stats["percent_of_total"] <= 100


def test_production_impact_analysis(
    sample_operation_data, sample_log_data, turbine_config, criteria
):
    """Test l'analyse d'impact sur la production."""
    analyzer = CodeErrorAnalyzer()

    result = analyzer._compute(
        sample_operation_data, sample_log_data, turbine_config, criteria
    )

    impact = result["production_impact"]

    # Vérifier la structure
    assert "mean_power_with_errors_kW" in impact
    assert "mean_power_without_errors_kW" in impact
    assert "production_loss_percent" in impact
    assert "periods_with_critical_errors_count" in impact
    assert "periods_without_errors_count" in impact

    # Vérifier que les valeurs sont raisonnables
    assert impact["mean_power_with_errors_kW"] >= 0
    assert impact["mean_power_without_errors_kW"] >= 0


def test_wind_correlation_analysis(
    sample_operation_data, sample_log_data, turbine_config, criteria
):
    """Test l'analyse de corrélation avec le vent."""
    analyzer = CodeErrorAnalyzer()

    result = analyzer._compute(
        sample_operation_data, sample_log_data, turbine_config, criteria
    )

    wind = result["wind_correlation"]

    # Vérifier la structure
    assert "mean_wind_with_errors_ms" in wind
    assert "mean_wind_without_errors_ms" in wind
    assert "wind_ranges" in wind

    # Vérifier que les plages de vent ont la bonne structure
    for wind_range, stats in wind["wind_ranges"].items():
        assert "error_periods" in stats
        assert "total_periods" in stats
        assert "error_rate_percent" in stats
        assert 0 <= stats["error_rate_percent"] <= 100


def test_most_impactful_codes(
    sample_operation_data, sample_log_data, turbine_config, criteria
):
    """Test l'identification des codes les plus impactants."""
    analyzer = CodeErrorAnalyzer()

    result = analyzer._compute(
        sample_operation_data, sample_log_data, turbine_config, criteria
    )

    impactful = result["most_impactful_codes"]

    # Vérifier la structure
    assert len(impactful) > 0

    for code_info in impactful:
        assert "code" in code_info
        assert "occurrences" in code_info
        assert "total_duration_hours" in code_info
        assert "criticality" in code_info
        assert "description" in code_info

    # Vérifier que les codes sont triés par durée décroissante
    durations = [c["total_duration_hours"] for c in impactful]
    assert durations == sorted(durations, reverse=True)


def test_empty_log_data(sample_operation_data, turbine_config, criteria):
    """Test avec des logs vides."""
    analyzer = CodeErrorAnalyzer()

    empty_log = pd.DataFrame(columns=["start_date", "end_date", "code", "name", "status"])

    result = analyzer._compute(
        sample_operation_data, empty_log, turbine_config, criteria
    )

    # Doit retourner une erreur
    assert "error" in result
    assert result["total_codes"] == 0


def test_analyze_method_with_turbine_farm(
    sample_operation_data, sample_log_data, turbine_config, criteria
):
    """Test la méthode analyze avec un TurbineFarm."""
    # Note: Ce test nécessiterait de mocker load_csv
    # Pour l'instant, on teste juste que la méthode existe
    analyzer = CodeErrorAnalyzer()
    assert hasattr(analyzer, "analyze")


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
