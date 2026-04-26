"""Example demonstrating ConsolePipelinePresenter usage with workflows."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from src.wind_turbine_analytics.presentation.console_presenter import (
    ConsolePipelinePresenter,
)
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def example_simple_result():
    """Example 1: Display a simple analysis result."""
    print("\n" + "=" * 100)
    print("EXAMPLE 1: Simple Analysis Result")
    print("=" * 100)

    presenter = ConsolePipelinePresenter()

    # Create a simple result (like ConsecutiveHoursAnalyzer might return)
    result = AnalysisResult(
        status="PASS",
        metadata={
            "turbine_id": "WTG01",
            "test_start": "2024-01-01 00:00:00",
            "test_end": "2024-05-31 23:50:00",
        },
        requires_visuals=True,
        detailed_results={
            "consecutive_hours": 125.5,
            "threshold": 120.0,
            "criterion_met": True,
        },
    )

    presenter.show_analysis_result(result, "Consecutive Hours Analysis")


def example_eba_result():
    """Example 2: Display an EBA analysis result with monthly data."""
    print("\n" + "=" * 100)
    print("EXAMPLE 2: EBA Analysis Result with Monthly Performance")
    print("=" * 100)

    presenter = ConsolePipelinePresenter()

    # Create a result similar to EbACutInCutOutAnalyzer
    result = AnalysisResult(
        status="COMPLETE",
        metadata={
            "turbine_id": "WTG02",
            "analysis_period": "2024-01-01 to 2024-12-31",
            "wind_speed_range": "3-25 m/s",
        },
        requires_visuals=True,
        detailed_results={
            "total_real_energy": 1250000.75,
            "total_theoretical_energy": 1300000.0,
            "total_loss_energy": 49999.25,
            "performance": 96.15,
            "monthly_performance": [
                {"month": "2024-01", "performance": 95.5},
                {"month": "2024-02", "performance": 96.8},
                {"month": "2024-03", "performance": 97.2},
                {"month": "2024-04", "performance": 96.0},
                {"month": "2024-05", "performance": 95.8},
            ],
        },
    )

    presenter.show_analysis_result(result, "EBA Cut-In/Cut-Out Analysis")


def example_data_availability_result():
    """Example 3: Display a data availability result with DataFrame."""
    print("\n" + "=" * 100)
    print("EXAMPLE 3: Data Availability Analysis with DataFrame")
    print("=" * 100)

    presenter = ConsolePipelinePresenter()

    # Create sample availability data
    availability_df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=10, freq="10min"),
            "wind_speed": [1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
            "active_power": [1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
            "wind_direction": [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            "overall": [1, 1, 0, 0, 0, 1, 0, 1, 0, 1],
        }
    )

    result = AnalysisResult(
        status="COMPLETE",
        metadata={"turbine_id": "WTG03", "total_intervals": 10},
        requires_visuals=False,
        detailed_results={
            "availability_table": availability_df,
            "summary": {
                "total_intervals": 10,
                "wind_speed_availability_pct": 80.0,
                "active_power_availability_pct": 80.0,
                "wind_direction_availability_pct": 90.0,
                "overall_availability_pct": 50.0,
            },
        },
    )

    presenter.show_analysis_result(result, "Data Availability Analysis")


def example_none_result():
    """Example 4: Display a None result (error handling)."""
    print("\n" + "=" * 100)
    print("EXAMPLE 4: Handling None Result")
    print("=" * 100)

    presenter = ConsolePipelinePresenter()
    presenter.show_analysis_result(None, "Failed Analysis")


def example_large_dataframe():
    """Example 5: Display result with large DataFrame (truncation test)."""
    print("\n" + "=" * 100)
    print("EXAMPLE 5: Large DataFrame Truncation")
    print("=" * 100)

    presenter = ConsolePipelinePresenter()

    # Create a large DataFrame (100 rows)
    large_df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="10min"),
            "wind_speed": [i * 0.1 + 5 for i in range(100)],
            "power": [i * 10 + 1000 for i in range(100)],
            "status": ["OK"] * 100,
        }
    )

    result = AnalysisResult(
        status="COMPLETE",
        metadata={"turbine_id": "WTG04", "note": "Large dataset for testing"},
        requires_visuals=False,
        detailed_results={
            "full_data": large_df,
            "summary_stats": {
                "total_rows": len(large_df),
                "avg_wind_speed": large_df["wind_speed"].mean(),
                "avg_power": large_df["power"].mean(),
            },
        },
    )

    presenter.show_analysis_result(result, "Large Dataset Analysis")


def main():
    """Run all examples."""
    print("\n" + "█" * 100)
    print("ConsolePipelinePresenter - Usage Examples")
    print("█" * 100)

    example_simple_result()
    example_eba_result()
    example_data_availability_result()
    example_none_result()
    example_large_dataframe()

    print("\n" + "█" * 100)
    print("All examples completed successfully!")
    print("█" * 100)


if __name__ == "__main__":
    main()
