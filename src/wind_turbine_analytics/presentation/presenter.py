from __future__ import annotations


class PipelinePresenter:
    """Default no-op presenter implementation."""

    def show_test_results(self, result: Any) -> None:
        return None

    def show_test_park_summary(self, results: list[Any]) -> None:
        return None

    def info(self, message: str) -> None:
        return None
