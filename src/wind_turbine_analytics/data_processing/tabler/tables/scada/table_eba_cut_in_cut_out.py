from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class EbaCutInCutOutTabler(BaseTabler):
    def __init__(self):
        super().__init__(table_name="eba_cut_in_cut_out_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        pass²

    def _add_table_row(self, turbine_id: str, turbine_result: Dict[str, Any]) -> None:
        """
        Ajoute une ligne pour une turbine.

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'cut_in', 'cut_out', 'criterion'
        """
        pass
