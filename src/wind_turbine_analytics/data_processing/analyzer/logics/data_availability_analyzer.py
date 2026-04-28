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
import dateparser

logger = get_logger(__name__)


class DataAvailabilityAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()

    def _compute(
        self,
        operation_data: pd.DataFrame,
        log_data: pd.DataFrame,
        turbine_config: TurbineConfig,
        criteria: ValidationCriteria,
    ) -> Dict[str, Any]:

        test_start = turbine_config.test_start
        test_end = turbine_config.test_end
        mapping = turbine_config.mapping_operation_data
        timestamp_col = mapping.timestamp

        # Colonnes des variables d'intérêt
        wind_speed_col = mapping.wind_speed
        active_power_col = mapping.activation_power
        temperature_col = mapping.temperature
        wind_direction_col = mapping.wind_direction

        # S'assurer que les timestamps sont en datetime (si pas déjà fait par load_csv)
        if not pd.api.types.is_datetime64_any_dtype(operation_data[timestamp_col]):
            operation_data[timestamp_col] = pd.to_datetime(
                operation_data[timestamp_col], dayfirst=True, errors="coerce"
            )

        test_data = operation_data[
            (operation_data[timestamp_col] >= test_start)
            & (operation_data[timestamp_col] <= test_end)
        ].copy()

        # Créer une plage de temps par tranches de 10 minutes avec le même timezone
        time_range = pd.date_range(start=test_start, end=test_end, freq="10min")

        # Initialiser les listes pour construire le DataFrame
        timestamps = []
        wind_speed_availability = []
        active_power_availability = []
        wind_direction_availability = []
        overall_availability = []
        temperature_availability = [] if temperature_col else None

        # Pour chaque tranche de 10 minutes
        if not pd.api.types.is_float_dtype(test_data[wind_speed_col]):
            logger.warning(
                f"Wind speed column '{wind_speed_col}' is not numeric, "
                f"cannot compute availability for turbine {turbine_config.turbine_id}"
            )
            test_data[wind_speed_col] = pd.to_numeric(
                test_data[wind_speed_col], errors="coerce"
            )
        if not pd.api.types.is_float_dtype(test_data[active_power_col]):
            logger.warning(
                f"Active power column '{active_power_col}' is not numeric, "
                f"cannot compute availability for turbine {turbine_config.turbine_id}"
            )
            test_data[active_power_col] = pd.to_numeric(
                test_data[active_power_col], errors="coerce"
            )

        for i in range(len(time_range) - 1):
            start_interval = time_range[i]
            end_interval = time_range[i + 1]

            # Ajouter le timestamp de début de l'intervalle
            timestamps.append(start_interval)
            # Filtrer les données dans cette tranche
            interval_data = test_data[
                (test_data[timestamp_col] >= start_interval)
                & (test_data[timestamp_col] < end_interval)
            ]

            # Vérifier la présence de données pour chaque variable
            wind_speed_present = (
                1
                if not interval_data[wind_speed_col].isna().all()
                and len(interval_data) > 0
                else 0
            )
            active_power_present = (
                1
                if not interval_data[active_power_col].isna().all()
                and len(interval_data) > 0
                else 0
            )
            wind_direction_present = (
                1
                if not interval_data[wind_direction_col].isna().all()
                and len(interval_data) > 0
                else 0
            )

            wind_speed_availability.append(wind_speed_present)
            active_power_availability.append(active_power_present)
            wind_direction_availability.append(wind_direction_present)

            # Temperature (optionnel)
            if temperature_col:
                temperature_present = (
                    1
                    if not interval_data[temperature_col].isna().all()
                    and len(interval_data) > 0
                    else 0
                )
                temperature_availability.append(temperature_present)

            # Disponibilité globale : toutes les variables obligatoires sont présentes
            overall_present = (
                wind_speed_present and active_power_present and wind_direction_present
            )
            overall_availability.append(1 if overall_present else 0)

        # Créer le DataFrame avec timestamp et disponibilités
        availability_data = {
            "timestamp": timestamps,
            "wind_speed": wind_speed_availability,
            "active_power": active_power_availability,
            "wind_direction": wind_direction_availability,
            "overall": overall_availability,
        }

        if temperature_col:
            availability_data["temperature"] = temperature_availability

        availability_df = pd.DataFrame(availability_data)

        # Calculer les statistiques de disponibilité
        total_intervals = len(time_range) - 1
        summary = {
            "total_intervals": total_intervals,
            "wind_speed_availability_pct": (
                (sum(wind_speed_availability) / total_intervals * 100)
                if total_intervals > 0
                else 0
            ),
            "active_power_availability_pct": (
                (sum(active_power_availability) / total_intervals * 100)
                if total_intervals > 0
                else 0
            ),
            "wind_direction_availability_pct": (
                (sum(wind_direction_availability) / total_intervals * 100)
                if total_intervals > 0
                else 0
            ),
            "overall_availability_pct": (
                (sum(overall_availability) / total_intervals * 100)
                if total_intervals > 0
                else 0
            ),
        }

        if temperature_col:
            summary["temperature_availability_pct"] = (
                sum(temperature_availability) / total_intervals * 100
                if total_intervals > 0
                else 0
            )
        return {"availability_table": availability_df, "summary": summary}
