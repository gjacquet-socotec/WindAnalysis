from src.logger_config import get_logger
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineFarm,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from typing import Dict, Any
from src.wind_turbine_analytics.application.utils.load_data import (
    load_csv,
    CSVLoadError,
)
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineMappingOperationData,
    ValidationCriteria,
    Criterion,
)

logger = get_logger(__name__)


class BaseAnalyzer:

    def analyze(
        self, turbines_farm: TurbineFarm, criteria: ValidationCriteria
    ) -> AnalysisResult:
        results = {}
        for turbine_id, turbine_data in turbines_farm.farm.items():
            try:
                # Extraire le path des données d'opération
                if not turbine_data.general_information:
                    logger.warning(
                        f"Pas d'informations générales pour la turbine {turbine_id}"
                    )
                    continue

                path_operation_data = (
                    turbine_data.general_information.path_operation_data
                )
                if not path_operation_data:
                    logger.warning(
                        f"Pas de chemin de données d'opération pour la turbine {turbine_id}"
                    )
                    continue

                # Charger les données d'opération
                logger.info(
                    f"Chargement des données pour la turbine {turbine_id} depuis {path_operation_data}"
                )
                operation_data = load_csv(path_operation_data)
                # TODO: Implémenter la logique d'analyse des heures consécutives
                results[turbine_id] = self._compute(
                    operation_data,
                    turbine_data,
                    criteria,
                )

            except CSVLoadError as e:
                logger.error(
                    f"Erreur de chargement CSV pour la turbine {turbine_id}: {e}"
                )
                results[turbine_id] = {"error": str(e)}
            except Exception as e:
                logger.error(f"Erreur inattendue pour la turbine {turbine_id}: {e}")
                results[turbine_id] = {"error": str(e)}
        return AnalysisResult(
            detailed_results=results, status="completed", requires_visuals=False
        )

    def _compute(
        self,
        operation_data: pd.DataFrame,
        turbine_config: TurbineConfig,
        criteria: ValidationCriteria,
    ) -> Dict[str, Any]:
        """Placeholder for the main analysis logic."""
        raise NotImplementedError(
            "L'analyse des heures consécutives n'est pas encore implémentée."
        )

    def generate_synthetic_power_curve(
        self,
        operation_data: pd.DataFrame,
        turbine_config: TurbineConfig,
        criteria: ValidationCriteria,
    ) -> interp1d:
        """
        Generate a synthetic power curve based on operation data.

        Interpolates power points using 95th percentile per 0.5 m/s wind speed bin.
        This creates a realistic theoretical baseline that represents optimal performance.

        Args:
            operation_data: DataFrame containing operational data
            turbine_config: Configuration for the turbine
            criteria: Validation criteria containing cut-in/cut-out specifications

        Returns:
            interp1d: Interpolation function for the power curve
        """
        mapping = turbine_config.mapping_operation_data
        wind_speed_col = mapping.wind_speed
        power_col = mapping.activation_power
        P_nom = turbine_config.general_information.nominal_power

        if P_nom is None:
            logger.warning(
                "Nominal power not provided for turbine %s. Defaulting to 3780.0 kW for synthetic power curve generation.",
                turbine_config.turbine_id,
            )
            P_nom = 3780.0  # Default nominal power in kW (ex: 3.78 MW)
        if P_nom <= 20:
            logger.info(
                "Nominal power for turbine %s is very low (%s kW)."
                " This may indicate an issue with the configuration. "
                "Multiplying by 1000.",
                turbine_config.turbine_id,
                P_nom,
            )
            P_nom = P_nom * 1000  # Default nominal power in kW (ex: 3.78 MW)

        [v_min, v_max] = criteria.validation_criterion.get(
            "cut_in_to_cut_out", Criterion()
        ).specification

        df_curve = operation_data[[wind_speed_col, power_col]].copy()
        # Filter: keep only data with significant production AND within wind speed range
        # This avoids including low-performance periods that would bias the theoretical curve downward
        df_curve = df_curve[
            (df_curve[power_col] > 0.01 * P_nom) & (df_curve[wind_speed_col] <= v_max)
        ]
        bins = np.arange(v_min, v_max + 0.5, 0.5)
        df_curve["wind_bin"] = pd.cut(df_curve[wind_speed_col], bins)
        # Use 95th percentile instead of median to represent optimal performance
        # This creates a more realistic theoretical baseline and prevents performance > 100%
        power_curve = df_curve.groupby("wind_bin")[power_col].quantile(0.95)

        bin_centers = np.array([interval.mid for interval in power_curve.index])

        power_curve = interp1d(
            bin_centers, power_curve.values, bounds_error=False, fill_value=0.0
        )

        return power_curve
