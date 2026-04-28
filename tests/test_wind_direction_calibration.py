"""
Tests unitaires pour WindDirectionCalibrationAnalyzer
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.wind_turbine_analytics.data_processing.analyzer.logics.wind_direction_calibration_analyzer import (
    WindDirectionCalibrationAnalyzer,
)
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    ValidationCriteria,
    Criterion,
)


class TestAngularDifferenceCalculation:
    """Tests pour la fonction _calculate_angular_difference"""

    def test_normal_difference(self):
        """Test cas normal : angle1=10°, angle2=20° → écart = 10°"""
        angle1 = pd.Series([10.0])
        angle2 = pd.Series([20.0])
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            angle1, angle2
        )
        assert result[0] == 10.0

    def test_wraparound_359_to_1(self):
        """Test wraparound : angle1=359°, angle2=1° → écart = 2°"""
        angle1 = pd.Series([359.0])
        angle2 = pd.Series([1.0])
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            angle1, angle2
        )
        assert result[0] == 2.0

    def test_wraparound_1_to_359(self):
        """Test wraparound inverse : angle1=1°, angle2=359° → écart = 2°"""
        angle1 = pd.Series([1.0])
        angle2 = pd.Series([359.0])
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            angle1, angle2
        )
        assert result[0] == 2.0

    def test_wraparound_180_degrees(self):
        """Test limite : angle1=180°, angle2=0° → écart = 180°"""
        angle1 = pd.Series([180.0])
        angle2 = pd.Series([0.0])
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            angle1, angle2
        )
        assert result[0] == 180.0

    def test_wraparound_10_to_350(self):
        """Test wraparound : angle1=10°, angle2=350° → écart = 20°"""
        angle1 = pd.Series([10.0])
        angle2 = pd.Series([350.0])
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            angle1, angle2
        )
        assert result[0] == 20.0

    def test_multiple_values_with_wraparound(self):
        """Test avec plusieurs valeurs incluant wraparound"""
        angle1 = pd.Series([358.0, 359.0, 0.0, 1.0, 2.0])
        angle2 = pd.Series([0.0, 1.0, 2.0, 3.0, 4.0])
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            angle1, angle2
        )
        expected = np.array([2.0, 2.0, 2.0, 2.0, 2.0])
        np.testing.assert_array_almost_equal(result, expected)

    def test_identical_angles(self):
        """Test angles identiques : écart = 0°"""
        angle1 = pd.Series([45.0, 90.0, 180.0])
        angle2 = pd.Series([45.0, 90.0, 180.0])
        result = WindDirectionCalibrationAnalyzer._calculate_angular_difference(
            angle1, angle2
        )
        expected = np.array([0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(result, expected)


class TestWindDirectionCalibrationAnalyzer:
    """Tests pour l'analyse complète de calibration"""

    @pytest.fixture
    def turbine_config(self, tmp_path):
        """Configuration de turbine pour les tests"""
        config = TurbineConfig(
            turbine_id="TEST01",
            test_start=pd.Timestamp("2024-01-01 00:00:00"),
            test_end=pd.Timestamp("2024-01-06 00:00:00"),
            general_information=TurbineGeneralInformation(
                model="N131",
                nominal_power=3780.0,
                constructor="Nordex",
                path_operation_data=str(tmp_path / "operation.csv"),
                path_log_data=str(tmp_path / "log.csv"),
            ),
            mapping_operation_data=TurbineMappingOperationData(
                timestamp="timestamp",
                wind_speed="wind_speed",
                wind_direction="wind_direction",
                nacelle_position="nacelle_position",
                activation_power="active_power",
            ),
        )
        return config

    @pytest.fixture
    def validation_criteria(self):
        """Critères de validation pour les tests"""
        return ValidationCriteria(
            validation_criterion={
                "cut_in_to_cut_out": Criterion(specification=[3.0, 25.0])
            }
        )

    def test_constant_3_degree_offset(self, turbine_config, validation_criteria):
        """
        Test avec un décalage constant de 3° entre wind_direction et
        nacelle_position. L'écart moyen doit être ~3° et criterion_met = True.
        """
        # Créer des données synthétiques : 5 jours, 1 mesure par heure
        timestamps = pd.date_range(
            start="2024-01-01", end="2024-01-06", freq="1H", inclusive="left"
        )
        wind_directions = np.arange(0, len(timestamps)) % 360
        nacelle_positions = (wind_directions + 3) % 360
        wind_speeds = np.full(len(timestamps), 10.0)

        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "wind_direction": wind_directions,
                "nacelle_position": nacelle_positions,
                "wind_speed": wind_speeds,
                "active_power": np.full(len(timestamps), 2000.0),
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        # Vérifications
        assert "overall_mean_angular_error" in result
        assert abs(result["overall_mean_angular_error"] - 3.0) < 0.1
        assert result["criterion_met"] == True
        assert result["threshold_degrees"] == 5.0
        assert len(result["daily_calibration"]) == 5

        # Vérifier que chaque jour a un écart moyen ~3°
        for day_result in result["daily_calibration"]:
            assert abs(day_result["mean_angular_error"] - 3.0) < 0.5

    def test_wraparound_scenario(self, turbine_config, validation_criteria):
        """
        Test avec wraparound : wind_direction autour de 0°/360°.
        Vérifier que les écarts sont bien calculés avec le chemin court.
        """
        timestamps = pd.date_range(
            start="2024-01-01", end="2024-01-02", freq="1H", inclusive="left"
        )
        # wind_direction oscille autour de 0° : [358, 359, 0, 1, 2] * 5
        wind_directions = np.tile([358, 359, 0, 1, 2], 5)[:24]
        # nacelle_position décalé de +2° avec wraparound
        nacelle_positions = np.tile([0, 1, 2, 3, 4], 5)[:24]
        wind_speeds = np.full(len(wind_directions), 10.0)

        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps[:len(wind_directions)],
                "wind_direction": wind_directions,
                "nacelle_position": nacelle_positions,
                "wind_speed": wind_speeds,
                "active_power": np.full(len(wind_directions), 2000.0),
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        # Tous les écarts devraient être exactement 2°
        assert abs(result["overall_mean_angular_error"] - 2.0) < 0.1
        assert result["criterion_met"] == True

    def test_no_data_in_test_period(self, turbine_config, validation_criteria):
        """Test avec aucune donnée dans la période de test"""
        # Données hors période de test
        timestamps = pd.date_range(start="2023-12-01", end="2023-12-02", freq="1H")
        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "wind_direction": np.full(len(timestamps), 0.0),
                "nacelle_position": np.full(len(timestamps), 0.0),
                "wind_speed": np.full(len(timestamps), 10.0),
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        assert "error" in result
        assert result["error"] == "No data in test period"

    def test_wind_speed_filtering(self, turbine_config, validation_criteria):
        """
        Test que les données avec wind_speed <= cut-in sont bien filtrées.
        """
        timestamps = pd.date_range(
            start="2024-01-01", end="2024-01-02", freq="1H", inclusive="left"
        )

        # Moitié des données avec wind_speed > cut-in (3 m/s), moitié en dessous
        wind_speeds = np.concatenate(
            [np.full(12, 10.0), np.full(12, 2.0)]
        )  # 12h @ 10 m/s, 12h @ 2 m/s
        wind_directions = np.arange(0, len(timestamps)) % 360
        nacelle_positions = (wind_directions + 3) % 360

        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "wind_direction": wind_directions,
                "nacelle_position": nacelle_positions,
                "wind_speed": wind_speeds,
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        # Seules les 12 premières heures (wind_speed > 3 m/s) devraient être prises en compte
        assert result["total_measurements"] == 12
        assert abs(result["overall_mean_angular_error"] - 3.0) < 0.5

    def test_criterion_failure(self, turbine_config, validation_criteria):
        """
        Test avec un écart moyen > 5° (échec du critère).
        """
        timestamps = pd.date_range(
            start="2024-01-01", end="2024-01-02", freq="1H", inclusive="left"
        )
        wind_directions = np.arange(0, len(timestamps)) % 360
        nacelle_positions = (wind_directions + 8) % 360
        wind_speeds = np.full(len(timestamps), 10.0)

        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "wind_direction": wind_directions,
                "nacelle_position": nacelle_positions,
                "wind_speed": wind_speeds,
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        assert abs(result["overall_mean_angular_error"] - 8.0) < 0.1
        assert result["criterion_met"] == False

    def test_daily_results_structure(self, turbine_config, validation_criteria):
        """Vérifier la structure des résultats journaliers"""
        timestamps = pd.date_range(
            start="2024-01-01", end="2024-01-03", freq="1H", inclusive="left"
        )
        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "wind_direction": np.arange(0, len(timestamps)) % 360,
                "nacelle_position": (np.arange(0, len(timestamps)) + 3) % 360,
                "wind_speed": np.full(len(timestamps), 10.0),
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        assert "daily_calibration" in result
        assert len(result["daily_calibration"]) == 2  # 2 jours complets

        # Vérifier la structure de chaque jour
        for day_result in result["daily_calibration"]:
            assert "date" in day_result
            assert "mean_angular_error" in day_result
            assert "std_angular_error" in day_result
            assert "max_angular_error" in day_result
            assert "correlation" in day_result
            assert "num_measurements" in day_result

    def test_missing_nacelle_position_column(self, turbine_config, validation_criteria):
        """Test quand la colonne nacelle_position n'est pas configurée"""
        turbine_config.mapping_operation_data.nacelle_position = None

        timestamps = pd.date_range(start="2024-01-01", end="2024-01-02", freq="1H")
        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "wind_direction": np.full(len(timestamps), 0.0),
                "wind_speed": np.full(len(timestamps), 10.0),
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        assert "error" in result
        assert "nacelle_position" in result["error"]

    def test_chart_data_included_in_result(self, turbine_config, validation_criteria):
        """Test que chart_data est inclus dans le résultat pour les visualiseurs Rose"""
        # Créer des données synthétiques avec 7 jours
        timestamps = pd.date_range(start="2024-01-01", end="2024-01-08", freq="1H")[
            :-1
        ]
        n_samples = len(timestamps)

        # Variation naturelle de la direction du vent
        hours = np.arange(n_samples)
        wind_direction = (180 + 120 * np.sin(hours * 2 * np.pi / 24)) % 360
        nacelle_position = (wind_direction + 3.0) % 360  # Décalage de 3°
        nacelle_position += np.random.normal(0, 1, n_samples)
        nacelle_position = nacelle_position % 360

        # Vitesse et puissance
        wind_speed = 9 + 4 * np.sin(hours * 2 * np.pi / 48)
        active_power = np.minimum(wind_speed**3 * 15, 3780)

        operation_data = pd.DataFrame(
            {
                "timestamp": timestamps,
                "wind_direction": wind_direction,
                "nacelle_position": nacelle_position,
                "wind_speed": wind_speed,
                "active_power": active_power,
            }
        )

        log_data = pd.DataFrame()

        analyzer = WindDirectionCalibrationAnalyzer()
        result = analyzer._compute(
            operation_data, log_data, turbine_config, validation_criteria
        )

        # Vérifier que chart_data existe
        assert "chart_data" in result
        assert isinstance(result["chart_data"], pd.DataFrame)

        # Vérifier les colonnes standardisées
        assert "wind_direction" in result["chart_data"].columns
        assert "activation_power" in result["chart_data"].columns
        assert "wind_speed" in result["chart_data"].columns
        assert "timestamp" in result["chart_data"].columns
        assert "nacelle_position" in result["chart_data"].columns

        # Vérifier que les données sont filtrées (wind_speed > cut-in)
        assert len(result["chart_data"]) > 0
        assert result["chart_data"]["wind_speed"].min() >= 3.0  # cut-in

        # Vérifier que les colonnes sont dans le bon ordre
        expected_columns = [
            "wind_direction",
            "activation_power",
            "wind_speed",
            "timestamp",
            "nacelle_position",
        ]
        assert list(result["chart_data"].columns) == expected_columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
