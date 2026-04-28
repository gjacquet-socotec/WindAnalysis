import plotly.graph_objects as go
from src.wind_turbine_analytics.data_processing.data_result_models import AnalysisResult
from src.wind_turbine_analytics.data_processing.visualizer.base_visualizer import (
    BaseVisualizer,
)
from src.logger_config import get_logger

logger = get_logger(__name__)


class TreemapErrorCodeVisualizer(BaseVisualizer):
    """
    Visualiseur Treemap pour la distribution des codes d'erreur.
    Hiérarchie : Turbine -> Système -> Code d'erreur
    La taille et la couleur dépendent du nombre d'occurrences.
    """

    def __init__(self):
        super().__init__(chart_name="error_code_treemap", use_plotly=True)

    def _create_figure(self, result: AnalysisResult) -> go.Figure:
        if not result.detailed_results:
            return self._create_empty_figure()

        # Listes pour construire la hiérarchie Plotly
        ids = []
        labels = []
        parents = []
        values = []
        hovertext = []

        # 1. Racine (Le parc complet)
        ids.append("Wind Farm")
        labels.append("<b>Wind Farm</b>")
        parents.append("")
        values.append(0)  # Sera calculé par la somme des enfants
        hovertext.append("Total fleet errors")

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

            # Organiser par système pour créer un niveau intermédiaire
            codes = turbine_data.get("code_frequency", [])
            systems_in_turbine = {}

            for c in codes:
                sys_name = c.get("system", "unknown").capitalize()
                if sys_name not in systems_in_turbine:
                    systems_in_turbine[sys_name] = 0
                systems_in_turbine[sys_name] += c["count"]

            # 3. Niveau Système
            for sys_name, sys_count in systems_in_turbine.items():
                sys_id = f"{turbine_id}_{sys_name}"
                ids.append(sys_id)
                labels.append(f"System: {sys_name}")
                parents.append(turbine_id)
                values.append(sys_count)
                hovertext.append(
                    f"Turbine {turbine_id} - {sys_name}<br>Total: {sys_count}"
                )

                # 4. Niveau Code d'erreur
                for c in codes:
                    if c.get("system", "unknown").capitalize() == sys_name:
                        code_id = f"{sys_id}_{c['code']}"
                        ids.append(code_id)
                        # Label court pour le rectangle
                        labels.append(f"Code {c['code']}")
                        parents.append(sys_id)
                        values.append(c["count"])

                        # Texte riche au survol
                        desc = c.get("description", "No description")[:100] + "..."
                        hovertext.append(
                            f"<b>Turbine:</b> {turbine_id}<br>"
                            f"<b>System:</b> {sys_name}<br>"
                            f"<b>Code:</b> {c['code']}<br>"
                            f"<b>Count:</b> {c['count']}<br>"
                            f"<b>Criticality:</b> {c.get('criticality', 'N/A')}<br>"
                            f"<b>Desc:</b> {desc}"
                        )

        # Création de la figure
        fig = go.Figure(
            go.Treemap(
                ids=ids,
                labels=labels,
                parents=parents,
                values=values,
                textinfo="label+value",
                hovertext=hovertext,
                hoverinfo="text",
                marker=dict(
                    colorscale="YlOrRd",  # Jaune -> Orange -> Rouge
                    colors=values,  # Intensité de la couleur selon le nombre
                    showscale=True,
                    colorbar=dict(title="Occurrences"),
                ),
                branchvalues="remainder",  # Permet de mieux gérer les tailles relatives
            )
        )

        fig.update_layout(
            title={
                "text": "Error Distribution Treemap<br><sub>Hierarchy: Turbine > System > Error Code (Size & Color by Frequency)</sub>",
                "x": 0.5,
                "font": {"size": 20},
            },
            width=1200,
            height=800,
            margin=dict(t=100, l=10, r=10, b=10),
        )

        return fig

    def _create_empty_figure(self) -> go.Figure:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for Treemap",
            x=0.5,
            y=0.5,
            showarrow=False,
            font_size=20,
        )
        return fig
