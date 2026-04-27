from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class CutInCutoutTimelineVisualizer(BaseVisualizer):
    """
    Visualiseur de timeline Cut-in/Cut-out.

    Génère une timeline (Gantt chart) montrant:
    - Périodes RUN (vert): turbine en fonctionnement
    - Périodes STOP (rouge): turbine à l'arrêt
    - Annotations avec codes d'alarme sur les périodes STOP
    - Une ligne par turbine (empilées verticalement)

    Utilise les données de TestCutInCutOutAnalyzer.all_periods
    """

    def __init__(self):
        super().__init__(chart_name="cutin_cutout_timeline_chart", use_plotly=True)

    def _create_figure(self, result: AnalysisResult) -> go.Figure:
        """
        Crée la figure Plotly avec timeline pour toutes les turbines.

        Args:
            result: Résultat de TestCutInCutOutAnalyzer (contient all_periods)

        Returns:
            Figure Plotly avec timeline Gantt
        """
        if not result.detailed_results:
            logger.warning("Aucune donnée détaillée pour générer la timeline")
            return self._create_empty_figure()

        # Préparer les données pour le Gantt chart
        timeline_data = []

        for turbine_id, turbine_data in result.detailed_results.items():
            all_periods = turbine_data.get("all_periods", [])

            if not all_periods:
                logger.warning(f"Pas de périodes pour {turbine_id}")
                continue

            # Ajouter chaque période à la timeline
            for period in all_periods:
                is_available = period.get("is_available", False)
                start = period.get("start")
                end = period.get("end")
                alarm_codes = period.get("alarm_codes", [])

                if start is None or end is None:
                    continue

                # Formater les codes d'alarme
                alarm_text = ", ".join(alarm_codes) if alarm_codes else "No alarms"

                # Statut
                status = "RUN" if is_available else "STOP"
                color = "#43a047" if is_available else "#d32f2f"

                timeline_data.append({
                    "Task": f"{turbine_id}",
                    "Start": start,
                    "Finish": end,
                    "Status": status,
                    "Color": color,
                    "Alarm_Codes": alarm_text,
                })

        if not timeline_data:
            logger.warning("Aucune période valide trouvée")
            return self._create_empty_figure()

        # Créer le DataFrame
        df = pd.DataFrame(timeline_data)

        # Créer la figure avec Plotly (Gantt chart)
        fig = go.Figure()

        # Ajouter les traces par turbine et statut
        for turbine_id in df["Task"].unique():
            df_turbine = df[df["Task"] == turbine_id]

            for idx, row in df_turbine.iterrows():
                # Calculer la durée en secondes (pour éviter les Timedelta non sérialisables)
                duration_seconds = (row["Finish"] - row["Start"]).total_seconds()

                # Formater les dates pour l'hover
                start_str = row["Start"].strftime("%Y-%m-%d %H:%M") if hasattr(row["Start"], "strftime") else str(row["Start"])
                end_str = row["Finish"].strftime("%Y-%m-%d %H:%M") if hasattr(row["Finish"], "strftime") else str(row["Finish"])

                # Ajouter une barre pour cette période
                fig.add_trace(
                    go.Bar(
                        x=[duration_seconds / 3600],  # Convertir en heures pour l'affichage
                        y=[row["Task"]],
                        base=row["Start"],
                        orientation="h",
                        marker=dict(color=row["Color"]),
                        name=row["Status"],
                        showlegend=False,
                        hovertemplate=(
                            f"<b>{row['Task']}</b><br>"
                            f"Status: {row['Status']}<br>"
                            f"Start: {start_str}<br>"
                            f"End: {end_str}<br>"
                            f"Duration: {duration_seconds/3600:.2f}h<br>"
                            f"Alarm Codes: {row['Alarm_Codes']}<br>"
                            "<extra></extra>"
                        ),
                    )
                )

        # Ajouter une légende manuelle
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color="#43a047"),
                name="RUN (Available)",
                showlegend=True,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color="#d32f2f"),
                name="STOP (Unavailable)",
                showlegend=True,
            )
        )

        # Mise en page
        fig.update_layout(
            title="Cut-In/Cut-Out Timeline - All Turbines",
            xaxis=dict(
                title="Time",
                type="date",
                showgrid=True,
            ),
            yaxis=dict(
                title="Turbine",
                categoryorder="category ascending",
                showgrid=True,
            ),
            height=max(400, len(df["Task"].unique()) * 80),
            width=1200,
            template="plotly_white",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="closest",
        )

        return fig

    def _create_empty_figure(self) -> go.Figure:
        """Crée une figure vide en cas de données manquantes."""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for timeline",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="red"),
        )
        fig.update_layout(
            title="Cut-In/Cut-Out Timeline",
            height=400,
            width=800,
            template="plotly_white",
        )
        return fig
