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
    Visualiseur d'histogramme de vitesse de vent avec bins de 0.5 m/s.
    """

    def __init__(self):
        super().__init__(chart_name="wind_histogram_chart", use_plotly=False)

    def _create_figure(self, result: AnalysisResult) -> matplotlib.figure.Figure:
        if not result.detailed_results:
            logger.warning("Aucune donnée détaillée pour générer l'histogramme")
            return self._create_empty_figure()

        turbine_ids = list(result.detailed_results.keys())
        n_turbines = len(turbine_ids)

        n_cols = min(n_turbines, 3)
        n_rows = (n_turbines + n_cols - 1) // n_cols

        fig, axes = plt.subplots(
            n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows), sharex=True
        )

        # Gestion des axes pour différents layouts
        if n_turbines == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)

        # 1. Déterminer la vitesse max globale pour uniformiser les graphiques
        all_speeds = []
        for tid in turbine_ids:
            df = result.detailed_results[tid].get("chart_data")
            if df is not None and not df.empty:
                all_speeds.append(df["wind_speed"].max())

        max_wind = max(all_speeds) if all_speeds else 30
        bins = np.arange(0, max_wind + 0.5, 0.5)  # Bins de 0.5 m/s

        # 2. Tracer pour chaque turbine
        for idx, turbine_id in enumerate(turbine_ids):
            row, col = idx // n_cols, idx % n_cols
            ax = axes[row, col]

            chart_data = result.detailed_results[turbine_id].get("chart_data")

            if chart_data is None or chart_data.empty:
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                continue

            # Utilisation de histplot (plus adapté pour des bins réguliers et nombreux)
            sns.histplot(
                data=chart_data,
                x="wind_speed",
                bins=bins,
                ax=ax,
                color="#4393c3",
                edgecolor="white",
                alpha=0.8,
            )

            # Design & Labels
            ax.set_title(f"WTG {turbine_id}", fontsize=12, fontweight="bold")
            ax.set_xlabel("Wind Speed [m/s]", fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
            ax.grid(axis="y", linestyle="--", alpha=0.4)

            # Optionnel : Ajuster les ticks de l'axe X pour plus de lisibilité
            ax.xaxis.set_major_locator(
                plt.MultipleLocator(5)
            )  # Un gros tick tous les 5 m/s
            ax.xaxis.set_minor_locator(
                plt.MultipleLocator(1)
            )  # Un petit tick tous les 1 m/s

        # Supprimer les axes vides
        for idx in range(n_turbines, n_rows * n_cols):
            fig.delaxes(axes[idx // n_cols, idx % n_cols])

        fig.suptitle(
            "Wind Speed Distribution (0.5 m/s bins)", fontsize=14, fontweight="bold"
        )
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        return fig
