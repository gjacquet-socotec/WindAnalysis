import plotly.graph_objects as go
import plotly.express as px  # Nécessaire pour la palette de couleurs
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


class TreemapErrorCodeVisualizer(BaseVisualizer):
    def __init__(self):
        super().__init__(chart_name="error_code_treemap", use_plotly=True)

    def _create_figure(self, result: AnalysisResult) -> go.Figure:
        if not result.detailed_results:
            return self._create_empty_figure()

        ids, labels, parents, values, hovertext, colors = [], [], [], [], [], []

        # Palette de couleurs marquées (très contrastées)
        # On utilise une palette qualitative pour bien démarquer les systèmes
        palette = px.colors.qualitative.Bold
        system_color_map = {}
        color_index = 0

        # 1. Racine (Wind Farm)
        ids.append("Wind Farm")
        labels.append("<b>WIND FARM</b>")
        parents.append("")
        values.append(0)
        hovertext.append("Total fleet errors")
        colors.append("#f8f9fa")  # Couleur neutre pour le fond global

        for turbine_id, turbine_data in result.detailed_results.items():
            if "error" in turbine_data:
                continue

            summary = turbine_data.get("summary", {})
            total_turbine_errors = summary.get("total_error_events", 0)

            # 2. Niveau Turbine
            ids.append(turbine_id)
            labels.append(f"<b>Turbine {turbine_id}</b>")
            parents.append("Wind Farm")
            values.append(total_turbine_errors)
            hovertext.append(f"Total errors: {total_turbine_errors}")
            colors.append("white")

            codes = turbine_data.get("code_frequency", [])
            systems_in_turbine = {}
            for c in codes:
                sys_name = c.get("system", "unknown").capitalize()
                systems_in_turbine[sys_name] = (
                    systems_in_turbine.get(sys_name, 0) + c["count"]
                )

            # 3. Niveau Système
            for sys_name, sys_count in systems_in_turbine.items():
                sys_id = f"{turbine_id}_{sys_name}"

                # Assigner une couleur unique par système pour tout le graphique
                if sys_name not in system_color_map:
                    system_color_map[sys_name] = palette[color_index % len(palette)]
                    color_index += 1

                current_sys_color = system_color_map[sys_name]

                ids.append(sys_id)
                labels.append(f"<b>System: {sys_name}</b>")
                parents.append(turbine_id)
                values.append(sys_count)
                hovertext.append(
                    f"Turbine {turbine_id} - {sys_name}<br>Total: {sys_count}"
                )
                colors.append(current_sys_color)

                # 4. Niveau Code d'erreur
                for c in codes:
                    if c.get("system", "unknown").capitalize() == sys_name:
                        code_id = f"{sys_id}_{c['code']}"
                        ids.append(code_id)
                        labels.append(f"Code {c['code']}")
                        parents.append(sys_id)
                        values.append(c["count"])
                        # On garde la couleur du système pour grouper visuellement
                        colors.append(current_sys_color)

                        desc = c.get("description", "No description")[:100]
                        hovertext.append(
                            f"<b>Turbine:</b> {turbine_id}<br>"
                            f"<b>System:</b> {sys_name}<br>"
                            f"<b>Code:</b> {c['code']}<br>"
                            f"<b>Count:</b> {c['count']}<br>"
                            f"<b>Desc:</b> {desc}..."
                        )

        # Création de la figure
        fig = go.Figure(
            go.Treemap(
                ids=ids,
                labels=labels,
                parents=parents,
                values=values,
                hovertext=hovertext,
                hoverinfo="text",
                marker=dict(
                    colors=colors,
                    line=dict(
                        width=2, color="white"
                    ),  # Bordures blanches plus épaisses
                    pad=dict(
                        b=5, l=5, r=5, t=30
                    ),  # Plus d'espace pour le titre du bloc
                ),
                # template de texte optimisé
                texttemplate="<b>%{label}</b><br>%{value}",
                # CORRECTION ICI : 'middle center' au lieu de 'inside'
                textposition="middle center",
                branchvalues="remainder",
            )
        )

        fig.update_layout(
            title={
                "text": "<b>Error Distribution Analysis</b><br><sub>Size by frequency | Colored by System Type</sub>",
                "x": 0.5,
                "font": {"size": 24, "color": "#1a2a6c"},
            },
            width=1300,
            height=850,
            margin=dict(t=100, l=20, r=20, b=20),
            # Force la lisibilité du texte
            uniformtext=dict(minsize=12, mode="hide"),
            paper_bgcolor="white",
        )

        return fig

    def _create_empty_figure(self) -> go.Figure:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available", x=0.5, y=0.5, showarrow=False, font_size=20
        )
        return fig
