from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class AvailabilityTabler(BaseTabler):
    """
    Tableau pour le critère de disponibilité.

    Format: | WTG | Availability (%) | WTG OK [h] | Warning [h] | Criterion (>=92%) [True/False] |
    """

    def __init__(self):
        super().__init__(table_name="availability_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        return [
            "WTG",
            "Availability (%)",
            "WTG OK [h]",
            "Warning [h]",
            "Criterion (>=92%)",
        ]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'availability_percent',
                           'available_hours', 'unauthorized_downtime_hours', 'criterion_met'
        """
        availability_percent = turbine_result.get("availability_percent", 0.0)
        available_hours = turbine_result.get("available_hours", 0.0)
        downtime_hours = turbine_result.get("unauthorized_downtime_hours", 0.0)
        criterion_met = turbine_result.get("criterion_met", False)

        self._table_data.append(
            {
                "wtg": turbine_id,
                "availability_percent": self._format_number(
                    availability_percent, decimals=2, unit="%"
                ),
                "wtg_ok_hours": self._format_number(
                    available_hours, decimals=2, unit="h"
                ),
                "warning_hours": self._format_number(downtime_hours, decimals=2, unit="h"),
                "criterion_met": self._format_status_cell(criterion_met),
            }
        )
