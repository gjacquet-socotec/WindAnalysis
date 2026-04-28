"""
Tests unitaires pour EbaManufacturerVisualizer.
"""

import sys
from pathlib import Path
import pytest

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_manifacturer_visualizer import (
    EbaManufacturerVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)


@pytest.fixture
def sample_manufacturer_eba_result():
    """Génère un résultat EBA Manufacturer factice."""
    return AnalysisResult(
        detailed_results={
            "WTG01": {
                "total_real_energy": 140000.0,
                "total_theoretical_energy": 160000.0,
                "performance": 87.5,  # Plus bas que Cut-In/Cut-Out car inclut downtimes
                "monthly_performance": [
                    {"month": "2024-01", "performance": 86.5},
                    {"month": "2024-02", "performance": 88.2},
                    {"month": "2024-03", "performance": 87.8},
                    {"month": "2024-04", "performance": 88.5},
                ],
            },
            "WTG02": {
                "total_real_energy": 135000.0,
                "total_theoretical_energy": 155000.0,
                "performance": 87.1,
                "monthly_performance": [
                    {"month": "2024-01", "performance": 85.2},
                    {"month": "2024-02", "performance": 87.8},
                    {"month": "2024-03", "performance": 88.5},
                    {"month": "2024-04", "performance": 87.0},
                ],
            },
        },
        status="completed",
        requires_visuals=True,
    )


def test_visualizer_initialization():
    """Test l'initialisation du visualiseur."""
    visualizer = EbaManufacturerVisualizer()
    assert visualizer is not None
    assert visualizer.chart_name == "eba_manufacturer"
    assert visualizer.use_plotly is True


def test_create_figure_with_data(sample_manufacturer_eba_result):
    """Test la création de figure avec des données valides."""
    visualizer = EbaManufacturerVisualizer()
    fig = visualizer._create_figure(sample_manufacturer_eba_result)

    assert fig is not None
    # Vérifier que la figure a des traces (lignes)
    assert len(fig.data) > 0


def test_create_figure_empty_result():
    """Test la création de figure avec résultat vide."""
    visualizer = EbaManufacturerVisualizer()
    empty_result = AnalysisResult(
        detailed_results={},
        status="completed",
        requires_visuals=True,
    )

    fig = visualizer._create_figure(empty_result)
    assert fig is not None


def test_create_figure_with_error():
    """Test avec des données contenant une erreur."""
    visualizer = EbaManufacturerVisualizer()
    error_result = AnalysisResult(
        detailed_results={
            "WTG01": {
                "error": "No data in period",
            }
        },
        status="completed",
        requires_visuals=True,
    )

    fig = visualizer._create_figure(error_result)
    assert fig is not None


def test_generate_saves_files(sample_manufacturer_eba_result, tmp_path):
    """Test que generate() sauvegarde bien les fichiers."""
    visualizer = EbaManufacturerVisualizer()
    visualizer.output_dir = tmp_path

    result = visualizer.generate(sample_manufacturer_eba_result)

    # Vérifier les chemins retournés
    assert "png_path" in result
    assert "json_path" in result

    # Vérifier que les fichiers existent
    assert Path(result["png_path"]).exists()
    assert Path(result["json_path"]).exists()


def test_metadata_storage(sample_manufacturer_eba_result):
    """Test que les chemins sont stockés dans metadata."""
    visualizer = EbaManufacturerVisualizer()
    visualizer.generate(sample_manufacturer_eba_result)

    # Vérifier que metadata a été mis à jour
    assert sample_manufacturer_eba_result.metadata is not None
    assert "charts" in sample_manufacturer_eba_result.metadata
    assert "eba_manufacturer" in sample_manufacturer_eba_result.metadata["charts"]


def test_multiple_turbines():
    """Test avec plusieurs turbines."""
    multi_result = AnalysisResult(
        detailed_results={
            f"WTG{i:02d}": {
                "performance": 85 + i,  # Performances plus basses (inclut downtimes)
                "monthly_performance": [
                    {"month": f"2024-{m:02d}", "performance": 85 + i + m}
                    for m in range(1, 5)
                ],
            }
            for i in range(1, 7)  # 6 turbines
        },
        status="completed",
        requires_visuals=True,
    )

    visualizer = EbaManufacturerVisualizer()
    fig = visualizer._create_figure(multi_result)

    assert fig is not None
    # Devrait avoir 6 turbines + 1 ligne moyenne = 7 traces
    assert len(fig.data) == 7

    # Vérifier que la dernière trace est la moyenne du parc
    assert fig.data[-1].name == "Wind farm"
    assert fig.data[-1].line.dash == "dash"


def test_title_includes_manufacturer():
    """Test que le titre indique qu'il s'agit de l'EBA Manufacturer."""
    result = AnalysisResult(
        detailed_results={
            "WTG01": {
                "performance": 87.5,
                "monthly_performance": [
                    {"month": "2024-01", "performance": 87.5},
                ],
            }
        },
        status="completed",
        requires_visuals=True,
    )

    visualizer = EbaManufacturerVisualizer()
    fig = visualizer._create_figure(result)

    # Vérifier que le titre contient "Manufacturer"
    assert "Manufacturer" in fig.layout.title.text


def test_performance_values_in_correct_range():
    """Test que les performances sont bien en % (0-100)."""
    result = AnalysisResult(
        detailed_results={
            "WTG01": {
                "performance": 87.5,
                "monthly_performance": [
                    {"month": "2024-01", "performance": 85.0},
                    {"month": "2024-02", "performance": 90.0},
                ],
            }
        },
        status="completed",
        requires_visuals=True,
    )

    visualizer = EbaManufacturerVisualizer()
    fig = visualizer._create_figure(result)

    # Vérifier que l'axe Y a la bonne plage (Plotly retourne un tuple)
    assert list(fig.layout.yaxis.range) == [0, 105]
    assert fig.layout.yaxis.ticksuffix == "%"


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
