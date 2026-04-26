"""Unit tests for ConsolePipelinePresenter."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
from src.wind_turbine_analytics.presentation.console_presenter import (
    ConsolePipelinePresenter,
)
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult


class TestConsolePipelinePresenter:
    """Test suite for ConsolePipelinePresenter."""

    @pytest.fixture
    def presenter(self):
        """Create a ConsolePipelinePresenter instance."""
        return ConsolePipelinePresenter()

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=5, freq="10min"),
                "wind_speed": [5.2, 6.1, 7.3, 5.8, 6.5],
                "active_power": [1200, 1500, 1800, 1300, 1600],
            }
        )

    @pytest.fixture
    def simple_analysis_result(self):
        """Create a simple AnalysisResult for testing."""
        return AnalysisResult(
            status="SUCCESS",
            metadata={"turbine_id": "WTG01", "test_duration_hours": 120},
            requires_visuals=False,
            detailed_results={
                "total_hours": 120,
                "valid_hours": 115,
                "availability_pct": 95.83,
            },
        )

    @pytest.fixture
    def complex_analysis_result(self, sample_dataframe):
        """Create a complex AnalysisResult with DataFrame for testing."""
        return AnalysisResult(
            status="SUCCESS",
            metadata={
                "turbine_id": "WTG02",
                "analysis_type": "EBA Cut-In/Cut-Out",
                "period": {"start": "2024-01-01", "end": "2024-12-31"},
            },
            requires_visuals=True,
            detailed_results={
                "summary": {
                    "total_real_energy": 125000.5,
                    "total_theoretical_energy": 130000.0,
                    "performance": 96.15,
                },
                "data_table": sample_dataframe,
                "monthly_performance": [
                    {"month": "2024-01", "performance": 95.5},
                    {"month": "2024-02", "performance": 96.8},
                    {"month": "2024-03", "performance": 97.2},
                ],
            },
        )

    def test_show_analysis_result_none(self, presenter, capsys):
        """Test handling of None result."""
        presenter.show_analysis_result(None, "Test Analysis")
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "No results" in captured.out

    def test_show_analysis_result_simple(self, presenter, simple_analysis_result, capsys):
        """Test display of simple analysis result."""
        presenter.show_analysis_result(simple_analysis_result, "Simple Test Analysis")
        captured = capsys.readouterr()

        # Check that key elements are displayed
        assert "Simple Test Analysis" in captured.out
        assert "Status: SUCCESS" in captured.out
        assert "Metadata:" in captured.out
        assert "turbine_id: WTG01" in captured.out
        assert "Detailed Results:" in captured.out
        assert "total_hours:" in captured.out
        assert "120" in captured.out
        assert "availability_pct:" in captured.out
        assert "95.83" in captured.out

    def test_show_analysis_result_complex(
        self, presenter, complex_analysis_result, capsys
    ):
        """Test display of complex analysis result with DataFrame."""
        presenter.show_analysis_result(
            complex_analysis_result, "EBA Cut-In/Cut-Out Analysis"
        )
        captured = capsys.readouterr()

        # Check that all sections are displayed
        assert "EBA Cut-In/Cut-Out Analysis" in captured.out
        assert "Status: SUCCESS" in captured.out
        assert "turbine_id: WTG02" in captured.out
        assert "summary:" in captured.out
        assert "total_real_energy" in captured.out
        assert "125000.5" in captured.out
        assert "data_table:" in captured.out
        assert "timestamp" in captured.out
        assert "wind_speed" in captured.out
        assert "monthly_performance:" in captured.out

    def test_show_analysis_result_with_large_dataframe(self, presenter, capsys):
        """Test display of result with large DataFrame (should be truncated)."""
        large_df = pd.DataFrame(
            {
                "index": range(100),
                "value": [i * 2 for i in range(100)],
            }
        )

        result = AnalysisResult(
            status="SUCCESS",
            metadata={"note": "Large dataset test"},
            requires_visuals=False,
            detailed_results={"large_table": large_df},
        )

        presenter.show_analysis_result(result, "Large Data Test")
        captured = capsys.readouterr()

        # Check truncation message
        assert "Showing first 50" in captured.out
        assert "more rows" in captured.out

    def test_display_dict_recursive(self, presenter, capsys):
        """Test recursive dictionary display."""
        nested_dict = {
            "level1": {"level2": {"level3": "deep_value", "level3_b": 42}},
            "list_data": [1, 2, 3],
        }

        presenter._display_dict(nested_dict, indent=0)
        captured = capsys.readouterr()

        assert "level1:" in captured.out
        assert "level2:" in captured.out
        assert "level3: deep_value" in captured.out
        assert "list_data:" in captured.out

    def test_info_method(self, presenter, capsys):
        """Test info method."""
        presenter.info("Test information message")
        captured = capsys.readouterr()
        assert "Test information message" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
