"""
Tests unitaires pour EbaLossVisualizer.
"""

import sys
from pathlib import Path
import pytest
from datetime import datetime

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_loss_visualizer import (
    EbaLossVisualizer,
)


class TestEbaLossVisualizer:
    """Tests pour le visualiseur des pertes d'énergie EBA."""

    @pytest.fixture
    def sample_result_single_turbine(self):
        """Résultat d'analyse pour une seule turbine."""
        return AnalysisResult(
            status="success",
            metadata={"timestamp": datetime.now()},
            requires_visuals=True,
            detailed_results={
                "E1": {
                    "total_real_energy": 50000.0,
                    "total_theoretical_energy": 52356.0,
                    "total_loss_energy": 2356.0,
                    "performance": 95.5,
                    "monthly_performance": [
                        {"month": "2026-01", "performance": 96.2},
                        {"month": "2026-02", "performance": 94.8},
                        {"month": "2026-03", "performance": 95.5},
                    ],
                }
            },
        )

    @pytest.fixture
    def sample_result_multi_turbines(self):
        """Résultat d'analyse pour plusieurs turbines."""
        return AnalysisResult(
            status="success",
            metadata={"timestamp": datetime.now()},
            requires_visuals=True,
            detailed_results={
                "E1": {
                    "total_real_energy": 50000.0,
                    "total_theoretical_energy": 52356.0,
                    "total_loss_energy": 2356.0,
                    "performance": 95.5,
                    "monthly_performance": [
                        {"month": "2026-01", "performance": 96.2},
                        {"month": "2026-02", "performance": 94.8},
                        {"month": "2026-03", "performance": 95.5},
                    ],
                },
                "E6": {
                    "total_real_energy": 48000.0,
                    "total_theoretical_energy": 51500.0,
                    "total_loss_energy": 3500.0,
                    "performance": 93.2,
                    "monthly_performance": [
                        {"month": "2026-01", "performance": 92.5},
                        {"month": "2026-02", "performance": 93.0},
                        {"month": "2026-03", "performance": 94.1},
                    ],
                },
                "E8": {
                    "total_real_energy": 52000.0,
                    "total_theoretical_energy": 53500.0,
                    "total_loss_energy": 1500.0,
                    "performance": 97.2,
                    "monthly_performance": [
                        {"month": "2026-01", "performance": 97.8},
                        {"month": "2026-02", "performance": 96.5},
                        {"month": "2026-03", "performance": 97.3},
                    ],
                },
            },
        )

    @pytest.fixture
    def empty_result(self):
        """Résultat vide."""
        return AnalysisResult(
            status="error",
            metadata={"timestamp": datetime.now()},
            requires_visuals=True,
            detailed_results={},
        )

    def test_visualizer_initialization(self):
        """Test que le visualiseur s'initialise correctement."""
        visualizer = EbaLossVisualizer()
        assert visualizer.chart_name == "eba_loss_chart"
        assert visualizer.use_plotly is True

    def test_create_figure_single_turbine(self, sample_result_single_turbine):
        """Test la création de figure pour une seule turbine."""
        visualizer = EbaLossVisualizer()
        fig = visualizer._create_figure(sample_result_single_turbine)

        assert fig is not None
        assert len(fig.data) == 1  # Une trace pour E1

        # Vérifier que les données sont correctes
        trace = fig.data[0]
        assert trace.name == "E1"
        assert len(trace.x) == 3  # 3 mois
        assert len(trace.y) == 3  # 3 valeurs de pertes

        # Vérifier que les pertes sont calculées (100 - performance)
        expected_losses = [100 - 96.2, 100 - 94.8, 100 - 95.5]
        for i, expected_loss in enumerate(expected_losses):
            assert abs(trace.y[i] - expected_loss) < 0.01

    def test_create_figure_multi_turbines(self, sample_result_multi_turbines):
        """Test la création de figure pour plusieurs turbines."""
        visualizer = EbaLossVisualizer()
        fig = visualizer._create_figure(sample_result_multi_turbines)

        assert fig is not None
        assert len(fig.data) == 3  # Trois traces (E1, E6, E8)

        # Vérifier les noms des traces
        trace_names = {trace.name for trace in fig.data}
        assert trace_names == {"E1", "E6", "E8"}

        # Vérifier que chaque trace a 3 mois
        for trace in fig.data:
            assert len(trace.x) == 3
            assert len(trace.y) == 3

    def test_create_figure_empty_data(self, empty_result):
        """Test la gestion des données vides."""
        visualizer = EbaLossVisualizer()
        fig = visualizer._create_figure(empty_result)

        assert fig is not None
        # Devrait contenir une annotation indiquant qu'il n'y a pas de données
        assert len(fig.layout.annotations) > 0
        assert "No data available" in fig.layout.annotations[0].text

    def test_color_scaling(self, sample_result_multi_turbines):
        """Test que les couleurs varient en fonction des pertes."""
        visualizer = EbaLossVisualizer()
        fig = visualizer._create_figure(sample_result_multi_turbines)

        # Vérifier que chaque trace a des couleurs
        for trace in fig.data:
            assert trace.marker.color is not None
            # Les couleurs doivent être une liste (une couleur par barre)
            assert len(trace.marker.color) == len(trace.y)

    def test_figure_layout(self, sample_result_multi_turbines):
        """Test que la mise en page est correcte."""
        visualizer = EbaLossVisualizer()
        fig = visualizer._create_figure(sample_result_multi_turbines)

        # Vérifier le titre
        assert "Monthly Energy Loss" in fig.layout.title.text

        # Vérifier les axes
        assert fig.layout.xaxis.title.text == "Period (Month)"
        assert fig.layout.yaxis.title.text == "Energy Loss (%)"
        assert fig.layout.yaxis.ticksuffix == "%"

        # Vérifier le mode de barres
        assert fig.layout.barmode == "group"

        # Vérifier la légende
        assert fig.layout.showlegend is True

    def test_generate_creates_files(self, sample_result_single_turbine, tmp_path):
        """Test que generate() crée bien les fichiers PNG et JSON."""
        visualizer = EbaLossVisualizer()
        visualizer.output_dir = tmp_path  # Utiliser un répertoire temporaire

        output_paths = visualizer.generate(sample_result_single_turbine)

        # Vérifier que les chemins sont retournés
        assert "png_path" in output_paths
        assert "json_path" in output_paths

        # Vérifier que les fichiers existent
        assert Path(output_paths["png_path"]).exists()
        assert Path(output_paths["json_path"]).exists()

    def test_metadata_stored_in_result(self, sample_result_single_turbine, tmp_path):
        """Test que les chemins sont stockés dans result.metadata."""
        visualizer = EbaLossVisualizer()
        visualizer.output_dir = tmp_path

        visualizer.generate(sample_result_single_turbine)

        # Vérifier que metadata est mis à jour
        assert sample_result_single_turbine.metadata is not None
        assert "charts" in sample_result_single_turbine.metadata
        assert "eba_loss_chart" in sample_result_single_turbine.metadata["charts"]

        chart_info = sample_result_single_turbine.metadata["charts"]["eba_loss_chart"]
        assert "png_path" in chart_info
        assert "json_path" in chart_info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
