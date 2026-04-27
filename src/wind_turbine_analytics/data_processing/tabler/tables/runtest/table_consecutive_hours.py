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
        return ["WTG", "Data hours [h]", "Start date", "End date", "Status"]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'duration', 'criterion', 'start_date', 'end_date'
        """
        duration = turbine_result.get("duration", 0.0)
        criterion_met = turbine_result.get("criterion", False)
        start_date = turbine_result.get("start_date", "N/A")
        end_date = turbine_result.get("end_date", "N/A")

        # Formater les dates si ce sont des timestamps
        if hasattr(start_date, 'strftime'):
            start_date = start_date.strftime("%Y-%m-%d %H:%M")
        if hasattr(end_date, 'strftime'):
            end_date = end_date.strftime("%Y-%m-%d %H:%M")

        self._table_data.append(
            {
                "wtg": turbine_id,
                "data_hours": self._format_number(duration, decimals=2, unit="h"),
                "start_date": start_date,
                "end_date": end_date,
                "status": self._format_status_cell(criterion_met),
            }
        )
