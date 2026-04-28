# EbaCutInCutOutVisualizer - Documentation

## 📊 Vue d'ensemble

Le `EbaCutInCutOutVisualizer` est un visualiseur spécialisé pour afficher la **disponibilité énergétique** (EBA - Energy Based Availability) d'éoliennes sur une période donnée.

## 🎯 Objectif

Générer un graphique interactif montrant :
- **Évolution mensuelle** : Courbes de rendement énergétique pour chaque turbine
- **Moyenne du parc** : Ligne pointillée noire montrant la performance globale
- **Vue unifiée** : Toutes les turbines sur le même graphique pour comparaison facile
- **Échelle 0-100%** : Axe Y fixé entre 50% et 105% pour visualisation optimale

## 📈 Format de sortie

Le visualiseur génère deux fichiers :

1. **PNG** (1200×800 px) : Image statique pour rapports Word/PDF
2. **JSON** : Format Plotly interactif pour dashboard web futur

## 🔧 Utilisation

### Import

```python
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders import (
    EbaCutInCutOutVisualizer,
)
```

### Exemple basique

```python
# Après avoir exécuté l'analyseur EBA
from src.wind_turbine_analytics.data_processing.analyzer.logics import (
    EbACutInCutOutAnalyzer,
)

# 1. Analyser
analyzer = EbACutInCutOutAnalyzer()
results = analyzer.analyze(turbine_farm, criteria)

# 2. Visualiser
visualizer = EbaCutInCutOutVisualizer()
output_paths = visualizer.generate(results)

print(f"PNG: {output_paths['png_path']}")
print(f"JSON: {output_paths['json_path']}")
```

## 📊 Structure des données attendues

Le visualiseur attend un `AnalysisResult` avec cette structure :

```python
AnalysisResult(
    detailed_results={
        "WTG01": {
            "performance": 93.75,  # Performance globale en %
            "total_real_energy": 150000.0,  # kWh
            "total_theoretical_energy": 160000.0,  # kWh
            "monthly_performance": [
                {"month": "2024-01", "performance": 92.5},
                {"month": "2024-02", "performance": 94.2},
                {"month": "2024-03", "performance": 93.8},
                # ... autres mois
            ]
        },
        "WTG02": {
            # ... données turbine 2
        }
    },
    status="completed",
    requires_visuals=True
)
```

## 🎨 Caractéristiques visuelles

### Palette de couleurs

Chaque turbine a sa propre couleur :
- 🔵 Bleu : Turbine 1
- 🟠 Orange : Turbine 2  
- 🟢 Vert : Turbine 3
- 🔴 Rouge : Turbine 4
- 🟣 Violet : Turbine 5
- 🟤 Marron : Turbine 6
- ⚫ Noir (pointillés) : Moyenne du parc éolien

### Style

- **Lignes + marqueurs** : Chaque point mensuel est visible
- **Ligne épaisse** : 2.5px pour la moyenne, 2px pour les turbines
- **Hover unifié** : Au survol d'un mois, toutes les valeurs s'affichent

### Axes

- **X** : Périodes mensuelles (format YYYY-MM), rotation -45°
- **Y** : Performance (%), plage fixe 50-105%, suffix "%"

## 📁 Fichiers de sortie

### PNG
- **Chemin** : `output/charts/eba_cut_in_cut_out_chart.png`
- **Résolution** : 1200×800 px
- **Format** : 24-bit RGB
- **Taille typique** : 50-100 KB

### JSON
- **Chemin** : `output/charts/eba_cut_in_cut_out_chart.json`
- **Format** : Plotly JSON schema
- **Utilisation** : Chargement dans dashboard web via `plotly.js`
- **Taille typique** : 5-15 KB

## 🔗 Intégration avec les workflows

### Workflow SCADA

```python
from src.wind_turbine_analytics.application.workflows import ScadaWorkflow

workflow = ScadaWorkflow(config)
workflow.add_visualizer(EbaCutInCutOutVisualizer())
workflow.run()
```

### Workflow RunTest

```python
from src.wind_turbine_analytics.application.workflows import RunTestWorkflow

workflow = RunTestWorkflow(config)
# EBA visualizer peut être ajouté si critère EBA présent
if "cut_in_to_cut_out" in criteria:
    workflow.add_visualizer(EbaCutInCutOutVisualizer())
workflow.run()
```

## 🧪 Tests

### Tests unitaires

```bash
pytest tests/test_eba_cut_in_cut_out_visualizer.py -v
```

### Exemple avec données réelles

```bash
python tests/example_eba_visualizer.py
```

## 📊 Exemple de résultat

Sur la turbine **LU09** (période avril-décembre 2024) :

- **Performance globale** : 79.64%
- **Meilleur mois** : Septembre 2024 (82.99%)
- **Moins bon mois** : Novembre 2024 (74.69%)
- **Énergie réelle** : 4,134 MWh
- **Énergie théorique** : 5,191 MWh

## ⚠️ Notes importantes

1. **Périodes courtes** : Si moins de 3 mois de données, le graphique peut manquer de lisibilité
2. **Données manquantes** : Les mois sans données ne sont pas affichés
3. **Performance > 100%** : Possible si la turbine sur-performe (rare mais normal)
4. **Échelle fixe** : L'axe Y est fixé 75-105% pour comparabilité entre turbines

## 🔍 Dépannage

### Erreur : "No data available for EBA analysis"

**Cause** : Pas de données dans `monthly_performance`

**Solution** : Vérifier que l'analyseur EBA a retourné des résultats valides

### Erreur : "KeyError: 'month'"

**Cause** : Structure de données incorrecte

**Solution** : Vérifier que `monthly_performance` contient bien les clés `month` et `performance`

### Graphique vide

**Cause** : Toutes les turbines ont des erreurs

**Solution** : Vérifier les logs de l'analyseur pour identifier les problèmes en amont

## 📚 Références

- [BaseVisualizer](../src/wind_turbine_analytics/data_processing/visualizer/base_visualizer.py)
- [EbACutInCutOutAnalyzer](../src/wind_turbine_analytics/data_processing/analyzer/logics/eba_cut_in_cut_out_analyzer.py)
- [Plotly Documentation](https://plotly.com/python/)

---

**Dernière mise à jour** : 2026-04-28  
**Version** : 1.0.0
