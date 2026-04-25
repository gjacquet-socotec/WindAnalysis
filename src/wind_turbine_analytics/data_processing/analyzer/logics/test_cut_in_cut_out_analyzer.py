from src.wind_turbine_analytics.application.utils.load_data import load_csv
from src.wind_turbine_analytics.data_processing.analyzer.base_analyzer import (
    BaseAnalyzer,
)
from src.logger_config import get_logger
import pandas as pd
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    ValidationCriteria,
    Criterion,
)
from typing import Dict, Any
from src.wind_turbine_analytics.data_processing.log_code.generator_type.nordex_n311_log_code_manager import (
    NordexN311LogCodeManager,
)

logger = get_logger(__name__)


class TestCutInCutOutAnalyzer(BaseAnalyzer):
    def __init__(self) -> None:
        super().__init__()

    def _compute(
        self,
        operation_data: pd.DataFrame,
        turbine_config: TurbineConfig,
        criteria: ValidationCriteria,
    ) -> Dict[str, Any]:
        """
        Cette méthode doit retourner un dictionnaire avec les résultats
        Logics :

        STEP 1 : CREATE FILTERING:
        - Production > 0, wind speed between cut-in and cut-out,
        - including all downtimes (curtailments, maintenance, grid issues, etc.).
        - Check if the wind speed is between cut-in and cut-out speeds defined
          in the turbine configuration.
        - Check if the power production is greater than 0.

        STEP 2 : DETECT AVAILABLE AND UNAVAILABLE PERIODS:
        - List PERIODES where the FILTER is respected
        - Sum each PERIODE where the FILTER is respected
        - Make a table of the PERIODES where the FILTER is respected
          with their sum and their start and end date

        - List  PERIODES where the FILTER is not respected
        - Sum each PERIODE where the FILTER is not respected
        - Make a table of the PERIODES where the FILTER is not respected
         with their sum and their start and end date

        STEP 3 :  CRITERIA of SUCCESS
        - If one of the sum of the period is greater than the criteria defined
            in the configuration, then the test is a success, else it's a
            failure.

        """
        # Extraire les informations de configuration
        test_start = pd.to_datetime(turbine_config.test_start)
        test_end = pd.to_datetime(turbine_config.test_end)
        mapping = turbine_config.mapping_operation_data
        timestamp_col = mapping.timestamp
        path_log_data = turbine_config.general_information.path_log_data
        manager = NordexN311LogCodeManager()
        breakpoint()
        log_code_data = load_csv(path_log_data)

        if log_code_data.empty:
            logger.error(
                f"Log data is empty for turbine {turbine_config.turbine_id} at {path_log_data}"
            )
            raise ValueError(
                f"Log data is empty for turbine {turbine_config.turbine_id}"
            )

        df_of_test = operation_data.copy()
        df_of_test = df_of_test.where(timestamp_col >= test_start).where(
            timestamp_col <= test_end
        )

        # STEP 1 : CREATE FILTERING:
        # - Production > 0, wind speed between cut-in and cut-out,

        # STEP 2 : DETECT AVAILABLE AND UNAVAILABLE PERIODS:
        return {
            "test_start": test_start,
            "test_end": test_end,
            "timestamp_col": timestamp_col,
        }
