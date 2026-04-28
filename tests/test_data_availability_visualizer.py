"""
Tests unitaires pour DataAvailabilityVisualizer
Valide la génération du graphique de disponibilité des données.
"""

import sys
from pathlib import Path

# Support pour emojis sur Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ajouter le projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
from datetime import datetime
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.data_availability_visualizer import (
    DataAvailabilityVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)


@pytest.fixture
def sample_availability_result():
    """Crée un résultat d'analyse de disponibilité pour tests."""
    # Créer des données pour 24 heures avec quelques gaps
    timestamps = pd.date_range(
        start="2026-01-01 00:00:00", end="2026-01-02 00:00:00", freq="1h"
    )

    # Turbine E1 - Bonne disponibilité
    availability_e1 = pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_speed": [1] * 20 + [0] * 4 + [1],  # Gap de 4h
            "active_power": [1] * 25,  # Toujours disponible
            "wind_direction": [1] * 15 + [0] * 5 + [1] * 5,  # Gap de 5h
            "temperature": [1] * 25,
            "overall": [1] * 15 + [0] * 5 + [1] * 5,
        }
    )

    # Turbine E2 - Disponibilité partielle
    availability_e2 = pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_speed": [1] * 10 + [0] * 10 + [1] * 5,
            "active_power": [1] * 15 + [0] * 10,
            "wind_direction": [1] * 25,
            "temperature": [1] * 25,
            "overall": [1] * 10 + [0] * 10 + [1] * 5,
        }
    )

    # Turbine E3 - Excellente disponibilité
    availability_e3 = pd.DataFrame(
        {
            "timestamp": timestamps,
            "wind_speed": [1] * 25,
            "active_power": [1] * 25,
            "wind_direction": [1] * 25,
            "temperature": [1] * 25,
            "overall": [1] * 25,
        }
    )

    result = AnalysisResult(
        detailed_results={
            "E1": {
                "availability_table": availability_e1,
                "summary": {
                    "overall_availability_pct": 80.0,
                    "wind_speed_availability_pct": 84.0,
                },
            },
            "E2": {
                "availability_table": availability_e2,
                "summary": {
                    "overall_availability_pct": 60.0,
                    "wind_speed_availability_pct": 60.0,
                },
            },
            "E3": {
                "availability_table": availability_e3,
                "summary": {
                    "overall_availability_pct": 100.0,
                    "wind_speed_availability_pct": 100.0,
                },
            },
        },
        status="completed",
        requires_visuals=True,
    )

    return result


def test_visualizer_initialization():
    """Test l'initialisation du visualiseur."""
    visualizer = DataAvailabilityVisualizer()
    assert visualizer.chart_name == "data_availability"
    assert visualizer.use_plotly is True


def test_create_figure(sample_availability_result):
    """Test la création de la figure."""
    visualizer = DataAvailabilityVisualizer()
    fig = visualizer._create_figure(sample_availability_result)

    # Vérifier que la figure a été créée
    assert fig is not None
    assert hasattr(fig, "data")
    assert hasattr(fig, "layout")

    # Vérifier le titre
    assert "SCADA Data Availability" in fig.layout.title.text

    # Vérifier qu'il y a des traces (barres)
    assert len(fig.data) > 0

    print(f"\n✅ Figure créée avec {len(fig.data)} traces")


def test_group_consecutive_segments():
    """Test le groupement de segments consécutifs."""
    visualizer = DataAvailabilityVisualizer()

    # Créer des données de test
    timestamps = pd.date_range(
        start="2026-01-01 00:00:00", periods=10, freq="1h"
    )
    values = pd.Series([1, 1, 1, 0, 0, 1, 1, 1, 1, 0])

    segments = visualizer._group_consecutive_segments(timestamps, values)

    # Devrait avoir 4 segments : [1,1,1], [0,0], [1,1,1,1], [0]
    assert len(segments) == 4

    # Vérifier le premier segment
    start, end, value = segments[0]
    assert value == 1
    assert start == timestamps[0]
    assert end == timestamps[2]

    # Vérifier le deuxième segment
    start, end, value = segments[1]
    assert value == 0
    assert start == timestamps[3]
    assert end == timestamps[4]

    print(f"\n✅ {len(segments)} segments identifiés correctement")
    for i, (start, end, val) in enumerate(segments):
        print(f"   Segment {i+1}: {start} → {end}, value={val}")


def test_multiple_turbines(sample_availability_result):
    """Test avec plusieurs turbines."""
    visualizer = DataAvailabilityVisualizer()
    fig = visualizer._create_figure(sample_availability_result)

    # Vérifier que toutes les turbines sont présentes
    turbine_count = len(sample_availability_result.detailed_results)
    assert turbine_count == 3

    # Vérifier qu'il y a des Y labels pour chaque turbine
    # Chaque turbine a 4 variables (ws, power, dir, temp)
    expected_y_labels = turbine_count * 4
    assert len(fig.layout.yaxis.categoryarray) == expected_y_labels

    print(f"\n✅ {turbine_count} turbines visualisées")
    print(f"   Labels Y: {fig.layout.yaxis.categoryarray}")


def test_generate_output_files(sample_availability_result, tmp_path):
    """Test la génération des fichiers de sortie."""
    visualizer = DataAvailabilityVisualizer()

    # Définir le répertoire de sortie temporaire
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Initialiser les métadonnées si nécessaire
    if sample_availability_result.metadata is None:
        sample_availability_result.metadata = {}

    # Sauvegarder les métadonnées pour la génération
    sample_availability_result.metadata["output_dir"] = str(output_dir)
    sample_availability_result.metadata["charts"] = {}

    # Générer les fichiers
    output_paths = visualizer.generate(sample_availability_result)

    # Vérifier que les fichiers ont été créés
    assert "png_path" in output_paths
    assert "json_path" in output_paths

    png_path = Path(output_paths["png_path"])
    json_path = Path(output_paths["json_path"])

    assert png_path.exists()
    assert json_path.exists()
    assert png_path.suffix == ".png"
    assert json_path.suffix == ".json"

    print(f"\n✅ Fichiers générés:")
    print(f"   PNG: {png_path}")
    print(f"   JSON: {json_path}")


def test_empty_result():
    """Test avec un résultat vide."""
    visualizer = DataAvailabilityVisualizer()

    empty_result = AnalysisResult(
        detailed_results={}, status="completed", requires_visuals=False
    )

    fig = visualizer._create_figure(empty_result)

    # Devrait créer une figure vide sans erreur
    assert fig is not None
    assert len(fig.data) == 0

    print("\n✅ Figure vide gérée correctement")


def test_color_coding():
    """Test que les couleurs sont correctes (green + orange)."""
    visualizer = DataAvailabilityVisualizer()

    # Créer un résultat avec disponibilité complète ET gaps
    timestamps = pd.date_range(
        start="2026-01-01 00:00:00", periods=10, freq="1h"
    )

    result = AnalysisResult(
        detailed_results={
            "E1": {
                "availability_table": pd.DataFrame(
                    {
                        "timestamp": timestamps,
                        "wind_speed": [1, 1, 1, 0, 0, 1, 1, 1, 1, 1],  # Gaps
                        "active_power": [1] * 10,
                        "wind_direction": [1] * 10,
                        "temperature": [1] * 10,
                    }
                ),
                "summary": {"overall_availability_pct": 80.0},
            }
        },
        status="completed",
        requires_visuals=True,
    )

    fig = visualizer._create_figure(result)

    # Vérifier barres vertes
    green_bars = [t for t in fig.data if t.marker.color == "#2ca02c"]
    assert len(green_bars) > 0

    # Vérifier barres orange (unavailable)
    orange_bars = [t for t in fig.data if t.marker.color == "#FFA500"]
    assert len(orange_bars) > 0

    print(f"\n✅ {len(green_bars)} barres vertes trouvées")
    print(f"✅ {len(orange_bars)} barres orange trouvées")


def test_xaxis_date_formatting():
    """Test que le formatage de l'axe X s'adapte à la durée."""
    visualizer = DataAvailabilityVisualizer()

    # Test court (3 jours)
    timestamps_short = pd.date_range(
        start="2026-01-01 00:00:00", periods=72, freq="1h"
    )
    result_short = AnalysisResult(
        detailed_results={
            "E1": {
                "availability_table": pd.DataFrame(
                    {
                        "timestamp": timestamps_short,
                        "wind_speed": [1] * 72,
                        "active_power": [1] * 72,
                        "wind_direction": [1] * 72,
                        "temperature": [1] * 72,
                    }
                ),
                "summary": {"overall_availability_pct": 100.0},
            }
        },
        status="completed",
        requires_visuals=True,
    )

    fig_short = visualizer._create_figure(result_short)

    # Vérifier format court
    assert fig_short.layout.xaxis.type == "date"
    assert fig_short.layout.xaxis.tickformat == "%d/%m %H:%M"
    assert fig_short.layout.xaxis.tickangle == -45

    # Test long (90 jours)
    timestamps_long = pd.date_range(start="2026-01-01", periods=90, freq="1D")
    result_long = AnalysisResult(
        detailed_results={
            "E1": {
                "availability_table": pd.DataFrame(
                    {
                        "timestamp": timestamps_long,
                        "wind_speed": [1] * 90,
                        "active_power": [1] * 90,
                        "wind_direction": [1] * 90,
                        "temperature": [1] * 90,
                    }
                ),
                "summary": {"overall_availability_pct": 100.0},
            }
        },
        status="completed",
        requires_visuals=True,
    )

    fig_long = visualizer._create_figure(result_long)

    # Vérifier format long
    assert fig_long.layout.xaxis.tickformat == "%b %Y"
    assert fig_long.layout.xaxis.tickangle == 0

    print("\n✅ Formatage adaptatif vérifié")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
