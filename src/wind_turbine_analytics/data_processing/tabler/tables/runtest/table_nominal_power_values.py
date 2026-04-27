from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class NominalPowerValuesTabler(BaseTabler):
    """
    Tableau des valeurs observées pour la puissance nominale.

    Format: | WTG | Max Power [kW] | Max Wind Speed [m/s] | Status |
    """

    def __init__(self):
        super().__init__(table_name="nominal_power_values_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        return ["WTG", "Max Power [kW]", "Max Wind Speed [m/s]", "Status"]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'max_power_observed_kW',
                           'max_wind_speed_observed_ms', 'criterion_met'
        """
        max_power = turbine_result.get("max_power_observed_kW", 0.0)
        max_wind_speed = turbine_result.get("max_wind_speed_observed_ms", 0.0)
        criterion_met = turbine_result.get("criterion_met", False)

        self._table_data.append(
            {
                "wtg": turbine_id,
                "max_power_kw": self._format_number(max_power, decimals=2, unit="kW"),
                "max_wind_speed_ms": self._format_number(
                    max_wind_speed, decimals=2, unit="m/s"
                ),
                "status": self._format_status_cell(criterion_met),
            }
        )
