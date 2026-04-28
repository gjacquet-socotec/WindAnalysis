from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from typing import Any


class EbaLossVisualizer(BaseVisualizer):
    """
    Constructeur de graphique pour l'énergie produite.
    """

    def __init__(self):
        super().__init__(chart_name="energy_chart")

    def _create_graph(self, result: AnalysisResult) -> None:
        """
        Implémente la logique de construction du graphique d'énergie perdue.
        """
        pass
