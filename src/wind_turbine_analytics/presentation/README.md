# Presentation Layer - README

## Vue d'ensemble

La couche de présentation gère l'affichage des résultats d'analyse dans différents formats. Elle implémente le pattern **Strategy** pour permettre différents rendus (console, HTML, PDF, etc.) sans modifier le code métier.

---

## Architecture

```
presentation/
├── presenter.py            # Classe de base abstraite
├── console_presenter.py    # Implémentation console
└── README.md              # Ce fichier
```

---

## Classes principales

### `PipelinePresenter` (Base)

Classe de base abstraite définissant l'interface pour tous les présentateurs.

**Méthodes :**
- `show_test_results(result)` : Affiche les résultats de tests d'une éolienne
- `show_test_park_summary(results)` : Affiche le résumé du parc
- `info(message)` : Affiche un message d'information
- `show_analysis_result(result, analysis_name)` : Affiche les résultats d'une analyse

### `ConsolePipelinePresenter`

Implémentation pour affichage console avec formatage structuré.

**Caractéristiques :**
- Formatage structuré avec séparateurs visuels
- Gestion automatique des DataFrames pandas
- Troncature intelligente pour grands tableaux (max 50 lignes)
- Affichage récursif de structures imbriquées (dict, list)
- Indentation automatique pour hiérarchie visuelle

---

## Utilisation

### 1. Avec les workflows

```python
from src.wind_turbine_analytics.presentation.console_presenter import (
    ConsolePipelinePresenter
)
from src.wind_turbine_analytics.application.workflows.scada_workflow import (
    ScadaWorkflow
)

# Créer le présentateur
presenter = ConsolePipelinePresenter()

# Créer et exécuter le workflow
workflow = ScadaWorkflow(config=config, presenter=presenter)
workflow.run()

# Les résultats sont automatiquement affichés pendant l'exécution
```

### 2. Affichage manuel de résultats

```python
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult
)

# Créer un résultat
result = AnalysisResult(
    status="SUCCESS",
    metadata={"turbine_id": "WTG01"},
    detailed_results={
        "total_hours": 120,
        "availability": 95.5
    }
)

# Afficher
presenter.show_analysis_result(result, "Mon Analyse")
```

---

## Format d'affichage

### Structure générale

```
====================================================================================================
Analysis: [Nom de l'analyse]
====================================================================================================
Status: [SUCCESS/FAIL/COMPLETE]
----------------------------------------------------------------------------------------------------

Metadata:
  clé1: valeur1
  clé2: valeur2
----------------------------------------------------------------------------------------------------

Detailed Results:

  résultat1:
    valeur ou tableau

  résultat2:
    [DataFrame ou structure imbriquée]
====================================================================================================
```

### Gestion des types de données

#### **Dictionnaires simples**
```python
{"total_hours": 120, "availability": 95.5}
```
Affichage :
```
total_hours: 120
availability: 95.5
```

#### **Dictionnaires imbriqués**
```python
{
    "summary": {
        "energy": 125000,
        "performance": 96.15
    }
}
```
Affichage :
```
summary:
  energy: 125000
  performance: 96.15
```

#### **Listes**
```python
{"monthly_data": [{"month": "2024-01", "value": 95.5}]}
```
Affichage :
```
monthly_data:
    month: 2024-01
    value: 95.5
```

#### **DataFrames pandas**
- Affichage tabulaire automatique
- Troncature à 50 lignes si > 50 rows
- Message indiquant le nombre total de lignes

```
availability_table:
  [Showing first 50 of 100 rows]
             timestamp  wind_speed  power
  0  2024-01-01 00:00:00         5.2   1200
  1  2024-01-01 00:10:00         6.1   1500
  ...
  ... (50 more rows)
```

---

## Résultats attendus par analyseur

### `ConsecutiveHoursAnalyzer`

```python
AnalysisResult(
    status="PASS/FAIL",
    metadata={
        "turbine_id": str,
        "test_start": datetime,
        "test_end": datetime
    },
    detailed_results={
        "consecutive_hours": float,
        "threshold": float,
        "criterion_met": bool
    }
)
```

### `EbACutInCutOutAnalyzer`

```python
AnalysisResult(
    status="COMPLETE",
    metadata={
        "turbine_id": str,
        "wind_speed_range": str
    },
    detailed_results={
        "total_real_energy": float,
        "total_theoretical_energy": float,
        "total_loss_energy": float,
        "performance": float,
        "monthly_performance": List[Dict]
    }
)
```

### `DataAvailabilityAnalyzer`

```python
AnalysisResult(
    status="COMPLETE",
    metadata={
        "turbine_id": str,
        "total_intervals": int
    },
    detailed_results={
        "availability_table": pd.DataFrame,
        "summary": {
            "wind_speed_availability_pct": float,
            "active_power_availability_pct": float,
            "wind_direction_availability_pct": float,
            "overall_availability_pct": float
        }
    }
)
```

---

## Extension : Créer un nouveau présentateur

Pour créer un nouveau type de présentateur (HTML, PDF, etc.) :

### 1. Hériter de `PipelinePresenter`

```python
from src.wind_turbine_analytics.presentation.presenter import PipelinePresenter

class HtmlPipelinePresenter(PipelinePresenter):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def show_analysis_result(self, result, analysis_name):
        # Générer HTML
        html_content = self._generate_html(result, analysis_name)
        
        # Sauvegarder
        output_path = self.output_dir / f"{analysis_name}.html"
        output_path.write_text(html_content, encoding="utf-8")
```

### 2. Implémenter toutes les méthodes

```python
def show_test_results(self, result):
    # Votre implémentation
    pass

def show_test_park_summary(self, results):
    # Votre implémentation
    pass

def info(self, message):
    # Votre implémentation
    pass
```

### 3. Utiliser dans les workflows

```python
presenter = HtmlPipelinePresenter(output_dir=Path("./reports"))
workflow = ScadaWorkflow(config=config, presenter=presenter)
workflow.run()
```

---

## Tests et exemples

### Tests unitaires

```bash
pytest tests/test_console_presenter.py -v
```

**Couverture :**
- ✅ Affichage de résultats simples
- ✅ Affichage de résultats complexes (avec DataFrames)
- ✅ Gestion de résultats None
- ✅ Troncature de grands DataFrames
- ✅ Affichage récursif de dictionnaires imbriqués

### Exemples d'utilisation

```bash
python tests/example_presenter_usage.py
```

**Exemples inclus :**
1. Résultat simple (heures consécutives)
2. Résultat EBA avec performance mensuelle
3. Résultat avec DataFrame (disponibilité)
4. Gestion d'erreur (résultat None)
5. Grand DataFrame (troncature)

---

## Bonnes pratiques

### ✅ À faire

- **Utiliser le présentateur dans les workflows** pour affichage automatique
- **Structurer les résultats** avec `AnalysisResult` pour cohérence
- **Utiliser les metadata** pour contexte (turbine_id, dates, etc.)
- **Grouper les données** dans `detailed_results` par type

### ❌ À éviter

- **Ne pas utiliser `print()` directement** dans les analyseurs
- **Ne pas mélanger** logique métier et présentation
- **Ne pas hardcoder** le format d'affichage dans les analyseurs
- **Ne pas oublier** de passer le présentateur au workflow

---

## Dépannage

### Problème : Les résultats ne s'affichent pas

**Cause :** Le présentateur n'est pas passé au workflow ou n'est pas appelé

**Solution :**
```python
# ✅ BON
workflow = ScadaWorkflow(config=config, presenter=presenter)

# ❌ MAUVAIS
workflow = ScadaWorkflow(config=config, presenter=None)
```

### Problème : DataFrame mal formaté en console

**Cause :** Largeur de console insuffisante

**Solution :**
- Augmenter la largeur de la console
- Les DataFrames utilisent `to_string()` qui s'adapte automatiquement

### Problème : Encodage Windows (emojis, caractères spéciaux)

**Solution :**
```python
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
```

---

## Historique des modifications

### 2026-04-26 : Ajout de `show_analysis_result()`

**Changements :**
- Nouvelle méthode `show_analysis_result()` dans `PipelinePresenter`
- Implémentation console dans `ConsolePipelinePresenter`
- Support des DataFrames pandas
- Troncature automatique pour grands tableaux
- Affichage récursif de structures imbriquées
- Tests unitaires et exemples complets

**Objectif :** Permettre l'affichage structuré et propre des résultats d'analyse dans les workflows SCADA et RunTest.

---

## Roadmap

### Court terme
- [ ] Créer `HtmlPipelinePresenter` pour rapports web
- [ ] Ajouter export CSV des DataFrames
- [ ] Support de graphiques inline (matplotlib to ASCII)

### Long terme
- [ ] `PdfPipelinePresenter` pour rapports professionnels
- [ ] Dashboard interactif (Streamlit ou Flask)
- [ ] Notifications par email des résultats

---

**Maintenu par** : gjacquet  
**Dernière mise à jour** : 2026-04-26
