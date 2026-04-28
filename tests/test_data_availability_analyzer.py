"""
Tests unitaires pour DataAvailabilityAnalyzer
Valide le calcul de disponibilité par plages horaires (1h) avec vérification sur 5 minutes.
"""

import sys
from pathlib import Path

# Ajouter le projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.wind_turbine_analytics.data_processing.analyzer.logics.data_availability_analyzer import (
    DataAvailabilityAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    ValidationCriteria,
    TurbineMappingOperationData,
)


@pytest.fixture
def turbine_config():
    """Configuration de turbine pour les tests."""
    test_start = datetime(2026, 1, 1, 0, 0, 0)
    test_end = datetime(2026, 1, 4, 0, 0, 0)  # 3 jours de test

    mapping = TurbineMappingOperationData(
        timestamp="timestamp",
        wind_speed="wind_speed",
        activation_power="active_power",
        temperature="temperature",
        wind_direction="wind_direction",
    )

    return TurbineConfig(
        turbine_id="T01",
        test_start=test_start,
        test_end=test_end,
        mapping_operation_data=mapping,
    )


@pytest.fixture
def criteria():
    """Critères de validation (non utilisés ici mais requis par l'interface)."""
    return ValidationCriteria()


def test_fully_available_data(turbine_config, criteria):
    """Test avec données complètement disponibles."""
    # Créer des données toutes les 5 minutes pendant 3 jours
    timestamps = pd.date_range(
        start=turbine_config.test_start,
        end=turbine_config.test_end,
        freq="5min"
    )

    operation_data = pd.DataFrame({
        "timestamp": timestamps,
        "wind_speed": [10.5] * len(timestamps),
        "active_power": [2000.0] * len(timestamps),
        "temperature": [15.0] * len(timestamps),
        "wind_direction": [180.0] * len(timestamps),
    })

    log_data = pd.DataFrame()

    analyzer = DataAvailabilityAnalyzer()
    result = analyzer._compute(
        operation_data=operation_data,
        log_data=log_data,
        turbine_config=turbine_config,
        criteria=criteria,
    )

    # Vérifier que la disponibilité est à 100%
    assert result["summary"]["overall_availability_pct"] == 100.0
    assert result["summary"]["wind_speed_availability_pct"] == 100.0
    assert result["summary"]["active_power_availability_pct"] == 100.0
    assert result["summary"]["wind_direction_availability_pct"] == 100.0

    # Vérifier la taille du vecteur (3 jours = 3 intervalles)
    availability_df = result["availability_table"]
    assert len(availability_df) == 3
    assert all(availability_df["overall"] == 1)


def test_missing_data_in_one_5min_interval(turbine_config, criteria):
    """
    Test avec plus de 20% des données manquantes le premier jour.
    Le jour entier devrait être marqué comme indisponible (0).
    """
    # Créer des données toutes les 5 minutes pendant 3 jours
    timestamps = pd.date_range(
        start=turbine_config.test_start,
        end=turbine_config.test_end,
        freq="5min"
    )

    operation_data = pd.DataFrame({
        "timestamp": timestamps,
        "wind_speed": [10.5] * len(timestamps),
        "active_power": [2000.0] * len(timestamps),
        "temperature": [15.0] * len(timestamps),
        "wind_direction": [180.0] * len(timestamps),
    })

    # Supprimer 25% des données du premier jour (>20% donc indisponible)
    day1_indices = operation_data[
        operation_data["timestamp"] < datetime(2026, 1, 2, 0, 0, 0)
    ].index
    # Garder seulement 75% des données (enlever 25%)
    indices_to_drop = day1_indices[::4]  # Supprimer 1 sur 4
    operation_data = operation_data.drop(indices_to_drop)

    log_data = pd.DataFrame()

    analyzer = DataAvailabilityAnalyzer()
    result = analyzer._compute(
        operation_data=operation_data,
        log_data=log_data,
        turbine_config=turbine_config,
        criteria=criteria,
    )

    availability_df = result["availability_table"]

    # Le premier jour devrait être indisponible (0) car <80% de données
    assert availability_df.iloc[0]["wind_speed"] == 0
    assert availability_df.iloc[0]["overall"] == 0

    # Les autres jours devraient être disponibles (1)
    assert availability_df.iloc[1]["wind_speed"] == 1
    assert availability_df.iloc[2]["wind_speed"] == 1

    # Disponibilité globale : 2/3 = 66.67%
    wind_speed_pct = result["summary"]["wind_speed_availability_pct"]
    assert wind_speed_pct == pytest.approx(66.67, abs=0.1)


def test_completely_missing_data(turbine_config, criteria):
    """Test avec toutes les données manquantes."""
    # Créer des données avec valeurs nulles
    timestamps = pd.date_range(
        start=turbine_config.test_start,
        end=turbine_config.test_end,
        freq="5min"
    )

    operation_data = pd.DataFrame({
        "timestamp": timestamps,
        "wind_speed": [None] * len(timestamps),
        "active_power": [None] * len(timestamps),
        "temperature": [None] * len(timestamps),
        "wind_direction": [None] * len(timestamps),
    })

    log_data = pd.DataFrame()

    analyzer = DataAvailabilityAnalyzer()
    result = analyzer._compute(
        operation_data=operation_data,
        log_data=log_data,
        turbine_config=turbine_config,
        criteria=criteria,
    )

    # Disponibilité devrait être à 0%
    assert result["summary"]["overall_availability_pct"] == 0.0
    assert result["summary"]["wind_speed_availability_pct"] == 0.0

    # Tous les jours devraient être marqués comme indisponibles
    availability_df = result["availability_table"]
    assert all(availability_df["overall"] == 0)


def test_partial_availability_multiple_days(turbine_config, criteria):
    """Test avec différents jours ayant différentes disponibilités."""
    timestamps = pd.date_range(
        start=turbine_config.test_start,
        end=turbine_config.test_end,
        freq="5min"
    )

    operation_data = pd.DataFrame({
        "timestamp": timestamps,
        "wind_speed": [10.5] * len(timestamps),
        "active_power": [2000.0] * len(timestamps),
        "temperature": [15.0] * len(timestamps),
        "wind_direction": [180.0] * len(timestamps),
    })

    # Jour 1 : Supprimer 30% des lignes pour avoir <80%
    day1_mask = operation_data["timestamp"] < datetime(2026, 1, 2, 0, 0, 0)
    day1_indices = operation_data[day1_mask].index
    drop_indices_day1 = day1_indices[::3]  # Supprimer 1 sur 3
    operation_data = operation_data.drop(drop_indices_day1)

    # Jour 3 : Supprimer 30% des lignes aussi
    day3_mask = operation_data["timestamp"] >= datetime(2026, 1, 3, 0, 0, 0)
    day3_indices = operation_data[day3_mask].index
    drop_indices_day3 = day3_indices[::3]
    operation_data = operation_data.drop(drop_indices_day3)

    log_data = pd.DataFrame()

    analyzer = DataAvailabilityAnalyzer()
    result = analyzer._compute(
        operation_data=operation_data,
        log_data=log_data,
        turbine_config=turbine_config,
        criteria=criteria,
    )

    availability_df = result["availability_table"]

    # Vérifier les disponibilités par jour
    assert availability_df.iloc[0]["overall"] == 0  # Jour 1: <80%
    assert availability_df.iloc[1]["overall"] == 1  # Jour 2: 100%
    assert availability_df.iloc[2]["overall"] == 0  # Jour 3: <80%

    # Disponibilité globale : 1/3 = 33.33%
    overall_pct = result["summary"]["overall_availability_pct"]
    assert overall_pct == pytest.approx(33.33, abs=0.1)


def test_reduced_output_size():
    """Test pour valider la réduction de taille du vecteur de sortie."""
    # Configuration pour 5 jours de test
    test_start = datetime(2026, 1, 1, 0, 0, 0)
    test_end = datetime(2026, 1, 6, 0, 0, 0)  # 5 jours = 120 heures

    mapping = TurbineMappingOperationData(
        timestamp="timestamp",
        wind_speed="wind_speed",
        activation_power="active_power",
        temperature="temperature",
        wind_direction="wind_direction",
    )

    turbine_config = TurbineConfig(
        turbine_id="T01",
        test_start=test_start,
        test_end=test_end,
        mapping_operation_data=mapping,
    )

    # Créer des données complètes
    timestamps = pd.date_range(start=test_start, end=test_end, freq="5min")
    operation_data = pd.DataFrame({
        "timestamp": timestamps,
        "wind_speed": [10.5] * len(timestamps),
        "active_power": [2000.0] * len(timestamps),
        "temperature": [15.0] * len(timestamps),
        "wind_direction": [180.0] * len(timestamps),
    })

    log_data = pd.DataFrame()

    analyzer = DataAvailabilityAnalyzer()
    result = analyzer._compute(
        operation_data=operation_data,
        log_data=log_data,
        turbine_config=turbine_config,
        criteria=ValidationCriteria(),
    )

    availability_df = result["availability_table"]

    # Ancienne approche (10min) : 5 jours * 24h * 6 = 720 lignes
    # Nouvelle approche (1 jour) : 5 jours = 5 lignes
    assert len(availability_df) == 5

    # Vérifier que tous les jours sont disponibles
    assert all(availability_df["overall"] == 1)

    print(f"✅ Taille du vecteur réduite : {len(availability_df)} lignes pour 5 jours")
    print(f"✅ Ratio de compression : {720 / len(availability_df):.1f}x")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
