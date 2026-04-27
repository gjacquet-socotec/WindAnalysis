from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class NominalPowerDurationTabler(BaseTabler):
    """
    Tableau de la durée de la période à puissance nominale.

    Format: | WTG | Duration [h] | Start | End | Status |
    """

    def __init__(self):
        super().__init__(table_name="nominal_power_duration_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        return ["WTG", "Duration [h]", "Start", "End", "Status"]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'total_duration_hours',
                           'selected_window_start', 'selected_window_end', 'criterion_met'
        """
        duration = turbine_result.get("total_duration_hours", 0.0)
        start = turbine_result.get("selected_window_start", "N/A")
        end = turbine_result.get("selected_window_end", "N/A")
        criterion_met = turbine_result.get("criterion_met", False)

        # Formater les timestamps si ce sont des datetime
        if hasattr(start, "strftime"):
            start = start.strftime("%Y-%m-%d %H:%M")
        if hasattr(end, "strftime"):
            end = end.strftime("%Y-%m-%d %H:%M")

        self._table_data.append(
            {
                "wtg": turbine_id,
                "duration_hours": self._format_number(duration, decimals=2, unit="h"),
                "start": str(start),
                "end": str(end),
                "status": self._format_status_cell(criterion_met),
            }
        )
