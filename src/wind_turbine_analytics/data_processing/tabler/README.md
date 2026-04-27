# Système de Génération de Tableaux pour Rapports Word

Ce module fournit un système modulaire pour générer des tableaux dans des rapports Word à partir des résultats d'analyse.

## Architecture

Le système suit le **pattern Template Method** similaire à `BaseVisualizer`:

```
BaseTabler (classe abstraite)
    ├── ConsecutiveHoursTabler
    ├── CutInCutOutTabler
    ├── NominalPowerValuesTabler
    ├── NominalPowerDurationTabler
    ├── AutonomousOperationTabler
    ├── AvailabilityTabler
    └── RunTestSummaryTabler (agrégation)
```

## Utilisation

### 1. Intégration avec DataProcessingStep

```python
from src.wind_turbine_analytics.data_processing.data_processing import DataProcessingStep
from src.wind_turbine_analytics.data_processing.tabler.tables.runtest import ConsecutiveHoursTabler

# Un seul tabler
result = DataProcessingStep(
    analyzer=ConsecutiveHoursAnalyzer(),
    visualizer=ConseccutiveHoursVisualizer(),
    tabler=ConsecutiveHoursTabler()
).execute(turbine_farm, criteria)

# Plusieurs tablers pour un même analyseur
result = DataProcessingStep(
    analyzer=NominalPowerAnalyzer(),
    tabler=[NominalPowerValuesTabler(), NominalPowerDurationTabler()]
).execute(turbine_farm, criteria)
```

### 2. Génération du rapport Word

```python
from src.wind_turbine_analytics.presentation.word_presenter import WordPresenter

# Agréger les données de tableaux de tous les résultats
context = {}
for result in all_results:
    if result.metadata and 'table_data' in result.metadata:
        context.update(result.metadata['table_data'])

# Préparer les métadonnées
metadata = {
    "test_start": "01.02.2026 00:00:00",
    "test_end": "05.02.2026 23:50:00",
    "turbines": ["E1", "E6", "E8"]
}

# Générer le rapport
presenter = WordPresenter(
    template_path="./assets/templates/template_runtest.docx",
    output_path="./outputs/runtest_report.docx"
)
presenter.render_report(context, metadata=metadata)
```

### 3. Template Word

Le template Word doit contenir des balises docxtpl:

**Métadonnées:**
```
Date de génération: {{ generation_date }}
Période de test: {{ test_start }} à {{ test_end }}
Turbines analysées: {{ turbine_list }}
```

**Tableaux:**
```
{{ summary_table }}
{{ consecutive_hours_table }}
{{ cut_in_cut_out_table }}
{{ nominal_power_values_table }}
{{ nominal_power_duration_table }}
{{ autonomous_operation_table }}
{{ availability_table }}
```

## Créer un Nouveau Tabler

### Étape 1: Créer la classe

```python
from typing import Dict, Any, List
from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler

class MonNouveauTabler(BaseTabler):
    def __init__(self):
        super().__init__(table_name="mon_nouveau_table")
    
    def _get_table_headers(self) -> List[str]:
        """Définir les en-têtes de colonnes."""
        return ["WTG", "Valeur", "Status"]
    
    def _add_table_row(self, turbine_id: str, turbine_result: Dict[str, Any]) -> None:
        """Transformer les données de l'analyseur en ligne de tableau."""
        valeur = turbine_result.get("ma_valeur", 0.0)
        criterion_met = turbine_result.get("criterion_met", False)
        
        self._table_data.append({
            "wtg": turbine_id,
            "valeur": self._format_number(valeur, decimals=2, unit="kW"),
            "status": self._format_status_cell(criterion_met)
        })
```

### Étape 2: Utiliser les méthodes de formatage

**BaseTabler** fournit des utilitaires:

- `_format_status_cell(passed: bool)` → RichText avec couleur (vert/rouge)
- `_format_number(value: float, decimals: int, unit: str)` → Chaîne formatée

### Étape 3: Ajouter au workflow

```python
from mon_module import MonNouveauTabler

result = DataProcessingStep(
    analyzer=MonAnalyzer(),
    tabler=MonNouveauTabler()
).execute(context, criteria)
```

## Tableau Récapitulatif

`RunTestSummaryTabler` est spécial car il agrège les résultats de TOUS les analyseurs:

```python
summary_tabler = RunTestSummaryTabler()

# Accumuler les résultats de chaque analyseur
for analysis_name, result in all_results.items():
    summary_tabler.add_analysis_result(analysis_name, result)

# Générer le tableau récapitulatif
summary_data = summary_tabler.generate()
context.update(summary_data)
```

## Configuration YAML

Pour activer la génération Word, ajouter dans `config.yml`:

```yaml
render_template: true
template_path: "./assets/templates/template_runtest.docx"
output_path: "./outputs/runtest_report.docx"
```

## Structure des Données

Les tablers retournent un dict:

```python
{
    "table_name": [
        {
            "wtg": "E1",
            "data_hours": "119.83 h",
            "criterion_met": RichText("✓", color="00AA00", bold=True)
        },
        # ... autres lignes
    ],
    "table_name_raw": [
        # Données brutes pour debug
    ]
}
```

## Tests

```bash
# Test complet de génération Word
python tests/test_word_generation.py

# Tests unitaires
pytest tests/test_base_tabler.py
pytest tests/test_runtest_tablers.py
```

## Notes Techniques

- **docxtpl** : Bibliothèque de templating pour Word (Jinja2-like)
- **RichText** : Objet docxtpl pour formatage conditionnel (couleurs, gras, taille)
- **Pattern**: Template Method garantit l'uniformité des interfaces
- **Support multi-tables**: Un analyseur peut générer plusieurs tableaux

## Exemple Complet

Voir `src/wind_turbine_analytics/application/workflows/runtest_workflow.py` pour un exemple complet d'intégration.
