from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from typing import Any


class EbaManifacturerVisualizer(BaseVisualizer):
    """
    Constructeur de graphique pour l'énergie produite.
    """

    def __init__(self):
        super().__init__(chart_name="energy_chart")

    def _create_graph(self, result: AnalysisResult) -> None:
        """
        Implémente la logique de construction du graphique d'énergie produite.

        Args:
            result: Données nécessaires pour construire le graphique.

        Setps:
            STEP 1: Extraire les données d'énergie produite
            STEP 2: Construire le graphique d'énergie produite avec plolty
            STEP 3: savegarder dans le dossir de sortie et retourner le plotly
              en format JSON (pour l'affichage dans le dashboard web (à venir bientôt))
        """
        pass
