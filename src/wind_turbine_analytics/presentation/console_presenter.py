from __future__ import annotations
from typing import Any, Dict
import pandas as pd
from src.wind_turbine_analytics.presentation.presenter import PipelinePresenter
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult


class ConsolePipelinePresenter(PipelinePresenter):
    """Console renderer for pipeline progress and criterion tables."""

    def show_test_results(self, result: Any) -> None:
        print("\n" + "=" * 96)
        print(
            f"Turbine {result.turbine_id} | "
            f"Runtest: {result.test_start:%Y-%m-%d %H:%M} -> "
            f"{result.test_end:%Y-%m-%d %H:%M}"
        )
        print("-" * 96)
        print(f"{'Criterion':<52} {'Measured':<18} {'Threshold':<18} {'Status':<8}")
        print("-" * 96)
        for item in result.criteria_results:
            print(
                f"{item.label:<52} {item.measured_value:<18} "
                f"{item.threshold_value:<18} {item.status:<8}"
            )

        for item in result.criteria_results:
            print("\n" + item.label)
            print(f"Selected window: {item.selected_window}")
            print(item.details.to_string(index=False))

        if result.notes:
            print("\nNotes:")
            for note in result.notes:
                print(f"- {note}")

    def show_test_park_summary(self, results: list[Any]) -> None:
        print("\n" + "=" * 96)
        print("Park summary")
        print("-" * 96)
        print(f"{'Turbine':<10} {'Success':<10} {'Fail':<8} {'Total':<8}")
        print("-" * 96)
        for item in results:
            total = len(item.criteria_results)
            print(
                f"{item.turbine_id:<10} {item.success_count:<10} "
                f"{item.fail_count:<8} {total:<8}"
            )

    def info(self, message: str) -> None:
        print(message)

    def show_analysis_result(self, result: AnalysisResult, analysis_name: str) -> None:
        """Display analysis results in a structured way."""
        if result is None:
            print(f"\n[WARNING] No results for {analysis_name}")
            return

        print("\n" + "=" * 100)
        print(f"Analysis: {analysis_name}")
        print("=" * 100)

        # Display status if available
        if result.status:
            print(f"Status: {result.status}")
            print("-" * 100)

        # Display metadata if available
        if result.metadata and isinstance(result.metadata, dict):
            print("\nMetadata:")
            self._display_dict(result.metadata, indent=2)
            print("-" * 100)

        # Display detailed results
        if result.detailed_results:
            print("\nDetailed Results:")
            self._display_detailed_results(result.detailed_results)

        print("=" * 100)

    def _display_dict(self, data: Dict[str, Any], indent: int = 0) -> None:
        """Recursively display dictionary content with proper indentation."""
        if not isinstance(data, dict):
            print(f"{' ' * indent}[Invalid data type: {type(data).__name__}]")
            return

        prefix = " " * indent
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                self._display_dict(value, indent + 2)
            elif isinstance(value, (list, tuple)):
                print(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        self._display_dict(item, indent + 4)
                    else:
                        print(f"{prefix}  - {item}")
            elif isinstance(value, pd.DataFrame):
                print(f"{prefix}{key}:")
                self._display_dataframe(value, indent + 2)
            else:
                print(f"{prefix}{key}: {value}")

    def _display_detailed_results(self, detailed_results: Dict[str, Any]) -> None:
        """Display detailed results with proper formatting for different data types."""
        for key, value in detailed_results.items():
            print(f"\n  {key}:")

            if isinstance(value, pd.DataFrame):
                self._display_dataframe(value, indent=4)
            elif isinstance(value, dict):
                # Check if it's a summary dict or nested structure
                if any(isinstance(v, (pd.DataFrame, list, dict)) for v in value.values()):
                    self._display_dict(value, indent=4)
                else:
                    # Simple key-value pairs
                    for k, v in value.items():
                        print(f"    {k}: {v}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._display_dict(item, indent=6)
                    else:
                        print(f"    - {item}")
            else:
                print(f"    {value}")

    def _display_dataframe(self, df: pd.DataFrame, indent: int = 0) -> None:
        """Display a pandas DataFrame with proper formatting."""
        prefix = " " * indent

        # Limit display for very large DataFrames
        max_rows = 50
        if len(df) > max_rows:
            print(f"{prefix}[Showing first {max_rows} of {len(df)} rows]")
            df_to_display = df.head(max_rows)
        else:
            df_to_display = df

        # Convert DataFrame to string and add indentation
        df_str = df_to_display.to_string(index=True, max_rows=max_rows)
        for line in df_str.split("\n"):
            print(f"{prefix}{line}")

        if len(df) > max_rows:
            print(f"{prefix}... ({len(df) - max_rows} more rows)")
