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

logger = get_logger(__name__)


class NominalPowerAnalyzer(BaseAnalyzer):
    def __init__(self) -> None:
        super().__init__()

    def _compute(
        self,
        operation_data: pd.DataFrame,
        turbine_config: TurbineConfig,
        criteria: ValidationCriteria,
    ) -> Dict[str, Any]:
        """
        Analyse de la puissance nominale d'une turbine.

        Logique:
        STEP 1: Filtrer les données sur la période de test
        STEP 2: Détecter les périodes où power >= specification% * P_nom
        STEP 3: Calculer la durée cumulée totale
        STEP 4: Valider si durée >= value (heures requises)
        """
        # Extraire les informations de configuration
        test_start = pd.to_datetime(turbine_config.test_start, dayfirst=True)
        test_end = pd.to_datetime(turbine_config.test_end, dayfirst=True)
        mapping = turbine_config.mapping_operation_data
        timestamp_col = mapping.timestamp
        power_col = mapping.activation_power
        P_nom = turbine_config.general_information.nominal_power

        # Vérification de la puissance nominale
        if P_nom is None:
            logger.error(
                f"Nominal power not defined for turbine " f"{turbine_config.turbine_id}"
            )
            raise ValueError(f"Nominal power missing for {turbine_config.turbine_id}")

        # Convertir en kW si nécessaire (si < 100, c'est probablement en MW)
        if P_nom <= 100:
            logger.info(
                f"Nominal power for turbine {turbine_config.turbine_id} "
                f"is {P_nom} MW, converting to kW"
            )
            P_nom = P_nom * 1000  # Convertir MW en kW

        # Récupérer les critères
        nominal_criterion = criteria.validation_criterion.get(
            "nominal_power_hours", Criterion()
        )
        required_hours = nominal_criterion.value
        power_threshold_percent = nominal_criterion.specification

        # Calculer le seuil de puissance
        power_threshold = (power_threshold_percent / 100.0) * P_nom

        logger.info(
            f"Analyse puissance nominale pour {turbine_config.turbine_id}: "
            f"P_nom={P_nom}kW, seuil={power_threshold_percent}% "
            f"({power_threshold:.2f}kW), durée requise={required_hours}h"
        )

        # Copier et filtrer les données opérationnelles
        df = operation_data.copy()
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], dayfirst=True)
        df = df.sort_values(timestamp_col)

        # Filtrer sur la période de test
        mask_test_period = (df[timestamp_col] >= test_start) & (
            df[timestamp_col] <= test_end
        )
        df_filtered = df[mask_test_period].copy()

        if len(df_filtered) == 0:
            logger.warning("Aucune donnée dans la période de test")
            return {
                "nominal_power_periods": [],
                "total_duration_hours": 0.0,
                "required_hours": required_hours,
                "criterion_met": False,
                "power_threshold_kW": power_threshold,
                "power_threshold_percent": power_threshold_percent,
            }

        # STEP 2: Filtrer power >= seuil
        df_filtered["above_threshold"] = df_filtered[power_col] >= power_threshold

        # Détecter l'intervalle de mesure (temps entre 2 points)
        if len(df_filtered) > 1:
            time_diffs = df_filtered[timestamp_col].diff().dt.total_seconds() / 3600
            # Utiliser la médiane pour éviter les outliers
            measurement_interval_hours = time_diffs.median()
        else:
            measurement_interval_hours = 0.167  # 10 minutes par défaut

        logger.info(
            f"Intervalle de mesure détecté: "
            f"{measurement_interval_hours * 60:.1f} minutes"
        )

        # Détecter les périodes continues
        df_filtered["period_change"] = (
            df_filtered["above_threshold"] != df_filtered["above_threshold"].shift()
        )
        df_filtered["group"] = df_filtered["period_change"].cumsum()

        # Agréger par groupe
        periods = df_filtered.groupby("group").agg(
            {
                timestamp_col: ["min", "max", "count"],
                "above_threshold": "first",
            }
        )

        periods.columns = ["start", "end", "count", "above_threshold"]

        # Calculer durée = nombre de points × intervalle
        periods["duration_hours"] = periods["count"] * measurement_interval_hours

        # Filtrer seulement les périodes au-dessus du seuil
        above_threshold_periods = periods[periods["above_threshold"]].copy()

        # STEP 3: Calculer la durée totale cumulée
        total_duration = above_threshold_periods["duration_hours"].sum()

        # STEP 4: Valider le critère
        criterion_met = total_duration >= required_hours

        # Identifier les valeurs maximales dans la période de test
        max_power = df_filtered[power_col].max()
        max_power_idx = df_filtered[power_col].idxmax()
        max_power_timestamp = df_filtered.loc[max_power_idx, timestamp_col]

        # Si wind_speed existe, récupérer aussi la vitesse max
        wind_speed_col = mapping.wind_speed
        if wind_speed_col and wind_speed_col in df_filtered.columns:
            max_wind_speed = df_filtered[wind_speed_col].max()
            max_wind_idx = df_filtered[wind_speed_col].idxmax()
            max_wind_timestamp = df_filtered.loc[max_wind_idx, timestamp_col]
        else:
            max_wind_speed = None
            max_wind_timestamp = None

        logger.info(
            f"Durée totale >= {power_threshold_percent}% P_nom: "
            f"{total_duration:.2f}h, Critère: {required_hours}h, "
            f"Réussi: {criterion_met}"
        )
        logger.info(
            f"Puissance max observée: {max_power:.2f}kW " f"le {max_power_timestamp}"
        )
        if max_wind_speed is not None:
            logger.info(
                f"Vitesse vent max observée: {max_wind_speed:.2f}m/s "
                f"le {max_wind_timestamp}"
            )

        # Préparer les détails des périodes
        period_details = []
        for _, period in above_threshold_periods.iterrows():
            period_details.append(
                {
                    "start": period["start"],
                    "end": period["end"],
                    "duration_hours": round(period["duration_hours"], 2),
                }
            )
        result = {
            "nominal_power_periods": period_details,
            "total_duration_hours": round(total_duration, 2),
            "required_hours": required_hours,
            "criterion_met": criterion_met,
            "power_threshold_kW": round(power_threshold, 2),
            "power_threshold_percent": power_threshold_percent,
            "nominal_power_kW": P_nom,
            "max_power_observed_kW": round(max_power, 2),
            "max_power_timestamp": max_power_timestamp,
        }

        if max_wind_speed is not None:
            result["max_wind_speed_observed_ms"] = round(max_wind_speed, 2)
            result["max_wind_speed_timestamp"] = max_wind_timestamp

        return result
