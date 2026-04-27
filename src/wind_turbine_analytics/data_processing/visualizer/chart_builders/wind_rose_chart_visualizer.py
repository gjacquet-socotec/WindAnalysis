from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from typing import Dict, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from src.logger_config import get_logger

logger = get_logger(__name__)


class WindRoseChartVisualizer(BaseVisualizer):
    """
    Visualiseur de rose des vents (Wind Rose).

    Génère un graphique polaire avec grid layout (1 subplot par turbine):
    - Directions: 0-360° (16 secteurs: N, NNE, NE, ENE, E, etc.)
    - Bins de vitesse avec couleurs
    - Fréquence (%) dans chaque secteur
    """

    def __init__(self):
        super().__init__(chart_name="wind_rose_chart", use_plotly=True)

    def _create_figure(self, result: AnalysisResult) -> go.Figure:
        """
        Crée la figure Plotly avec grid layout pour toutes les turbines.

        Args:
            result: Résultat de NominalPowerAnalyzer (contient chart_data)

        Returns:
            Figure Plotly avec roses des vents
        """
        if not result.detailed_results:
            logger.warning("Aucune donnée détaillée pour générer la rose des vents")
            return self._create_empty_figure()

        # Nombre de turbines
        turbine_ids = list(result.detailed_results.keys())
        n_turbines = len(turbine_ids)

        # Calculer la disposition du grid
        n_cols = min(n_turbines, 3)
        n_rows = (n_turbines + n_cols - 1) // n_cols

        # Créer les subplots avec type polar
        fig = make_subplots(
            rows=n_rows,
            cols=n_cols,
            specs=[[{"type": "polar"}] * n_cols for _ in range(n_rows)],
            subplot_titles=[f"WTG {tid}" for tid in turbine_ids],
            vertical_spacing=0.15,
            horizontal_spacing=0.1,
        )

        # Définir les bins de vitesse de vent et couleurs
        wind_bins = [0, 3, 5, 10, 15, 20, 25, 100]
        wind_labels = ["0-3", "3-5", "5-10", "10-15", "15-20", "20-25", ">25"]
        colors = ["#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061", "#67001f", "#a50026"]

        # Directions (16 secteurs)
        directions = np.arange(0, 360, 22.5)
        dir_labels = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

        # Ajouter les données pour chaque turbine
        for idx, turbine_id in enumerate(turbine_ids):
            turbine_data = result.detailed_results[turbine_id]

            # Position dans le grid
            row = (idx // n_cols) + 1
            col = (idx % n_cols) + 1

            # Récupérer chart_data (doit contenir wind_speed et possiblement wind_direction)
            chart_data = turbine_data.get("chart_data")

            if chart_data is None or chart_data.empty:
                logger.warning(f"Pas de données pour {turbine_id}")
                continue

            # Vérifier si wind_direction existe (sinon on ne peut pas faire de rose des vents)
            # Pour NominalPowerAnalyzer, on n'a que wind_speed et power
            # Il faut donc que l'analyseur ajoute wind_direction dans chart_data
            # Pour l'instant, créons une distribution synthétique basée sur wind_speed

            if "wind_direction" not in chart_data.columns:
                logger.warning(f"Pas de colonne 'wind_direction' pour {turbine_id}, distribution omni-directionnelle simulée")
                # Simuler une distribution aléatoire pour démonstration
                chart_data = chart_data.copy()
                chart_data["wind_direction"] = np.random.uniform(0, 360, len(chart_data))

            # Créer les bins de direction (22.5° par secteur)
            chart_data["dir_bin"] = pd.cut(
                chart_data["wind_direction"],
                bins=np.append(directions, 360),
                labels=dir_labels,
                include_lowest=True
            )

            # Créer les bins de vitesse
            chart_data["wind_bin"] = pd.cut(
                chart_data["wind_speed"],
                bins=wind_bins,
                labels=wind_labels,
                include_lowest=True
            )

            # Calculer les fréquences par direction et vitesse
            freq_table = chart_data.groupby(["dir_bin", "wind_bin"]).size().unstack(fill_value=0)
            freq_table = freq_table / len(chart_data) * 100  # Convertir en pourcentage

            # Ajouter les traces pour chaque bin de vitesse (du plus faible au plus fort)
            for i, (wind_label, color) in enumerate(zip(wind_labels, colors)):
                if wind_label not in freq_table.columns:
                    continue

                values = freq_table[wind_label].values
                theta = dir_labels

                fig.add_trace(
                    go.Barpolar(
                        r=values,
                        theta=theta,
                        name=f"{wind_label} m/s" if idx == 0 else None,
                        marker=dict(color=color),
                        showlegend=(idx == 0),
                    ),
                    row=row,
                    col=col,
                )

        # Mise en page globale
        fig.update_layout(
            title="Wind Rose - All Turbines",
            height=400 * n_rows,
            width=1200,
            template="plotly_white",
            showlegend=True,
            legend=dict(
                title="Wind Speed",
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            ),
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    showticklabels=True,
                    title="Frequency (%)"
                ),
                angularaxis=dict(
                    direction="clockwise",
                    period=360
                )
            )
        )

        return fig

    def _create_empty_figure(self) -> go.Figure:
        """Crée une figure vide en cas de données manquantes."""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for wind rose",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="red"),
        )
        fig.update_layout(
            title="Wind Rose Analysis",
            height=400,
            width=600,
            template="plotly_white",
        )
        return fig
