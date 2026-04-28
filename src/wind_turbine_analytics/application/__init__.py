"""Application layer public API."""

# Lazy imports to avoid circular dependencies
# Import these only when needed:
# - RunTestPipelineConfig, RunTestWorkflow, run_runtest_pipeline
# - ScadaRunnerConfig, ScadaWorkflow, run_scada_pipeline

__all__ = [
    "RunTestPipelineConfig",
    "RunTestWorkflow",
    "run_runtest_pipeline",
    "ScadaRunnerConfig",
    "ScadaWorkflow",
    "run_scada_pipeline",
]


def __getattr__(name):
    """Lazy import to avoid circular dependencies."""
    if name in ("RunTestPipelineConfig", "RunTestWorkflow", "run_runtest_pipeline"):
        from src.wind_turbine_analytics.application.workflows.runtest_workflow import (
            RunTestPipelineConfig,
            RunTestWorkflow,
            run_runtest_pipeline,
        )
        if name == "RunTestPipelineConfig":
            return RunTestPipelineConfig
        elif name == "RunTestWorkflow":
            return RunTestWorkflow
        elif name == "run_runtest_pipeline":
            return run_runtest_pipeline

    elif name in ("ScadaRunnerConfig", "ScadaWorkflow", "run_scada_pipeline"):
        from src.wind_turbine_analytics.application.workflows.scada_workflow import (
            ScadaRunnerConfig,
            ScadaWorkflow,
            run_scada_pipeline,
        )
        if name == "ScadaRunnerConfig":
            return ScadaRunnerConfig
        elif name == "ScadaWorkflow":
            return ScadaWorkflow
        elif name == "run_scada_pipeline":
            return run_scada_pipeline

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
