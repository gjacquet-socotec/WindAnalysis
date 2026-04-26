"""Integration test for presenter with actual AnalysisResult from analyzers."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from src.wind_turbine_analytics.presentation.console_presenter import (
    ConsolePipelinePresenter,
)
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult


class TestPresenterIntegration:
    """Test presenter with realistic AnalysisResult structures."""

    @pytest.fixture
    def presenter(self):
        """Create a ConsolePipelinePresenter instance."""
        return ConsolePipelinePresenter()

    def test_analysis_result_with_none_metadata(self, presenter, capsys):
        """Test that AnalysisResult with None metadata doesn't crash."""
        result = AnalysisResult(
            status="completed",
            metadata=None,  # This should not crash
            requires_visuals=False,
            detailed_results={
                "WTG01": {"duration": 125.5, "criterion": True},
                "WTG02": {"duration": 115.0, "criterion": False},
            },
        )

        # This should not raise an exception
        presenter.show_analysis_result(result, "Test Analysis")
        captured = capsys.readouterr()

        # Check that output is generated
        assert "Test Analysis" in captured.out
        assert "completed" in captured.out
        assert "WTG01" in captured.out
        assert "125.5" in captured.out

    def test_analysis_result_default_values(self, presenter, capsys):
        """Test that default AnalysisResult values work correctly."""
        # Create AnalysisResult with default values (as returned by BaseAnalyzer)
        result = AnalysisResult(
            detailed_results={"turbine_1": {"value": 42}},
            status="completed",
            requires_visuals=False,
        )

        # Should not crash with default metadata=None
        presenter.show_analysis_result(result, "Default Values Test")
        captured = capsys.readouterr()

        assert "Default Values Test" in captured.out
        assert "completed" in captured.out
        assert "turbine_1" in captured.out
        assert "42" in captured.out

    def test_consecutive_hours_result_format(self, presenter, capsys):
        """Test format similar to ConsecutiveHoursAnalyzer output."""
        result = AnalysisResult(
            detailed_results={
                "WTG01": {"duration": 125.5, "criterion": True},
                "WTG02": {"duration": 115.0, "criterion": False},
                "WTG03": {"duration": 130.2, "criterion": True},
            },
            status="completed",
            requires_visuals=False,
        )

        presenter.show_analysis_result(result, "Consecutive Hours Analysis")
        captured = capsys.readouterr()

        # Verify all turbines are displayed
        assert "WTG01" in captured.out
        assert "WTG02" in captured.out
        assert "WTG03" in captured.out

        # Verify values are displayed
        assert "125.5" in captured.out
        assert "115.0" in captured.out
        assert "130.2" in captured.out

    def test_eba_result_format(self, presenter, capsys):
        """Test format similar to EbACutInCutOutAnalyzer output."""
        result = AnalysisResult(
            detailed_results={
                "WTG01": {
                    "total_real_energy": 125000.5,
                    "total_theoretical_energy": 130000.0,
                    "total_loss_energy": 4999.5,
                    "performance": 96.15,
                    "monthly_performance": [
                        {"month": "2024-01", "performance": 95.5},
                        {"month": "2024-02", "performance": 96.8},
                    ],
                }
            },
            status="completed",
            requires_visuals=True,
        )

        presenter.show_analysis_result(result, "EBA Analysis")
        captured = capsys.readouterr()

        assert "EBA Analysis" in captured.out
        assert "125000.5" in captured.out
        assert "96.15" in captured.out
        assert "monthly_performance" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
