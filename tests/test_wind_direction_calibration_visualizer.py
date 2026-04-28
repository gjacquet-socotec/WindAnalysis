"""
Tests unitaires pour WindDirectionCalibrationVisualizer
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
from datetime import datetime

from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.wind_direction_calibration_visualizer import (
    WindDirectionCalibrationVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)


class TestWindDirectionCalibrationVisualizer:
    """Tests pour le visualiseur de calibration"""

    @pytest.fixture
    def good_calibration_result(self):
        """Résultat avec bonne calibration (écart < 5°)"""
        daily_data = [
            {
                "date": "2024-01-01",
                "mean_angular_error": 2.5,
                "std_angular_error": 0.8,
                "max_angular_error": 4.0,
                "correlation": 0.98,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-02",
                "mean_angular_error": 3.0,
                "std_angular_error": 1.0,
                "max_angular_error": 4.5,
                "correlation": 0.97,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-03",
                "mean_angular_error": 2.8,
                "std_angular_error": 0.9,
                "max_angular_error": 4.2,
                "correlation": 0.99,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-04",
                "mean_angular_error": 3.2,
                "std_angular_error": 1.1,
                "max_angular_error": 4.8,
                "correlation": 0.96,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-05",
                "mean_angular_error": 2.9,
                "std_angular_error": 0.95,
                "max_angular_error": 4.3,
                "correlation": 0.98,
                "num_measurements": 24,
            },
        ]

        return AnalysisResult(
            detailed_results={
                "E01": {
                    "overall_mean_angular_error": 2.88,
                    "overall_std_angular_error": 0.95,
                    "overall_max_angular_error": 4.8,
                    "overall_correlation": 0.976,
                    "threshold_degrees": 5.0,
                    "criterion_met": True,
                    "total_measurements": 120,
                    "daily_calibration": daily_data,
                }
            },
            status="completed",
        )

    @pytest.fixture
    def poor_calibration_result(self):
        """Résultat avec mauvaise calibration (écart > 5°)"""
        daily_data = [
            {
                "date": "2024-01-01",
                "mean_angular_error": 7.5,
                "std_angular_error": 2.1,
                "max_angular_error": 12.0,
                "correlation": 0.92,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-02",
                "mean_angular_error": 8.0,
                "std_angular_error": 2.3,
                "max_angular_error": 13.5,
                "correlation": 0.91,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-03",
                "mean_angular_error": 7.2,
                "std_angular_error": 2.0,
                "max_angular_error": 11.5,
                "correlation": 0.93,
                "num_measurements": 24,
            },
        ]

        return AnalysisResult(
            detailed_results={
                "E02": {
                    "overall_mean_angular_error": 7.57,
                    "overall_std_angular_error": 2.13,
                    "overall_max_angular_error": 13.5,
                    "overall_correlation": 0.92,
                    "threshold_degrees": 5.0,
                    "criterion_met": False,
                    "total_measurements": 72,
                    "daily_calibration": daily_data,
                }
            },
            status="completed",
        )

    @pytest.fixture
    def multi_turbine_result(self):
        """Résultat avec plusieurs turbines"""
        daily_data_e1 = [
            {
                "date": "2024-01-01",
                "mean_angular_error": 2.5,
                "std_angular_error": 0.8,
                "max_angular_error": 4.0,
                "correlation": 0.98,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-02",
                "mean_angular_error": 3.0,
                "std_angular_error": 1.0,
                "max_angular_error": 4.5,
                "correlation": 0.97,
                "num_measurements": 24,
            },
        ]

        daily_data_e2 = [
            {
                "date": "2024-01-01",
                "mean_angular_error": 8.0,
                "std_angular_error": 2.1,
                "max_angular_error": 12.0,
                "correlation": 0.90,
                "num_measurements": 24,
            },
            {
                "date": "2024-01-02",
                "mean_angular_error": 7.5,
                "std_angular_error": 2.0,
                "max_angular_error": 11.5,
                "correlation": 0.92,
                "num_measurements": 24,
            },
        ]

        return AnalysisResult(
            detailed_results={
                "E01": {
                    "overall_mean_angular_error": 2.75,
                    "overall_std_angular_error": 0.9,
                    "overall_max_angular_error": 4.5,
                    "overall_correlation": 0.975,
                    "threshold_degrees": 5.0,
                    "criterion_met": True,
                    "total_measurements": 48,
                    "daily_calibration": daily_data_e1,
                },
                "E02": {
                    "overall_mean_angular_error": 7.75,
                    "overall_std_angular_error": 2.05,
                    "overall_max_angular_error": 12.0,
                    "overall_correlation": 0.91,
                    "threshold_degrees": 5.0,
                    "criterion_met": False,
                    "total_measurements": 48,
                    "daily_calibration": daily_data_e2,
                },
            },
            status="completed",
        )

    def test_create_figure_good_calibration(
        self, good_calibration_result, tmp_path
    ):
        """Test création de figure avec bonne calibration"""
        visualizer = WindDirectionCalibrationVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(good_calibration_result)

        assert fig is not None
        assert len(fig.data) > 0  # Au moins quelques traces
        assert "Calibration" in fig.layout.title.text

    def test_create_figure_poor_calibration(
        self, poor_calibration_result, tmp_path
    ):
        """Test création de figure avec mauvaise calibration"""
        visualizer = WindDirectionCalibrationVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(poor_calibration_result)

        assert fig is not None
        assert len(fig.data) > 0

    def test_create_figure_multi_turbines(self, multi_turbine_result, tmp_path):
        """Test création de figure avec plusieurs turbines"""
        visualizer = WindDirectionCalibrationVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(multi_turbine_result)

        assert fig is not None
        # Avec 2 turbines, on devrait avoir 4 subplots (2 par turbine)
        assert len(fig.data) > 0

    def test_generate_saves_files(self, good_calibration_result, tmp_path):
        """Test que generate() sauvegarde bien les fichiers PNG et JSON"""
        visualizer = WindDirectionCalibrationVisualizer()
        visualizer.output_dir = tmp_path

        result = visualizer.generate(good_calibration_result)

        assert "png_path" in result
        assert "json_path" in result

        # Vérifier que les fichiers existent
        png_path = Path(result["png_path"])
        json_path = Path(result["json_path"])

        assert png_path.exists()
        assert json_path.exists()
        assert png_path.suffix == ".png"
        assert json_path.suffix == ".json"

    def test_empty_result(self, tmp_path):
        """Test avec un résultat vide"""
        empty_result = AnalysisResult(detailed_results={}, status="completed")

        visualizer = WindDirectionCalibrationVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(empty_result)

        assert fig is not None
        # Devrait retourner une figure vide avec un message

    def test_result_with_error(self, tmp_path):
        """Test avec une turbine ayant une erreur"""
        error_result = AnalysisResult(
            detailed_results={"E01": {"error": "No data in test period"}},
            status="completed",
        )

        visualizer = WindDirectionCalibrationVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(error_result)

        assert fig is not None

    def test_chart_name(self):
        """Test que le nom du graphique est correct"""
        visualizer = WindDirectionCalibrationVisualizer()
        assert visualizer.chart_name == "wind_direction_calibration"

    def test_uses_plotly(self):
        """Test que le visualiseur utilise Plotly"""
        visualizer = WindDirectionCalibrationVisualizer()
        assert visualizer.use_plotly is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
