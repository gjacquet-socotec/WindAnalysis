"""
Tests unitaires pour TopErrorCodeFrequencyVisualizer.
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
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.top_error_code_frequency_visualizer import (
    TopErrorCodeFrequencyVisualizer,
)


class TestTopErrorCodeFrequencyVisualizer:
    """Tests pour le visualiseur des codes d'erreur."""

    @pytest.fixture
    def sample_result_single_turbine(self):
        """Résultat d'analyse pour une seule turbine."""
        return AnalysisResult(
            status="success",
            metadata={"timestamp": datetime.now()},
            requires_visuals=True,
            detailed_results={
                "E1": {
                    "summary": {
                        "total_error_events": 50,
                        "unique_error_codes": 10,
                        "turbine_id": "E1",
                    },
                    "code_frequency": [
                        {
                            "code": "FM6-310",
                            "count": 15,
                            "frequency_percent": 30.0,
                            "description": "Grid fault",
                            "criticality": "CRITICAL",
                        },
                        {
                            "code": "FM7-120",
                            "count": 10,
                            "frequency_percent": 20.0,
                            "description": "Generator temperature high",
                            "criticality": "HIGH",
                        },
                        {
                            "code": "FM2-050",
                            "count": 8,
                            "frequency_percent": 16.0,
                            "description": "Pitch error",
                            "criticality": "MEDIUM",
                        },
                    ],
                    "most_impactful_codes": [
                        {
                            "code": "FM6-310",
                            "occurrences": 15,
                            "total_duration_hours": 12.5,
                            "criticality": "CRITICAL",
                            "description": "Grid fault",
                        },
                        {
                            "code": "FM7-120",
                            "occurrences": 10,
                            "total_duration_hours": 8.3,
                            "criticality": "HIGH",
                            "description": "Generator temperature high",
                        },
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
                    "code_frequency": [
                        {
                            "code": "FM6-310",
                            "count": 15,
                            "description": "Grid fault",
                            "criticality": "CRITICAL",
                        },
                        {
                            "code": "FM7-120",
                            "count": 10,
                            "description": "Generator error",
                            "criticality": "HIGH",
                        },
                    ],
                    "most_impactful_codes": [
                        {
                            "code": "FM6-310",
                            "total_duration_hours": 12.5,
                            "criticality": "CRITICAL",
                            "description": "Grid fault",
                        },
                    ],
                },
                "E6": {
                    "code_frequency": [
                        {
                            "code": "FM2-050",
                            "count": 20,
                            "description": "Pitch error",
                            "criticality": "MEDIUM",
                        },
                    ],
                    "most_impactful_codes": [
                        {
                            "code": "FM2-050",
                            "total_duration_hours": 5.2,
                            "criticality": "MEDIUM",
                            "description": "Pitch error",
                        },
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
        visualizer = TopErrorCodeFrequencyVisualizer()
        assert visualizer.chart_name == "top_error_frequency"
        assert visualizer.use_plotly is True

    def test_create_figure_single_turbine(self, sample_result_single_turbine):
        """Test la création de figure pour une seule turbine."""
        visualizer = TopErrorCodeFrequencyVisualizer()
        fig = visualizer._create_figure(sample_result_single_turbine)

        assert fig is not None
        # Devrait avoir 2 traces (1 pour fréquence, 1 pour durée)
        assert len(fig.data) == 2

        # Vérifier les données de la première trace (fréquence)
        trace_freq = fig.data[0]
        assert trace_freq.orientation == "h"  # Barres horizontales
        assert len(trace_freq.y) == 3  # 3 codes

        # Vérifier les données de la deuxième trace (durée)
        trace_duration = fig.data[1]
        assert trace_duration.orientation == "h"
        assert len(trace_duration.y) == 2  # 2 codes

    def test_create_figure_multi_turbines(self, sample_result_multi_turbines):
        """Test la création de figure pour plusieurs turbines."""
        visualizer = TopErrorCodeFrequencyVisualizer()
        fig = visualizer._create_figure(sample_result_multi_turbines)

        assert fig is not None
        # Devrait avoir 4 traces (2 par turbine: fréquence + durée)
        assert len(fig.data) == 4

    def test_create_figure_empty_data(self, empty_result):
        """Test la gestion des données vides."""
        visualizer = TopErrorCodeFrequencyVisualizer()
        fig = visualizer._create_figure(empty_result)

        assert fig is not None
        # Devrait contenir une annotation indiquant qu'il n'y a pas de données
        assert len(fig.layout.annotations) > 0
        assert "No error code data available" in fig.layout.annotations[0].text

    def test_color_mapping(self, sample_result_single_turbine):
        """Test que les couleurs sont bien mappées selon la criticité."""
        visualizer = TopErrorCodeFrequencyVisualizer()
        fig = visualizer._create_figure(sample_result_single_turbine)

        # Vérifier que les barres ont des couleurs différentes
        trace_freq = fig.data[0]
        colors = trace_freq.marker.color

        assert len(colors) == 3
        # Les couleurs devraient être différentes pour différentes criticités
        assert len(set(colors)) >= 2  # Au moins 2 couleurs différentes

    def test_figure_layout(self, sample_result_single_turbine):
        """Test que la mise en page est correcte."""
        visualizer = TopErrorCodeFrequencyVisualizer()
        fig = visualizer._create_figure(sample_result_single_turbine)

        # Vérifier le titre
        assert "Error Code Analysis" in fig.layout.title.text

        # Vérifier qu'il y a 2 subplots (xaxis et xaxis2)
        assert hasattr(fig.layout, "xaxis")
        assert hasattr(fig.layout, "xaxis2")
        assert hasattr(fig.layout, "yaxis")
        assert hasattr(fig.layout, "yaxis2")

        # Vérifier que showlegend est False (pas de légende)
        assert fig.layout.showlegend is False

    def test_generate_creates_files(self, sample_result_single_turbine, tmp_path):
        """Test que generate() crée bien les fichiers PNG et JSON."""
        visualizer = TopErrorCodeFrequencyVisualizer()
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
        visualizer = TopErrorCodeFrequencyVisualizer()
        visualizer.output_dir = tmp_path

        visualizer.generate(sample_result_single_turbine)

        # Vérifier que metadata est mis à jour
        assert sample_result_single_turbine.metadata is not None
        assert "charts" in sample_result_single_turbine.metadata
        assert "top_error_frequency" in sample_result_single_turbine.metadata["charts"]

        chart_info = sample_result_single_turbine.metadata["charts"][
            "top_error_frequency"
        ]
        assert "png_path" in chart_info
        assert "json_path" in chart_info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
