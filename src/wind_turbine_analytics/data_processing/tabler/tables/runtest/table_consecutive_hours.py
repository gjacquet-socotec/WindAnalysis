from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class ConsecutiveHoursTabler(BaseTabler):
    """
    Tableau pour le critère des heures consécutives.

    Format: | WTG | Data hours[h] | Criterion (>=120h) [True/False] |
    """

    def __init__(self):
        super().__init__(table_name="consecutive_hours_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        return ["WTG", "Data hours [h]", "Criterion (>=120h)"]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'duration' et 'criterion'
        """
        duration = turbine_result.get("duration", 0.0)
        criterion_met = turbine_result.get("criterion", False)

        self._table_data.append(
            {
                "wtg": turbine_id,
                "data_hours": self._format_number(duration, decimals=2, unit="h"),
                "criterion_met": self._format_status_cell(criterion_met),
            }
        )
