from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler


class CutInCutOutTabler(BaseTabler):
    """
    Tableau pour le critère cut-in à cut-out.

    Format: | WTG | Status | Duration [h] | Start running | Stop running | Alarm codes | Criterion (>=72h) |

    Affiche toutes les périodes (disponibles et indisponibles) par turbine,
    triées par ordre chronologique.
    """

    def __init__(self):
        super().__init__(table_name="cut_in_cut_out_table")

    def _get_table_headers(self) -> List[str]:
        """Retourne les en-têtes du tableau."""
        return [
            "WTG",
            "Status",
            "Duration [h]",
            "Start running",
            "Stop running",
            "Alarm codes",
            "Criterion (>=72h)",
        ]

    def _add_table_row(
        self, turbine_id: str, turbine_result: Dict[str, Any]
    ) -> None:
        """
        Ajoute plusieurs lignes pour une turbine (une par période).

        Args:
            turbine_id: ID de la turbine
            turbine_result: Résultats contenant 'all_periods', 'required_hours'
        """
        all_periods = turbine_result.get("all_periods", [])
        required_hours = turbine_result.get("required_hours", 72)

        if not all_periods:
            # Aucune période trouvée
            self._table_data.append(
                {
                    "wtg": turbine_id,
                    "status": "N/A",
                    "duration": "0 h",
                    "start_running": "N/A",
                    "stop_running": "N/A",
                    "alarm_codes": "N/A",
                    "criterion_met": self._format_status_cell(False),
                }
            )
            return

        # Ajouter une ligne par période
        for idx, period in enumerate(all_periods):
            is_available = period.get("is_available", False)
            duration = period.get("net_duration_hours", 0.0)
            start = period.get("start", "N/A")
            end = period.get("end", "N/A")
            alarm_codes = period.get("alarm_codes", [])

            # Formater les dates
            if hasattr(start, "strftime"):
                start = start.strftime("%Y-%m-%d %H:%M")
            if hasattr(end, "strftime"):
                end = end.strftime("%Y-%m-%d %H:%M")

            # Formater les codes d'alarme
            alarm_codes_str = ", ".join(alarm_codes) if alarm_codes else "None"

            # Status
            status = "✓ RUN" if is_available else "✗ STOP"

            # Critère (seulement pour les périodes disponibles)
            if is_available:
                criterion_met = duration >= required_hours
                criterion_str = self._format_status_cell(criterion_met)
            else:
                criterion_str = "-"

            # WTG name: première ligne = nom complet, autres = "-"
            wtg_display = turbine_id if idx == 0 else "-"

            self._table_data.append(
                {
                    "wtg": wtg_display,
                    "status": status,
                    "duration": self._format_number(duration, decimals=2, unit="h"),
                    "start_running": start,
                    "stop_running": end,
                    "alarm_codes": alarm_codes_str,
                    "criterion_met": criterion_str,
                }
            )
