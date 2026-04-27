from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from typing import Any


class WindRoseChartVisualizer(BaseVisualizer):
    """
    Constructeur de graphique en rose des vents.
    """

    def __init__(self):
        super().__init__(chart_name="wind_rose_chart")

    def generate(self, result: AnalysisResult) -> None:
        """
        Implémente la logique de construction du graphique en rose des vents.

        Args:
            result: Données nécessaires pour construire le graphique.

        Setps:
            STEP 1: Extraire les données de vitesse de vent
            STEP 2: Extraire les données de direction de vent
            STEP 3: Construire le graphique en rose des vents avec plolty
            STEP 4: savegarder dans le dossir de sortie et retourner le plotly
              en format JSON (pour l'affichage dans le dashboard web (à venir bientôt))
        """
