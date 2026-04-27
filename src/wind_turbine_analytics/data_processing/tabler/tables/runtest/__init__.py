"""RunTest report tables."""

from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_consecutive_hours import (
    ConsecutiveHoursTabler,
)
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_cut_in_cut_out import (
    CutInCutOutTabler,
)
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_nominal_power_values import (
    NominalPowerValuesTabler,
)
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_nominal_power_duration import (
    NominalPowerDurationTabler,
)
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_autonomous_operation import (
    AutonomousOperationTabler,
)
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_availability import (
    AvailabilityTabler,
)
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_summary import (
    RunTestSummaryTabler,
)
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest.table_csv_files import (
    CsvFilesTabler,
)

__all__ = [
    "ConsecutiveHoursTabler",
    "CutInCutOutTabler",
    "NominalPowerValuesTabler",
    "NominalPowerDurationTabler",
    "AutonomousOperationTabler",
    "AvailabilityTabler",
    "RunTestSummaryTabler",
    "CsvFilesTabler",
]
