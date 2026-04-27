from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class CutInCutOutTabler(BaseTabler):
    """
    Tableau pour le critère cut-in à cut-out.

    Format: | WTG | Data hours[h] | Criterion (>=72h) [True/False] |
    """

    def __init__(self):
        super().__init__(table_name="cut_in_cut_out_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        return ["WTG", "Data hours [h]", "Criterion (>=72h)"]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'max_net_duration_hours' et 'criterion_met'
        """
        duration = turbine_result.get("max_net_duration_hours", 0.0)
        criterion_met = turbine_result.get("criterion_met", False)

        self._table_data.append(
            {
                "wtg": turbine_id,
                "data_hours": self._format_number(duration, decimals=2, unit="h"),
                "criterion_met": self._format_status_cell(criterion_met),
            }
        )
