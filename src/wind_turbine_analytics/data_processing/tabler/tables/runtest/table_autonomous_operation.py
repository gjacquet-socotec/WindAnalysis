from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class AutonomousOperationTabler(BaseTabler):
    """
    Tableau pour le critère d'autonomie d'exploitation.

    Format: | WTG | Local Acknowledgements / Restarts | Criterion (<=3) [True/False] |
    """

    def __init__(self):
        super().__init__(table_name="autonomous_operation_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        return ["WTG", "Local Acknowledgements / Restarts", "Criterion (<=3)"]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'manual_restart_count' et 'criterion_met'
        """
        manual_restart_count = turbine_result.get("manual_restart_count", 0)
        criterion_met = turbine_result.get("criterion_met", False)

        self._table_data.append(
            {
                "wtg": turbine_id,
                "manual_restart_count": str(manual_restart_count),
                "criterion_met": self._format_status_cell(criterion_met),
            }
        )
