from __future__ import annotations
from typing import Any
from src.wind_turbine_analytics.presentation.presenter import PipelinePresenter


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
