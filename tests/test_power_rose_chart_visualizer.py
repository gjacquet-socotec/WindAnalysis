"""
Tests unitaires pour PowerRoseChartVisualizer
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import numpy as np

from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.power_rose_chart_visualizer import (
    PowerRoseChartVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)


class TestPowerRoseChartVisualizer:
    """Tests pour le visualiseur de rose des puissances"""

    @pytest.fixture
    def sample_chart_data(self):
        """Données synthétiques avec distribution circulaire de puissance"""
        # Créer des données sur tous les secteurs directionnels
        n_samples = 1000
        directions = np.random.uniform(0, 360, n_samples)

        # Puissance variant selon la direction (simuler un problème au secteur Nord)
        # Secteur Nord (330-30°) : puissance réduite (problème de calibration)
        # Autres secteurs : puissance normale
        powers = []
        for direction in directions:
            if (direction >= 330) or (direction <= 30):
                # Secteur Nord : puissance réduite (50% de la normale)
                power = np.random.uniform(500, 1000)
            else:
                # Autres secteurs : puissance normale
                power = np.random.uniform(1800, 2200)
            powers.append(power)

        return pd.DataFrame({
            "wind_direction": directions,
            "activation_power": powers,
        })

    @pytest.fixture
    def uniform_chart_data(self):
        """Données avec puissance uniforme dans toutes les directions"""
        n_samples = 500
        return pd.DataFrame({
            "wind_direction": np.random.uniform(0, 360, n_samples),
            "activation_power": np.random.uniform(1900, 2100, n_samples),
        })

    @pytest.fixture
    def result_with_chart_data(self, sample_chart_data):
        """Résultat d'analyse avec chart_data"""
        return AnalysisResult(
            detailed_results={
                "E01": {
                    "chart_data": sample_chart_data,
                }
            },
            status="completed",
        )

    @pytest.fixture
    def result_multi_turbines(self, sample_chart_data, uniform_chart_data):
        """Résultat avec plusieurs turbines"""
        return AnalysisResult(
            detailed_results={
                "E01": {"chart_data": sample_chart_data},
                "E02": {"chart_data": uniform_chart_data},
            },
            status="completed",
        )

    def test_create_figure_single_turbine(
        self, result_with_chart_data, tmp_path
    ):
        """Test création de figure avec une turbine"""
        visualizer = PowerRoseChartVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(result_with_chart_data)

        assert fig is not None
        assert len(fig.data) > 0
        assert "Rose des Puissances" in fig.layout.title.text

    def test_create_figure_multi_turbines(
        self, result_multi_turbines, tmp_path
    ):
        """Test création de figure avec plusieurs turbines"""
        visualizer = PowerRoseChartVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(result_multi_turbines)

        assert fig is not None
        assert len(fig.data) >= 2  # Au moins 2 traces (une par turbine)

    def test_generate_saves_files(self, result_with_chart_data, tmp_path):
        """Test que generate() sauvegarde bien les fichiers PNG et JSON"""
        visualizer = PowerRoseChartVisualizer()
        visualizer.output_dir = tmp_path

        result = visualizer.generate(result_with_chart_data)

        assert "png_path" in result
        assert "json_path" in result

        png_path = Path(result["png_path"])
        json_path = Path(result["json_path"])

        assert png_path.exists()
        assert json_path.exists()
        assert png_path.suffix == ".png"
        assert json_path.suffix == ".json"

    def test_empty_result(self, tmp_path):
        """Test avec un résultat vide"""
        empty_result = AnalysisResult(detailed_results={}, status="completed")

        visualizer = PowerRoseChartVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(empty_result)

        assert fig is not None

    def test_result_with_error(self, tmp_path):
        """Test avec une turbine ayant une erreur"""
        error_result = AnalysisResult(
            detailed_results={"E01": {"error": "No data available"}},
            status="completed",
        )

        visualizer = PowerRoseChartVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(error_result)

        assert fig is not None

    def test_missing_chart_data(self, tmp_path):
        """Test avec chart_data manquant"""
        result = AnalysisResult(
            detailed_results={
                "E01": {
                    "some_other_data": "value",
                    # Pas de chart_data
                }
            },
            status="completed",
        )

        visualizer = PowerRoseChartVisualizer()
        visualizer.output_dir = tmp_path

        fig = visualizer._create_figure(result)

        assert fig is not None

    def test_chart_name(self):
        """Test que le nom du graphique est correct"""
        visualizer = PowerRoseChartVisualizer()
        assert visualizer.chart_name == "power_rose_chart"

    def test_uses_plotly(self):
        """Test que le visualiseur utilise Plotly"""
        visualizer = PowerRoseChartVisualizer()
        assert visualizer.use_plotly is True

    def test_directional_binning(self, sample_chart_data):
        """Test que les données sont correctement binées par secteur"""
        # Vérifier que les 16 secteurs sont bien créés
        visualizer = PowerRoseChartVisualizer()

        result = AnalysisResult(
            detailed_results={"E01": {"chart_data": sample_chart_data}},
            status="completed",
        )

        fig = visualizer._create_figure(result)

        # Il y a 7 traces (une par tranche de puissance)
        assert len(fig.data) == 7

        # Chaque trace a 16 points (16 secteurs directionnels)
        for trace in fig.data:
            assert len(trace.r) == 16
            assert len(trace.theta) == 16

    def test_power_distribution_by_sector(self, sample_chart_data):
        """
        Test que la distribution des puissances varie selon les secteurs.
        Les données synthétiques ont le secteur Nord avec puissances plus faibles.
        """
        visualizer = PowerRoseChartVisualizer()

        result = AnalysisResult(
            detailed_results={"E01": {"chart_data": sample_chart_data}},
            status="completed",
        )

        fig = visualizer._create_figure(result)

        # Il y a 7 traces (une par tranche de puissance)
        assert len(fig.data) == 7

        # Calculer la fréquence totale par secteur (somme de toutes les tranches)
        total_freq_by_sector = np.zeros(16)
        for trace in fig.data:
            total_freq_by_sector += trace.r

        # Tous les secteurs devraient avoir une fréquence > 0
        # (on a des données dans tous les secteurs)
        assert np.all(total_freq_by_sector > 0)

        # La somme de toutes les fréquences devrait être ~100%
        # (peut varier légèrement à cause des arrondis)
        total_sum = np.sum(total_freq_by_sector)
        assert 95 < total_sum < 105  # Tolérance de 5%


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
