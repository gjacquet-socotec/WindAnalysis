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


class ConsecutiveHoursAnalyzer(BaseAnalyzer):
    def __init__(self) -> None:
        super().__init__()

    def _compute(
        self,
        operation_data: pd.DataFrame,
        log_data: pd.DataFrame,
        turbine_config: TurbineConfig,
        criteria: ValidationCriteria,
    ) -> Dict[str, Any]:

        # Extraire les informations de configuration
        mapping = turbine_config.mapping_operation_data
        timestamp_col = mapping.timestamp
        path_log_data = turbine_config.general_information.path_log_data
        criteria_hours_threshold = criteria.validation_criterion.get(
            "consecutive_hours", Criterion()
        ).value
        if log_data.empty:
            logger.error(
                f"Log data is empty for turbine {turbine_config.turbine_id} at {path_log_data}"
            )
            raise ValueError(
                f"Log data is empty for turbine {turbine_config.turbine_id}"
            )
        # Accéder aux colonnes via le mapping
        df = operation_data.copy()
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])

        # Convertir test_start et test_end en utilisant le MÊME dtype que la colonne timestamp
        # Cela garantit que les comparaisons fonctionnent correctement
        test_start = turbine_config.test_start
        test_end = turbine_config.test_end
        print(f"duration :  {test_end - test_start}")

        # S'assurer que la colonne timestamp n'a pas de timezone non plus
        if df[timestamp_col].dt.tz is not None:
            df[timestamp_col] = df[timestamp_col].dt.tz_localize(None)

        self._format_window(test_start, test_end)

        # Trier par timestamp
        df = df.sort_values(timestamp_col).reset_index(drop=True)

        # Filtrer entre test_start et test_end
        mask = (df[timestamp_col] >= test_start) & (df[timestamp_col] <= test_end)
        df_filtered = df[mask].copy()

        # Rechercher dans le fichier log data les partie ou il y a
        # TODO changer la logique du code. Voir les partie qui
        # TODO nouvelle logique du code : trouves les periode d'arrête dans le code et
        if len(df_filtered) == 0:
            return {
                "Data hours[h]": 0,
                f"Criterion (>={criteria_hours_threshold}h) [True/False]": False,
            }

        # Calculer les différences de temps entre enregistrements consécutifs
        df_filtered["time_diff"] = df_filtered[timestamp_col].diff()

        # Définir un seuil d'interruption (ex: > 15 minutes = interruption)
        max_gap = pd.Timedelta(minutes=15)
        df_filtered["is_continuous"] = df_filtered["time_diff"] <= max_gap

        # Créer des groupes de périodes continues
        df_filtered["group"] = (~df_filtered["is_continuous"]).cumsum()

        # Pour chaque groupe continu, calculer la durée
        continuous_periods = df_filtered.groupby("group").agg(
            {timestamp_col: ["min", "max"]}
        )

        continuous_periods.columns = ["start", "end"]
        continuous_periods["duration_hours"] = (
            continuous_periods["end"] - continuous_periods["start"]
        ).dt.total_seconds() / 3600

        # Trouver la période continue maximale
        # Ajouter 10 minutes pour pendre en compte les plages de temps
        max_duration = continuous_periods["duration_hours"].max() + 1 / 6
        has_120h = max_duration >= criteria_hours_threshold

        # Récupérer les dates de début et fin de la période maximale
        max_period_idx = continuous_periods["duration_hours"].idxmax()
        max_period_start = continuous_periods.loc[max_period_idx, "start"]
        max_period_end = continuous_periods.loc[max_period_idx, "end"]

        return {
            "duration": round(max_duration, 2),
            "criterion": bool(has_120h),
            "start_date": max_period_start,
            "end_date": max_period_end,
        }
