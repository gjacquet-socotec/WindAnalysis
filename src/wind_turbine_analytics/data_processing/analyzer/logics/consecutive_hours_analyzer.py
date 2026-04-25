from src.wind_turbine_analytics.data_processing.analyzer.base_analyzer import (
    BaseAnalyzer,
)

from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from src.wind_turbine_analytics.application.configuration.config_models import TurbineFarm

import logging
import pandas as pd
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    ValidationCriteria,
    Criterion,
)
from typing import Dict, Any


class ConsecutiveHoursAnalyzer(BaseAnalyzer):
    def __init__(self) -> None:
        super().__init__()

    def _compute(
        self,
        operation_data: pd.DataFrame,
        turbine_config: TurbineConfig,
        criteria: ValidationCriteria,
    ) -> Dict[str, Any]:
        # Extraire les informations de configuration
        test_start = pd.to_datetime(turbine_config.test_start)
        test_end = pd.to_datetime(turbine_config.test_end)
        mapping = turbine_config.mapping_operation_data
        timestamp_col = mapping.timestamp
        criteria_hours_threshold = criteria.validation_criterion.get(
            "consecutive_hours", Criterion()
        ).value

        # Accéder aux colonnes via le mapping
        df = operation_data.copy()
        df["timestamp"] = pd.to_datetime(df[timestamp_col])

        # Trier par timestamp
        df = df.sort_values("timestamp")

        # Filtrer entre test_start et test_end
        mask = (df["timestamp"] >= test_start) & (df["timestamp"] <= test_end)
        df_filtered = df[mask].copy()

        if len(df_filtered) == 0:
            return {
                "Data hours[h]": 0,
                f"Criterion (>={criteria_hours_threshold}h) [True/False]": False,
            }

        # Calculer les différences de temps entre enregistrements consécutifs
        df_filtered["time_diff"] = df_filtered["timestamp"].diff()

        # Définir un seuil d'interruption (ex: > 15 minutes = interruption)
        max_gap = pd.Timedelta(minutes=15)
        df_filtered["is_continuous"] = df_filtered["time_diff"] <= max_gap

        # Créer des groupes de périodes continues
        df_filtered["group"] = (~df_filtered["is_continuous"]).cumsum()

        # Pour chaque groupe continu, calculer la durée
        continuous_periods = df_filtered.groupby("group").agg(
            {"timestamp": ["min", "max"]}
        )

        continuous_periods.columns = ["start", "end"]
        continuous_periods["duration_hours"] = (
            continuous_periods["end"] - continuous_periods["start"]
        ).dt.total_seconds() / 3600

        # Trouver la période continue maximale
        max_duration = continuous_periods["duration_hours"].max()
        has_120h = max_duration >= criteria_hours_threshold

        return {
            "duration": round(max_duration, 2),
            "criterion": bool(has_120h),
        }
