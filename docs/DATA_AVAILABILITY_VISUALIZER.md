# DataAvailabilityVisualizer

Documentation du visualiseur de disponibilité des données SCADA.

---

## 📋 Vue d'ensemble

Le `DataAvailabilityVisualizer` génère un graphique à barres horizontales empilées montrant la disponibilité temporelle des données SCADA pour chaque turbine et chaque variable.

**Type de graphique** : Barres horizontales type Gantt chart  
**Format de sortie** : PNG + JSON (Plotly)  
**Utilisation** : Diagnostic de qualité des données SCADA

---

## 🎨 Format du graphique

### Structure

```
Axe Y (vertical) : Variables par turbine
    ├── temp_E12    ──────────────────────────────  (Température turbine E12)
    ├── dir_E12     ──────────────────────────────  (Direction vent E12)
    ├── power_E12   ──────────────────────────────  (Puissance active E12)
    ├── ws_E12      ──────────────────────────────  (Vitesse vent E12)
    ├── temp_E11    ──────────────────────────────  (Température turbine E11)
    └── ...

Axe X (horizontal) : Temps (périodes horaires)
    └── 2024-09-01 00:00 ─→ 2024-09-04 00:00
```

### Code couleur

| Couleur | Signification | Valeur |
|---------|--------------|--------|
| 🟢 Vert (`#2ca02c`) | Données disponibles | `1` (100%) |
| 🟠 Orange (`#FFA500`) | Données indisponibles | `0` (0%) |
| 🟠 Orange (`#ff7f0e`) | Partiellement disponible | Entre 0 et 1 |

### Légende

- **Good (>95%)** : Données complètement disponibles sur la période
- **Partial (30-95%)** : Données partiellement disponibles (si implémenté)

---

## 🔧 Utilisation

### Exemple basique

```python
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.data_availability_visualizer import (
    DataAvailabilityVisualizer,
)
from src.wind_turbine_analytics.data_processing.data_result_models import (
    AnalysisResult,
)

# Préparer le résultat d'analyse
result = AnalysisResult(
    detailed_results={
        "E1": {
            "availability_table": availability_df_e1,  # DataFrame avec timestamp + variables
            "summary": {"overall_availability_pct": 95.5},
        },
        "E2": {
            "availability_table": availability_df_e2,
            "summary": {"overall_availability_pct": 88.2},
        },
    },
    status="completed",
    requires_visuals=True,
)

# Configurer les métadonnées
result.metadata = {
    "output_dir": "./output",
    "charts": {},
}

# Générer le graphique
visualizer = DataAvailabilityVisualizer()
output_paths = visualizer.generate(result)

print(f"PNG: {output_paths['png_path']}")
print(f"JSON: {output_paths['json_path']}")
```

### Format du DataFrame d'entrée

Le `availability_table` pour chaque turbine doit contenir :

```python
availability_df = pd.DataFrame({
    "timestamp": [datetime_1, datetime_2, ...],  # Timestamps horaires
    "wind_speed": [1, 1, 0, 1, ...],             # 0 ou 1
    "active_power": [1, 0, 1, 1, ...],           # 0 ou 1
    "wind_direction": [1, 1, 1, 1, ...],         # 0 ou 1
    "temperature": [1, 1, 1, 1, ...],            # 0 ou 1 (optionnel)
    "overall": [1, 0, 0, 1, ...],                # 0 ou 1 (ET logique)
})
```

**Variables obligatoires** :
- `wind_speed`
- `active_power`
- `wind_direction`

**Variables optionnelles** :
- `temperature`
- Autres variables SCADA

---

## 📊 Algorithme de visualisation

### 1. Préparation des données

```python
# Pour chaque turbine
for turbine_id in sorted(turbine_results.keys()):
    # Pour chaque variable (ws, power, dir, temp)
    for variable in variables:
        # Créer un label Y (ex: "ws_E1")
        y_label = f"{short_name}_{turbine_id}"
```

### 2. Groupement de segments

Le visualiseur groupe les valeurs consécutives identiques en segments :

```python
# Exemple :
timestamps = [00:00, 01:00, 02:00, 03:00, 04:00, 05:00]
values     = [  1,     1,     0,     0,     1,     1  ]

# Résultat :
segments = [
    (00:00, 01:00, 1),  # Segment disponible
    (02:00, 03:00, 0),  # Segment indisponible
    (04:00, 05:00, 1),  # Segment disponible
]
```

### 3. Création des barres

Pour chaque segment :

```python
if segment_value == 1:
    # Créer une barre verte
    color = "#2ca02c"
    duration = (segment_end - segment_start).total_seconds() / 3600
    
    trace = go.Bar(
        x=[duration],          # Largeur de la barre (en heures)
        y=[y_label],           # Position verticale
        orientation="h",       # Horizontale
        marker=dict(color=color),
        base=segment_start,    # Position de début sur l'axe X
    )
elif segment_value == 0:
    # Ne pas tracer (affiche un gap blanc)
    continue
```

### 4. Mise en forme

```python
fig.update_layout(
    barmode="overlay",               # Superposer les barres
    yaxis=dict(
        categoryorder="array",       # Ordre personnalisé
        categoryarray=y_labels,      # De bas en haut
    ),
    height=max(600, n_vars * 25),   # Hauteur dynamique
)
```

---

## 📅 Formatage de l'axe X

L'axe temporel s'adapte automatiquement à la durée de la période analysée :

| Durée | Format | Exemple | Intervalle |
|-------|--------|---------|-----------|
| ≤ 7 jours | `%d/%m %H:%M` | "01/09 14:00" | 6 heures |
| 8-60 jours | `%d %b` | "15 Sep" | 3 jours |
| > 60 jours | `%b %Y` | "Sep 2024" | 1 mois |

**Avantages** :
- Lisibilité optimale pour toutes les échelles de temps
- Pas de surcharge visuelle sur l'axe X
- Labels clairs et non-superposés

---

## 🧪 Tests

### Tests unitaires

**Fichier** : `tests/test_data_availability_visualizer.py`

**Couverture** :
```
✅ test_visualizer_initialization       - Initialisation
✅ test_create_figure                   - Création de figure
✅ test_group_consecutive_segments      - Groupement de segments
✅ test_multiple_turbines               - Plusieurs turbines
✅ test_generate_output_files           - Génération PNG/JSON
✅ test_empty_result                    - Résultat vide
✅ test_color_coding                    - Code couleur
```

**Exécution** :
```bash
pytest tests/test_data_availability_visualizer.py -v
```

### Exemple d'utilisation

**Fichier** : `tests/example_data_availability_visualizer.py`

**Ce qu'il fait** :
- Crée des données d'exemple pour 4 turbines (E9, E10, E11, E12)
- Simule différents patterns de disponibilité (good, partial, poor)
- Génère le graphique PNG + JSON
- Affiche les statistiques par turbine

**Exécution** :
```bash
python tests/example_data_availability_visualizer.py
```

**Sortie attendue** :
```
📊 Génération du graphique...
✅ VISUALISATION GÉNÉRÉE
📁 Fichiers générés:
   PNG: output\charts\data_availability.png
   JSON: output\charts\data_availability.json
```

---

## 📐 Détails techniques

### Mapping des noms de variables

```python
variable_display_names = {
    "wind_speed": "ws",
    "active_power": "power",
    "wind_direction": "dir",
    "temperature": "temp",
}
```

**Exemples de labels Y** :
- `ws_E1` → Wind Speed turbine E1
- `power_E1` → Active Power turbine E1
- `dir_E1` → Wind Direction turbine E1
- `temp_E1` → Temperature turbine E1

### Ordre d'affichage

Les turbines sont **triées alphabétiquement inversées** (de haut en bas) :

```
E12 (en haut)
E11
E10
E9  (en bas)
```

Les variables sont dans l'ordre :
```
temperature   (en haut)
wind_direction
active_power
wind_speed    (en bas)
```

### Gestion des timestamps

Les timestamps sont convertis en `pd.Timestamp` automatiquement.

**Important** : Les durées des barres sont calculées en heures (float) pour la sérialisation JSON :

```python
duration = (segment_end - segment_start).total_seconds() / 3600.0
```

### Légende

La légende n'affiche qu'une seule fois chaque groupe :

```python
show_legend = not any(
    getattr(trace, "legendgroup", None) == legend_group
    for trace in traces
)
```

---

## 🎯 Cas d'usage

### 1. Diagnostic de qualité des données

**Problème** : "Pourquoi mes analyses donnent des résultats étranges ?"  
**Solution** : Visualiser la disponibilité pour identifier les gaps de données

### 2. Validation avant traitement

**Problème** : "Mes données sont-elles suffisamment complètes ?"  
**Solution** : Vérifier visuellement que les périodes critiques ont des données

### 3. Identification de pannes capteurs

**Problème** : "Y a-t-il des capteurs défaillants ?"  
**Solution** : Les gaps récurrents sur une variable = capteur à vérifier

### 4. Rapport de qualité SCADA

**Problème** : "Le client veut un rapport de qualité des données"  
**Solution** : Inclure ce graphique dans le rapport Word/PDF

---

## 🔄 Intégration avec les workflows

### Avec DataAvailabilityAnalyzer

```python
# 1. Analyser la disponibilité
from src.wind_turbine_analytics.data_processing.analyzer.logics.data_availability_analyzer import (
    DataAvailabilityAnalyzer,
)

analyzer = DataAvailabilityAnalyzer()
result = analyzer._compute(
    operation_data=operation_df,
    log_data=log_df,
    turbine_config=config,
    criteria=criteria,
)

# 2. Créer un AnalysisResult
analysis_result = AnalysisResult(
    detailed_results={"E1": result},
    status="completed",
    requires_visuals=True,
)

# 3. Visualiser
visualizer = DataAvailabilityVisualizer()
output_paths = visualizer.generate(analysis_result)
```

### Avec ScadaWorkflow

Le visualiseur s'intègre automatiquement dans les workflows :

```python
# Dans scada_workflow.py
if analysis_result.requires_visuals:
    visualizer = DataAvailabilityVisualizer()
    visualizer.generate(analysis_result)
```

---

## 📏 Dimensions et performance

### Taille de sortie

| Turbines | Variables | Jours | Hauteur (px) | Taille PNG |
|----------|-----------|-------|--------------|------------|
| 1        | 4         | 3     | 600          | ~40 KB     |
| 4        | 4         | 3     | 800          | ~57 KB     |
| 10       | 4         | 7     | 1200         | ~120 KB    |

**Formule hauteur** : `height = max(600, n_variables * 25) px`

### Performance

| Opération | Temps typique |
|-----------|---------------|
| Création figure | ~100 ms |
| Export PNG | ~2-3 s |
| Export JSON | ~50 ms |
| Total | ~3-4 s |

---

## ⚠️ Limitations et considérations

### 1. Résolution temporelle

Le visualiseur affiche les données **par heure**. Pour des résolutions plus fines (minutes), le graphique devient illisible.

**Recommandation** : Utiliser l'optimisation horaire du `DataAvailabilityAnalyzer`.

### 2. Nombre de turbines

Au-delà de **20 turbines**, le graphique devient difficile à lire.

**Solution** : Créer plusieurs graphiques par groupe de turbines.

### 3. Périodes longues

Pour des périodes > 30 jours, l'axe X devient dense.

**Solution** : 
- Agréger par jour au lieu d'heure
- Diviser en plusieurs graphiques (par mois)

### 4. Encodage caractères

Éviter les caractères spéciaux (≥, ≤, etc.) dans les noms de légende car ils posent des problèmes d'encodage sur Windows.

**Utiliser** : `>`, `<`, `>=`, `<=` en ASCII

---

## 🔮 Améliorations futures

### À court terme

- [ ] Support des tooltips enrichis (statistiques horaires)
- [ ] Option pour afficher/masquer les gaps (barres blanches vs transparentes)
- [ ] Marqueurs pour événements spéciaux (maintenance, pannes)

### À moyen terme

- [ ] Mode agrégé par jour (pour longues périodes)
- [ ] Export vers formats supplémentaires (SVG, PDF)
- [ ] Intégration avec dashboard web interactif

### À long terme

- [ ] Comparaison multi-périodes (overlay temporel)
- [ ] Prédiction des futurs gaps (ML)
- [ ] Alertes automatiques (gaps anormaux)

---

## 📚 Références

### Code source

- **Visualiseur** : [data_availability_visualizer.py](../src/wind_turbine_analytics/data_processing/visualizer/chart_builders/data_availability_visualizer.py)
- **BaseVisualizer** : [base_visualizer.py](../src/wind_turbine_analytics/data_processing/visualizer/base_visualizer.py)
- **DataAvailabilityAnalyzer** : [data_availability_analyzer.py](../src/wind_turbine_analytics/data_processing/analyzer/logics/data_availability_analyzer.py)

### Tests et exemples

- **Tests** : [test_data_availability_visualizer.py](../tests/test_data_availability_visualizer.py)
- **Exemple** : [example_data_availability_visualizer.py](../tests/example_data_availability_visualizer.py)

### Documentation connexe

- **Optimisation** : [DATA_AVAILABILITY_OPTIMIZATION.md](./DATA_AVAILABILITY_OPTIMIZATION.md)
- **Architecture** : [CLAUDE.md](../CLAUDE.md)

### Bibliothèques

- **Plotly** : https://plotly.com/python/
- **Pandas** : https://pandas.pydata.org/

---

**Date de création** : 2026-04-28  
**Auteur** : gjacquet  
**Version** : 1.0  
**Format** : Graphique Gantt horizontal type SCADA
