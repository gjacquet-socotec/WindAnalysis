"""
Tests unitaires pour AutonomousOperationAnalyzer.

Vérifie que l'analyseur identifie correctement les codes nécessitant
un redémarrage manuel et valide le critère d'autonomie d'exploitation.
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import pytest
from src.wind_turbine_analytics.data_processing.analyzer.logics.autonomous_operation import (
    AutonomousOperationAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineLogMapping,
    ValidationCriteria,
    Criterion,
)


@pytest.fixture
def turbine_config_with_logs():
    """Configuration de turbine avec données de log pour les tests."""
    return TurbineConfig(
        turbine_id="E1",
        general_information=TurbineGeneralInformation(
            model="Nordex N131 - 3.78MW",
            nominal_power=3.78,
            constructor="Nordex",
            path_operation_data="./experiments/real_run_test/DATA/E1/tenMinTimeSeries-01WEA95986-Mean-1260206141902.csv",
            path_log_data="./experiments/real_run_test/DATA/E1/alarmLog-01WEA95986-1260206141836.csv",
        ),
        mapping_operation_data=TurbineMappingOperationData(
            timestamp="Date",
            wind_speed="01WEA95986 MET Wind Speed",
            activation_power="01WEA95986 GRD ActivePower",
        ),
        mapping_log_data=TurbineLogMapping(
            start_date=["date", "time"],
            end_date=["date", "time"],
            name="oper",
            oper="name",
            status="status",
        ),
        test_start="01.02.2026 00:00:00",
        test_end="05.02.2026 23:50:00",
    )


@pytest.fixture
def validation_criteria():
    """Critères de validation avec seuil de 3 redémarrages manuels."""
    return ValidationCriteria(
        validation_criterion={
            "local_restarts": Criterion(
                value=3,
                unit="nb",
                specification=None,
                description="Nombre maximal de redémarrages manuels autorisés",
            )
        }
    )


@pytest.fixture
def sample_operation_data():
    """Données d'opération factices pour les tests."""
    return pd.DataFrame(
        {
            "Date": pd.date_range("2026-02-01", periods=10, freq="10min"),
            "01WEA95986 MET Wind Speed": [5.0] * 10,
            "01WEA95986 GRD ActivePower": [2000.0] * 10,
        }
    )


def test_autonomous_operation_analyzer_initialization():
    """Test que l'analyseur s'initialise correctement."""
    analyzer = AutonomousOperationAnalyzer()
    assert analyzer is not None


def test_autonomous_operation_with_real_data(
    turbine_config_with_logs, validation_criteria, sample_operation_data
):
    """
    Test avec les vraies données de log E1.

    Selon le client: E1 a AUCUN code nécessitant redémarrage manuel/local.
    Le critère devrait donc être validé (count=0 <= threshold=3).
    """
    analyzer = AutonomousOperationAnalyzer()

    result = analyzer._compute(
        operation_data=sample_operation_data,
        turbine_config=turbine_config_with_logs,
        criteria=validation_criteria,
    )

    # Vérifications
    assert "manual_restart_count" in result
    assert "required_threshold" in result
    assert "criterion_met" in result
    assert "manual_restart_events" in result

    # Le seuil doit être 3 (depuis config)
    assert result["required_threshold"] == 3

    # Selon le client, E1 n'a pas de codes manuels
    assert result["manual_restart_count"] == 0
    assert result["criterion_met"] is True
    assert len(result["manual_restart_events"]) == 0

    print(f"\n✅ E1 Autonomie d'exploitation:")
    print(f"   Redémarrages manuels: {result['manual_restart_count']}")
    print(f"   Seuil: {result['required_threshold']}")
    print(f"   Critère validé: {result['criterion_met']}")


def test_autonomous_operation_format_output(
    turbine_config_with_logs, validation_criteria, sample_operation_data
):
    """Vérifie le format de sortie du résultat."""
    analyzer = AutonomousOperationAnalyzer()

    result = analyzer._compute(
        operation_data=sample_operation_data,
        turbine_config=turbine_config_with_logs,
        criteria=validation_criteria,
    )

    # Vérifier la structure du résultat
    required_keys = [
        "manual_restart_codes",
        "manual_restart_count",
        "required_threshold",
        "criterion_met",
        "manual_restart_events",
    ]

    for key in required_keys:
        assert key in result, f"Clé manquante: {key}"

    # Vérifier les types
    assert isinstance(result["manual_restart_codes"], list)
    assert isinstance(result["manual_restart_count"], int)
    assert isinstance(result["required_threshold"], (int, float))
    assert isinstance(result["criterion_met"], bool)
    assert isinstance(result["manual_restart_events"], list)

    # Si il y a des événements, vérifier leur structure
    for event in result["manual_restart_events"]:
        assert "timestamp" in event
        assert "code" in event
        assert "name" in event
        assert "status" in event


def test_all_turbines_autonomous_operation():
    """
    Test sur toutes les turbines E1, E6, E8.

    Selon le client, aucune turbine n'a de code nécessitant redémarrage manuel.
    """
    turbines_data = {
        "E1": {
            "log_path": "./experiments/real_run_test/DATA/E1/alarmLog-01WEA95986-1260206141836.csv",
            "power_col": "01WEA95986 GRD ActivePower",
            "wind_col": "01WEA95986 MET Wind Speed",
        },
        "E6": {
            "log_path": "./experiments/real_run_test/DATA/E6/alarmLog-06WEA95990-1260206135808.csv",
            "power_col": "06WEA95990 GRD ActivePower",
            "wind_col": "06WEA95990 MET Wind Speed",
        },
        "E8": {
            "log_path": "./experiments/real_run_test/DATA/E8/alarmLog-08WEA95991-1260206133630.csv",
            "power_col": "08WEA95991 GRD ActivePower",
            "wind_col": "08WEA95991 MET Wind Speed",
        },
    }

    analyzer = AutonomousOperationAnalyzer()
    validation_criteria = ValidationCriteria(
        validation_criterion={
            "local_restarts": Criterion(value=3, unit="nb", specification=None)
        }
    )

    results = {}

    for turbine_id, turbine_data in turbines_data.items():
        config = TurbineConfig(
            turbine_id=turbine_id,
            general_information=TurbineGeneralInformation(
                model="Nordex N131 - 3.78MW",
                nominal_power=3.78,
                constructor="Nordex",
                path_log_data=turbine_data["log_path"],
            ),
            mapping_operation_data=TurbineMappingOperationData(
                timestamp="Date",
                wind_speed=turbine_data["wind_col"],
                activation_power=turbine_data["power_col"],
            ),
            mapping_log_data=TurbineLogMapping(
                start_date=["date", "time"],
                end_date=["date", "time"],
                name="oper",
                oper="name",
                status="status",
            ),
            test_start="01.02.2026 00:00:00",
            test_end="05.02.2026 23:50:00",
        )

        sample_data = pd.DataFrame(
            {
                "Date": pd.date_range("2026-02-01", periods=10, freq="10min"),
                turbine_data["wind_col"]: [5.0] * 10,
                turbine_data["power_col"]: [2000.0] * 10,
            }
        )

        result = analyzer._compute(
            operation_data=sample_data,
            turbine_config=config,
            criteria=validation_criteria,
        )

        results[turbine_id] = result

    # Afficher le résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ - Autonomie d'exploitation pour toutes les turbines")
    print("=" * 60)

    for turbine_id, result in results.items():
        print(f"\n{turbine_id}:")
        print(f"  Redémarrages manuels: {result['manual_restart_count']}")
        print(f"  Seuil: {result['required_threshold']}")
        print(f"  Critère validé: {'✅' if result['criterion_met'] else '❌'}")

        # Selon le client, tous devraient avoir 0 redémarrages manuels
        assert result["manual_restart_count"] == 0, (
            f"{turbine_id} devrait avoir 0 redémarrages manuels "
            f"mais a {result['manual_restart_count']}"
        )
        assert result["criterion_met"] is True


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v", "-s"])
