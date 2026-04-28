from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
import plotly.graph_objects as go
import pandas as pd
from src.logger_config import get_logger
from typing import Dict, List, Tuple

logger = get_logger(__name__)


class DataAvailabilityVisualizer(BaseVisualizer):
    """
    Visualiseur pour la disponibilité des données SCADA.

    Génère un graphique à barres horizontales empilées avec:
    - Axe X: Temps (périodes horaires)
    - Axe Y: Variables par turbine (wind_speed, active_power, pitch, etc.)
    - Couleurs: Vert (≥95%), Jaune (30-95%), Rouge (<30%)
    - Format type Gantt chart pour voir la disponibilité temporelle
    """

    def __init__(self):
        super().__init__(chart_name="data_availability", use_plotly=True)

    def _calculate_optimal_tickformat(self, timestamps: pd.Series) -> dict:
        """
        Determine optimal X-axis formatting based on data time span.

        Args:
            timestamps: All timestamps in the availability data

        Returns:
            Dict with xaxis configuration parameters
        """
        if len(timestamps) == 0:
            return {}

        time_span = (timestamps.max() - timestamps.min()).total_seconds() / 86400.0

        if time_span <= 7:
            return {
                "tickformat": "%d/%m %H:%M",
                "dtick": 3600000 * 6,
                "tickangle": -45,
            }
        elif time_span <= 60:
            return {
                "tickformat": "%d %b",
                "dtick": 86400000 * 3,
                "tickangle": 0,
            }
        else:
            return {
                "tickformat": "%b %Y",
                "dtick": "M1",
                "tickangle": 0,
            }

    def _create_figure(self, result: AnalysisResult) -> go.Figure:
        """
        Crée un graphique de disponibilité des données SCADA.

        Args:
            result: Résultat de l'analyse contenant availability_table pour
                    chaque turbine

        Returns:
            Figure Plotly avec barres horizontales par variable/turbine
        """
        # Récupérer les résultats par turbine
        turbine_results = result.detailed_results

        # Trier les turbines par ordre alphabétique
        turbine_ids = sorted(turbine_results.keys())

        # Préparer les données pour le graphique
        y_labels = []  # Labels pour l'axe Y
        traces = []

        # Variables à afficher (ordre d'affichage)
        variables = [
            "wind_speed",
            "active_power",
            "wind_direction",
            "temperature",
        ]

        variable_display_names = {
            "wind_speed": "ws",
            "active_power": "power",
            "wind_direction": "dir",
            "temperature": "temp",
        }

        # Pour chaque turbine (de bas en haut)
        for turbine_id in reversed(turbine_ids):
            turbine_result = turbine_results[turbine_id]

            if "error" in turbine_result:
                logger.warning(
                    f"Skipping {turbine_id}: {turbine_result['error']}"
                )
                continue

            availability_df = turbine_result["availability_table"]

            # Pour chaque variable de cette turbine
            for var in variables:
                if var not in availability_df.columns:
                    continue

                # Label pour cette ligne (ex: "ws_12" pour wind_speed E12)
                short_name = variable_display_names.get(var, var)
                y_label = f"{short_name}_{turbine_id}"
                y_labels.append(y_label)

                # Créer les barres pour cette variable
                self._add_availability_bars(
                    traces,
                    availability_df,
                    var,
                    y_label,
                    turbine_id,
                )

        # Créer la figure
        fig = go.Figure(data=traces)

        # Mise en forme
        fig.update_layout(
            title={
                "text": (
                    "SCADA Data Availability - Operational Parameters<br>"
                    "<sub>Availability computed as proportion of valid "
                    "1-hour data points</sub>"
                ),
                "x": 0.5,
                "xanchor": "center",
            },
            xaxis_title="Time",
            yaxis_title="SCADA parameters",
            barmode="overlay",
            height=max(600, len(y_labels) * 25),
            showlegend=True,
            legend=dict(
                title="SCADA data availability",
                orientation="h",
                yanchor="top",
                y=1.08,
                xanchor="right",
                x=1,
            ),
            yaxis=dict(
                categoryorder="array",
                categoryarray=y_labels,
            ),
            xaxis=dict(
                title="Time",
                type="date",
                showgrid=True,
                gridcolor="lightgray",
                **self._calculate_optimal_tickformat(
                    pd.concat([
                        turbine_results[tid]["availability_table"]["timestamp"]
                        for tid in turbine_ids
                        if "availability_table" in turbine_results[tid]
                    ]) if any(
                        "availability_table" in turbine_results[tid]
                        for tid in turbine_ids
                    ) else pd.Series(dtype='datetime64[ns]')
                ),
            ),
            plot_bgcolor="white",
        )

        return fig

    def _add_availability_bars(
        self,
        traces: list,
        availability_df: pd.DataFrame,
        variable: str,
        y_label: str,
        turbine_id: str,
    ):
        """
        Ajoute les barres de disponibilité pour une variable donnée.

        Crée des segments colorés selon la disponibilité:
        - Vert: donnée disponible (1)
        - Jaune/Orange: donnée partiellement disponible (si on agrège)
        - Rouge/Blanc: donnée indisponible (0)

        Args:
            traces: Liste des traces Plotly
            availability_df: DataFrame avec timestamp et disponibilité
            variable: Nom de la variable (ex: 'wind_speed')
            y_label: Label pour l'axe Y (ex: 'ws_E1')
            turbine_id: ID de la turbine
        """
        # Récupérer les timestamps et valeurs
        timestamps = pd.to_datetime(availability_df["timestamp"])
        values = availability_df[variable].values

        # Grouper les segments consécutifs de même valeur
        segments = self._group_consecutive_segments(timestamps, values)

        # Créer les barres pour chaque segment
        for segment_start, segment_end, segment_value in segments:
            # Déterminer la couleur selon la valeur
            if segment_value == 1:
                color = "#2ca02c"  # Vert (Good >95%)
                legend_group = "good"
                legend_name = "Good (>95%)"
            elif segment_value == 0:
                color = "#FFA500"  # Orange (Unavailable)
                legend_group = "unavailable"
                legend_name = "Unavailable (0%)"
                # Ne pas faire continue - tracer la barre
            else:
                # Valeurs intermédiaires (si on a des valeurs partielles)
                color = "#ff7f0e"  # Orange (Partial 30-95%)
                legend_group = "partial"
                legend_name = "Partial (30-95%)"

            # Ajouter la trace (une barre horizontale)
            # Vérifier si la légende pour ce groupe existe déjà
            show_legend = not any(
                getattr(trace, "legendgroup", None) == legend_group
                for trace in traces
            )

            # Calculer la durée en heures (pour sérialisation JSON)
            duration = (segment_end - segment_start).total_seconds() / 3600.0

            # Mapper le statut pour clarté
            status_text = {
                1: "Available (100%)",
                0: "Unavailable (0%)",
            }.get(segment_value, f"Partial ({segment_value*100:.0f}%)")

            traces.append(
                go.Bar(
                    x=[duration],
                    y=[y_label],
                    orientation="h",
                    marker=dict(color=color),
                    base=segment_start,
                    legendgroup=legend_group,
                    name=legend_name,
                    showlegend=show_legend,
                    hovertemplate=(
                        f"<b>{turbine_id} - {variable}</b><br>"
                        f"Start: {segment_start.strftime('%Y-%m-%d %H:%M')}<br>"
                        f"End: {segment_end.strftime('%Y-%m-%d %H:%M')}<br>"
                        f"Duration: {duration:.1f}h<br>"
                        f"Status: {status_text}"
                        "<extra></extra>"
                    ),
                )
            )

    def _group_consecutive_segments(
        self, timestamps: pd.Series, values: pd.Series
    ) -> List[Tuple[pd.Timestamp, pd.Timestamp, int]]:
        """
        Groupe les valeurs consécutives identiques en segments.

        Args:
            timestamps: Série ou Index des timestamps
            values: Série des valeurs (0 ou 1)

        Returns:
            Liste de tuples (start_time, end_time, value)
        """
        segments = []
        if len(timestamps) == 0:
            return segments

        # Convertir en liste pour un accès uniforme
        if isinstance(timestamps, pd.DatetimeIndex):
            timestamps = timestamps.to_series().reset_index(drop=True)

        current_start = timestamps.iloc[0]
        current_value = values[0]

        for i in range(1, len(timestamps)):
            if values[i] != current_value:
                # Fin du segment courant
                segments.append(
                    (current_start, timestamps.iloc[i - 1], current_value)
                )
                # Début d'un nouveau segment
                current_start = timestamps.iloc[i]
                current_value = values[i]

        # Ajouter le dernier segment
        segments.append((current_start, timestamps.iloc[-1], current_value))

        return segments