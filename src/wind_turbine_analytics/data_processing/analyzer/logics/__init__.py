"""RunTest analysis logics."""

from src.wind_turbine_analytics.data_processing.analyzer.logics.consecutive_hours_analyzer import (
    ConsecutiveHoursAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.test_cut_in_cut_out_analyzer import (
    TestCutInCutOutAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.nominal_power_analyzer import (
    NominalPowerAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.autonomous_operation import (
    AutonomousOperationAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.test_availability_analyzer import (
    TestAvailabilityAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.data_availability_analyzer import (
    DataAvailabilityAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_cut_in_cut_out_analyzer import (
    EbACutInCutOutAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_manifacturer_analyzer import (
    EbaManufacturerAnalyzer,
)
from src.wind_turbine_analytics.data_processing.analyzer.logics.code_error_analyzer import (
    CodeErrorAnalyzer,
)

__all__ = [
    # RunTest analyzers
    "ConsecutiveHoursAnalyzer",
    "TestCutInCutOutAnalyzer",
    "NominalPowerAnalyzer",
    "AutonomousOperationAnalyzer",
    "TestAvailabilityAnalyzer",
    # SCADA analyzers
    "DataAvailabilityAnalyzer",
    "EbACutInCutOutAnalyzer",
    "EbaManufacturerAnalyzer",
    "CodeErrorAnalyzer",
]
