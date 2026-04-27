from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from typing import Any


class HeatmapChartVisualizer(BaseVisualizer):
    """
    Constructeur de graphique de type heatmap.
    """

    def __init__(self):
        super().__init__(chart_name="heatmap_chart")

    def generate(self, result: AnalysisResult) -> None:
        """
        Implémente la logique de construction du graphique de type heatmap.

        Args:
            result: Données nécessaires pour construire le graphique.

        Setps:
            STEP 1: Extraire les données nécessaires pour la heatmap
            STEP 2: Construire le graphique de type heatmap avec plolty
            STEP 3: savegarder dans le dossir de sortie et retourner le plotly
              en format JSON (pour l'affichage dans le dashboard web (à venir bientôt))
        """
        pass
