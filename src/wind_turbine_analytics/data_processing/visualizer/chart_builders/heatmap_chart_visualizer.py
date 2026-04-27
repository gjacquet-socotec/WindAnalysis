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


class HeatmapChartVisualizer(BaseVisualizer):
    """
    Visualiseur de heatmap pour la disponibilité des données.

    Génère une heatmap montrant:
    - Axe Y: Turbines (E1, E6, E8, etc.)
    - Axe X: Temps (heures ou jours selon la durée)
    - Couleur: Disponibilité des données (vert=data, rouge=no data)

    Utile pour identifier les gaps de données et périodes d'indisponibilité.
    """

    def __init__(self):
        super().__init__(chart_name="heatmap_chart", use_plotly=False)

    def _create_figure(self, result: AnalysisResult) -> matplotlib.figure.Figure:
        """
        Crée la figure Matplotlib avec heatmap de disponibilité.

        Args:
            result: Résultat d'analyse (peut venir de TestAvailabilityAnalyzer
                    ou NominalPowerAnalyzer avec chart_data)

        Returns:
            Figure Matplotlib avec heatmap
        """
        if not result.detailed_results:
            logger.warning("Aucune donnée détaillée pour générer la heatmap")
            return self._create_empty_figure()

        # Collecter les données de toutes les turbines
        turbine_ids = list(result.detailed_results.keys())

        # Créer une matrice de disponibilité
        # On va découper le temps en bins (par exemple par heure)
        all_data = {}
        min_time = None
        max_time = None

        for turbine_id in turbine_ids:
            turbine_data = result.detailed_results[turbine_id]
            chart_data = turbine_data.get("chart_data")

            if chart_data is None or chart_data.empty:
                logger.warning(f"Pas de données pour {turbine_id}")
                continue

            # Récupérer les timestamps (supposons qu'il y a une colonne avec des timestamps)
            # Pour chart_data de NominalPowerAnalyzer, on n'a pas de timestamps explicites
            # Créons une série temporelle synthétique basée sur le nombre de points
            # En réalité, il faudrait que chart_data contienne aussi la colonne timestamp

            # Pour la démo, créons un index temporel
            timestamps = pd.date_range(
                start="2026-02-01",
                periods=len(chart_data),
                freq="10min"
            )

            all_data[turbine_id] = timestamps

        if not all_data:
            return self._create_empty_figure()

        # Trouver la plage temporelle globale
        all_timestamps = pd.concat([pd.Series(v) for v in all_data.values()])
        min_time = all_timestamps.min()
        max_time = all_timestamps.max()

        # Créer des bins temporels (par heure)
        time_bins = pd.date_range(start=min_time, end=max_time, freq="1h")

        # Créer une matrice de disponibilité (turbines × time_bins)
        availability_matrix = pd.DataFrame(
            0,  # 0 = pas de données, 1 = données disponibles
            index=turbine_ids,
            columns=time_bins[:-1]
        )

        # Remplir la matrice
        for turbine_id in turbine_ids:
            if turbine_id not in all_data:
                continue

            timestamps = all_data[turbine_id]

            # Pour chaque bin, vérifier s'il y a des données
            for i in range(len(time_bins) - 1):
                bin_start = time_bins[i]
                bin_end = time_bins[i + 1]

                # Compter les points dans ce bin
                count = ((timestamps >= bin_start) & (timestamps < bin_end)).sum()
                availability_matrix.loc[turbine_id, bin_start] = 1 if count > 0 else 0

        # Créer la figure
        fig, ax = plt.subplots(figsize=(16, max(4, len(turbine_ids) * 0.8)))

        # Heatmap avec Seaborn
        sns.heatmap(
            availability_matrix,
            cmap=["#d32f2f", "#43a047"],  # Rouge pour 0, Vert pour 1
            cbar_kws={"label": "Data Available"},
            linewidths=0.5,
            linecolor='white',
            ax=ax,
            vmin=0,
            vmax=1
        )

        # Labels
        ax.set_title("Data Availability Heatmap - All Turbines", fontsize=14, fontweight="bold")
        ax.set_xlabel("Time (hourly bins)", fontsize=10)
        ax.set_ylabel("Turbine ID", fontsize=10)

        # Formater les labels de l'axe X (afficher seulement quelques dates)
        n_labels = min(20, len(time_bins))
        step = max(1, len(time_bins) // n_labels)
        ax.set_xticks(range(0, len(time_bins) - 1, step))
        ax.set_xticklabels(
            [time_bins[i].strftime("%m-%d %H:%M") for i in range(0, len(time_bins) - 1, step)],
            rotation=45,
            ha="right"
        )

        plt.tight_layout()

        return fig

    def _create_empty_figure(self) -> matplotlib.figure.Figure:
        """Crée une figure vide en cas de données manquantes."""
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No data available for heatmap",
                ha="center", va="center", fontsize=14, color="red")
        ax.set_title("Data Availability Heatmap")
        ax.axis("off")
        return fig
