from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
import matplotlib.pyplot as plt
import matplotlib.figure
import seaborn as sns
import pandas as pd
import numpy as np
from src.logger_config import get_logger

logger = get_logger(__name__)


class WindHistogramChartVisualizer(BaseVisualizer):
    """
    Visualiseur d'histogramme de vitesse de vent binné.

    Génère un histogramme avec grid layout (1 subplot par turbine):
    - Bins: [0-3, 3-5, 5-10, 10-15, 15-20, 20-25, >25 m/s]
    - Seaborn histplot ou barplot
    - Affichage du nombre d'occurrences par bin
    """

    def __init__(self):
        super().__init__(chart_name="wind_histogram_chart", use_plotly=False)

    def _create_figure(self, result: AnalysisResult) -> matplotlib.figure.Figure:
        """
        Crée la figure Matplotlib avec grid layout pour toutes les turbines.

        Args:
            result: Résultat de NominalPowerAnalyzer (contient chart_data)

        Returns:
            Figure Matplotlib avec histogrammes
        """
        if not result.detailed_results:
            logger.warning("Aucune donnée détaillée pour générer l'histogramme")
            return self._create_empty_figure()

        # Nombre de turbines
        turbine_ids = list(result.detailed_results.keys())
        n_turbines = len(turbine_ids)

        # Calculer la disposition du grid
        n_cols = min(n_turbines, 3)
        n_rows = (n_turbines + n_cols - 1) // n_cols

        # Créer la figure et les axes
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows))

        # Assurer que axes est toujours un array 2D
        if n_turbines == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)

        # Définir les bins de vitesse
        wind_bins = [0, 3, 5, 10, 15, 20, 25, 100]
        wind_labels = ["0-3", "3-5", "5-10", "10-15", "15-20", "20-25", ">25"]
        colors = sns.color_palette("Blues_d", len(wind_labels))

        # Tracer pour chaque turbine
        for idx, turbine_id in enumerate(turbine_ids):
            turbine_data = result.detailed_results[turbine_id]

            # Position dans le grid
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]

            # Récupérer chart_data
            chart_data = turbine_data.get("chart_data")

            if chart_data is None or chart_data.empty:
                logger.warning(f"Pas de données pour {turbine_id}")
                ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
                ax.set_title(f"WTG {turbine_id}")
                continue

            # Créer les bins
            wind_speed = chart_data["wind_speed"]
            binned = pd.cut(wind_speed, bins=wind_bins, labels=wind_labels, include_lowest=True)

            # Compter les occurrences
            counts = binned.value_counts().sort_index()

            # Barplot avec Seaborn
            sns.barplot(
                x=counts.index.astype(str),
                y=counts.values,
                palette=colors,
                ax=ax
            )

            # Annotations
            ax.set_title(f"WTG {turbine_id}", fontsize=12, fontweight="bold")
            ax.set_xlabel("Wind Speed [m/s]", fontsize=10)
            ax.set_ylabel("Frequency (count)", fontsize=10)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)

            # Ajouter les valeurs sur les barres
            for i, v in enumerate(counts.values):
                ax.text(i, v, str(v), ha='center', va='bottom', fontsize=9)

        # Supprimer les axes vides
        for idx in range(n_turbines, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            fig.delaxes(axes[row, col])

        # Titre global
        fig.suptitle("Wind Speed Distribution - All Turbines", fontsize=14, fontweight="bold")
        plt.tight_layout(rect=[0, 0, 1, 0.97])

        return fig

    def _create_empty_figure(self) -> matplotlib.figure.Figure:
        """Crée une figure vide en cas de données manquantes."""
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No data available for wind histogram",
                ha="center", va="center", fontsize=14, color="red")
        ax.set_title("Wind Histogram Analysis")
        ax.axis("off")
        return fig
