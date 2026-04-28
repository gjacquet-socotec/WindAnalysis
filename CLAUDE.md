# CLAUDE.md - Wind Turbine Analytics Project

Documentation du projet pour maintenir la cohérence et les bonnes pratiques.

---

## 📋 Vue d'ensemble

**Projet** : Wind Turbine Analytics  
**Objectif** : Analyse de performance et disponibilité d'éoliennes basée sur données SCADA et logs d'erreur  
**Langage** : Python 3.10+  
**Framework de test** : pytest

---

## 🏗️ Architecture du projet

```
WindAnalysis/
├── src/
│   ├── logger_config.py                    # Logger centralisé avec couleurs
│   └── wind_turbine_analytics/
│       ├── application/                     # Configuration et workflows
│       │   ├── configuration/              # Config models et validation
│       │   ├── utils/                      # Utilitaires (load_data, yaml)
│       │   └── workflows/                  # BaseWorkflow, ScadaWorkflow, etc.
│       ├── data_processing/                # Cœur du traitement
│       │   ├── analyzer/                   # Analyseurs de données
│       │   │   ├── base_analyzer.py       # Classe de base abstraite
│       │   │   └── logics/                # Analyseurs spécifiques
│       │   ├── chart_builders/            # Génération de visualisations
│       │   ├── log_code/                  # Gestion des codes d'erreur
│       │   │   ├── base_log_code.py      # Système de base (abstrait)
│       │   │   └── generator_type/       # Implémentations par constructeur
│       │   └── visualizer/                # Visualisations
│       └── presentation/                   # Présentation des résultats
├── assets/                                 # Fichiers de référence
│   ├── NORDEX_codes.csv                   # Codes d'erreur Nordex
│   └── template_*.docx                    # Templates de rapports
├── tests/                                  # Tests unitaires et exemples
│   ├── conftest.py                        # Config pytest (PYTHONPATH)
│   ├── test_*.py                          # Tests unitaires
│   └── example_*.py                       # Exemples d'utilisation
├── .gitignore                             # Fichiers à ignorer
├── pytest.ini                             # Configuration pytest
├── requirements.txt                       # Dépendances
└── CLAUDE.md                              # Ce fichier
```

---

## 🎯 Règles et conventions IMPORTANTES

### ⚠️ RÈGLE #1 : Toujours créer des tests unitaires

**Quand modifier du code, TOUJOURS :**
1. Créer/mettre à jour les tests unitaires dans `tests/test_*.py`
2. Créer un exemple d'utilisation si c'est une nouvelle fonctionnalité
3. Exécuter `pytest` pour vérifier que tous les tests passent
4. Mettre à jour la documentation si nécessaire

**Exemple :**
```bash
# Après modification
pytest tests/test_*.py -v
python tests/example_*.py
```

### 📝 RÈGLE #2 : Utiliser le logger centralisé

**TOUJOURS utiliser `get_logger()` au lieu de `logging.getLogger()`**

```python
# ✅ BON
from src.logger_config import get_logger
logger = get_logger(__name__)

# ❌ MAUVAIS
import logging
logger = logging.getLogger(__name__)
```

**Avantages :**
- Logs colorés (INFO=vert, WARNING=jaune, ERROR=rouge)
- Timestamps automatiques
- Nom du module pour traçabilité

### 🏛️ RÈGLE #3 : Architecture en couches

**Respecter la séparation des responsabilités :**

1. **Application Layer** : Configuration, orchestration, workflows
2. **Data Processing Layer** : Analyse, transformation, calculs
3. **Presentation Layer** : Affichage, rapports, export

**Ne JAMAIS :**
- Faire de l'analyse dans la couche présentation
- Mettre de la logique métier dans la configuration
- Mélanger les responsabilités

### 🔧 RÈGLE #4 : Pattern Template Method

**Les classes de base sont abstraites et doivent être héritées :**

- `BaseAnalyzer` → Analyseurs spécifiques (EBA, heures consécutives, etc.)
- `BaseWorkflow` → Workflows spécifiques (SCADA, RunTest)
- `BaseLogCodeManager` → Managers par constructeur (Nordex, Vestas, etc.)

**Exemple :**
```python
class MonAnalyzer(BaseAnalyzer):
    def _compute(self, operation_data, turbine_config, criteria):
        # Implémentation spécifique
        pass
```

### 📦 RÈGLE #5 : Structure des tests

**Conventions pytest :**
- Tests à la **racine** dans `tests/`
- Fichiers : `test_*.py` pour tests, `example_*.py` pour exemples
- Classes : `TestNomDeLaFonctionnalité`
- Méthodes : `test_description_du_test`
- Toujours utiliser des fixtures pour les données communes

---

## 🔍 Composants clés

### 1. Système de gestion des codes d'erreur

**Fichier** : `src/wind_turbine_analytics/data_processing/log_code/base_log_code.py`

**Enums importants :**
- `CodeCriticality` : CRITICAL, HIGH, MEDIUM, LOW
- `FunctionalSystem` : PITCH, GENERATOR, GRID_CONVERTER, etc.
- `ResetMode` : AUTOMATIC, MANUAL, SAFETY_LOCAL, SAFETY_REMOTE, MANUAL_AUTO

**Utilisation typique :**
```python
from src.wind_turbine_analytics.data_processing.log_code.generator_type.nordex_n311_log_code_manager import NordexN311LogCodeManager

manager = NordexN311LogCodeManager()

# Filtrer les données en excluant les erreurs manuelles
clean_data = manager.filter_by_codes(
    target_df=operation_df,
    log_df=log_df,
    code_column='oper',
    log_start_col='start_date',
    log_end_col='end_date',
    reset_mode_filter=["M", "SL"],
    exclude_error_periods=True
)
```

### 2. Logger centralisé

**Fichier** : `src/logger_config.py`

**Fonctionnalités :**
- Couleurs automatiques par niveau de log
- Timestamp format `[YYYY-MM-DD HH:MM:SS]`
- Affichage du nom du module
- Compatible Windows (colorama)

### 3. Analyseurs de données

**Classe de base** : `BaseAnalyzer`

**Analyseurs disponibles :**
- `ConsecutiveHoursAnalyzer` : Heures consécutives de fonctionnement
- `DataAvailabilityAnalyzer` : Disponibilité des données
- `EbACutInCutOutAnalyzer` : EBA avec filtrage des codes d'erreur
- `EbaManufacturerAnalyzer` : EBA sans filtrage (tous downtimes inclus)
- `NominalPowerAnalyzer` : Heures au-dessus d'un seuil de puissance nominale
- `TestCutInCutOutAnalyzer` : Analyse cut-in à cut-out avec filtrage arrêts
- `AutonomousOperationAnalyzer` : Autonomie d'exploitation (redémarrages manuels)
- `TestAvailabilityAnalyzer` : Disponibilité pendant la période de test

**Convention :**
- Méthode `analyze()` : Point d'entrée public
- Méthode `_compute()` : Implémentation spécifique (abstraite)
- Retourne toujours un `AnalysisResult`

### 4. Analyseur d'Autonomie d'Exploitation

**Fichier** : `src/wind_turbine_analytics/data_processing/analyzer/logics/autonomous_operation.py`

**Classe** : `AutonomousOperationAnalyzer`

**Objectif** : Vérifier que l'éolienne peut fonctionner sans redémarrage manuel local pendant la période de test.

**Critère** : Nombre de codes nécessitant redémarrage manuel ≤ 3 (config: `local_restarts.value`)

**Utilisation typique** :
```python
from src.wind_turbine_analytics.data_processing.analyzer.logics.autonomous_operation import AutonomousOperationAnalyzer

analyzer = AutonomousOperationAnalyzer()
result = analyzer.analyze(turbine_farm, criteria)

# Résultat :
# {
#     "manual_restart_count": 0,
#     "required_threshold": 3,
#     "criterion_met": True,
#     "manual_restart_events": []
# }
```

**Notes** :
- Identifie les codes MANUAL et SAFETY_LOCAL via `NordexN311LogCodeManager.get_codes_by_reset_mode()`
- Gère les événements ON/OFF dans les logs
- Pour Nordex N311 : aucun code manuel dans la base (validation automatique)

### 5. Analyseur de Disponibilité

**Fichier** : `src/wind_turbine_analytics/data_processing/analyzer/logics/test_availability_analyzer.py`

**Classe** : `TestAvailabilityAnalyzer`

**Objectif** : Calculer la disponibilité pendant la période de test.

**Critère** : Disponibilité ≥ 92% (config: `availability.value`)

**Formule** : `availability = (total_hours - unauthorized_downtime) / total_hours × 100`

**Utilisation typique** :
```python
from src.wind_turbine_analytics.data_processing.analyzer.logics.test_availability_analyzer import TestAvailabilityAnalyzer

analyzer = TestAvailabilityAnalyzer()
result = analyzer.analyze(turbine_farm, criteria)

# Résultat :
# {
#     "total_hours": 119.83,
#     "unauthorized_downtime_hours": 0.0,
#     "availability_percent": 100.0,
#     "required_threshold": 92,
#     "criterion_met": True
# }
```

**Notes** :
- Utilise la durée calendaire (test_end - test_start)
- Identifie les arrêts via `get_unauthorized_stop_codes()`
- Algorithme de suivi d'état pour gérer les chevauchements de codes
- Clipping des périodes dans la fenêtre de test

### 6. Analyseur de Calibration de Direction du Vent

**Fichier** : `src/wind_turbine_analytics/data_processing/analyzer/logics/wind_direction_calibration_analyzer.py`

**Classe** : `WindDirectionCalibrationAnalyzer`

**Objectif** : Vérifier que la nacelle suit correctement la direction du vent en comparant `wind_direction` (anémomètre) et `nacelle_position` (position yaw).

**Critère** : Écart angulaire moyen journalier ≤ 5° (config: `threshold_degrees`)

**Métriques calculées par jour** :
1. **Écart angulaire moyen** : Différence absolue moyenne (gestion wraparound 360°→0°)
2. **Écart-type** : Mesure la dispersion des écarts
3. **Écart maximum** : Détecte les anomalies ponctuelles
4. **Corrélation** : Mesure si la nacelle suit bien le vent (proche de 1.0 = bon)

**Utilisation typique** :
```python
from src.wind_turbine_analytics.data_processing.analyzer.logics.wind_direction_calibration_analyzer import WindDirectionCalibrationAnalyzer

analyzer = WindDirectionCalibrationAnalyzer()
result = analyzer.analyze(turbine_farm, criteria)

# Résultat :
# {
#     "overall_mean_angular_error": 3.02,
#     "overall_std_angular_error": 0.95,
#     "overall_max_angular_error": 5.24,
#     "overall_correlation": 0.976,
#     "threshold_degrees": 5.0,
#     "criterion_met": True,
#     "total_measurements": 168,
#     "daily_calibration": [
#         {
#             "date": "2024-01-01",
#             "mean_angular_error": 2.78,
#             "std_angular_error": 1.01,
#             "max_angular_error": 4.4,
#             "correlation": 0.98,
#             "num_measurements": 24
#         },
#         ...
#     ]
# }
```

**Notes** :
- Filtre automatiquement les données avec `wind_speed > cut-in` (périodes actives uniquement)
- Gestion du wraparound 360°/0° : `angle1=359°, angle2=1°` → écart = 2° (chemin le plus court)
- Fonction `_calculate_angular_difference` utilise la formule : `min(|a1 - a2|, 360 - |a1 - a2|)`
- Agrégation journalière pour éviter des graphiques trop lourds

**Visualiseur associé** : `WindDirectionCalibrationVisualizer`
- Génère 2 subplots par turbine :
  1. **Écart angulaire moyen journalier** (ligne bleue vs seuil rouge 5°)
  2. **Corrélation journalière** (ligne verte vs référence orange 0.95)
- Annotation automatique du résultat global : `[OK]` ou `[!]`
- Format PNG + JSON pour dashboard web futur

**Approche de conception** :
- Hérite de `BaseAnalyzer` pour uniformité
- Pattern d'agrégation journalière similaire à `DataAvailabilityAnalyzer`
- Structure de retour similaire à `EbaManufacturerAnalyzer` (métriques globales + détails journaliers)

### 7. Visualiseur Rose des Puissances (PowerRoseChartVisualizer)

**Fichier** : `src/wind_turbine_analytics/data_processing/visualizer/chart_builders/power_rose_chart_visualizer.py`

**Classe** : `PowerRoseChartVisualizer`

**Objectif** : Visualiser la puissance moyenne produite selon la direction du vent sous forme de rose polaire (16 secteurs de 22.5°).

**Utilité** : 
- Détecter les problèmes de calibration de nacelle (secteurs sous-performants)
- Identifier les effets de sillage entre turbines
- Repérer les obstacles environnementaux (arbres, bâtiments)

**Relation avec WindDirectionCalibrationVisualizer** :
- **WindDirectionCalibrationVisualizer** : Diagnostic (écarts nacelle/vent)
- **PowerRoseChartVisualizer** : Impact (conséquence sur la production)
- **Utilisation combinée** : Secteurs avec faible puissance + écart élevé = Action prioritaire

**Utilisation typique** :
```python
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.power_rose_chart_visualizer import PowerRoseChartVisualizer

# Préparer un AnalysisResult avec chart_data
result = AnalysisResult(
    detailed_results={
        "E01": {
            "chart_data": pd.DataFrame({
                "wind_direction": [...],  # 0-360°
                "activation_power": [...],  # kW
            })
        }
    },
    status="completed"
)

# Générer la rose des puissances
visualizer = PowerRoseChartVisualizer()
output_paths = visualizer.generate(result)
# Retourne: {"png_path": "...", "json_path": "..."}
```

**Caractéristiques** :
- **16 secteurs directionnels** : N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW
- **Gradient de couleurs** : Rouge (faible production) → Bleu (haute production)
- **Graphique polaire** : Longueur des barres = puissance moyenne en kW
- **Grille multi-turbines** : Max 3 colonnes, ajustement automatique
- **Tooltips interactifs** : Direction, puissance moyenne, nombre d'observations

**Insights fournis** :
- **Secteurs sous-performants** : Identifie visuellement les directions avec faible production
- **Uniformité** : Une rose équilibrée indique une bonne calibration globale
- **Asymétries** : Des secteurs faibles indiquent un problème localisé (calibration ou obstacle)
- **Comparaison turbines** : Détecte les effets de sillage (turbine en aval sous-performe sur certains secteurs)

**Notes techniques** :
- Binning directionnel avec gestion du wraparound 360°/0° (décalage de 11.25° pour centrer le Nord)
- Calcul de la puissance moyenne par secteur (pas de somme)
- Palette de couleurs normalisée sur le max global pour comparaison entre turbines
- Axe radial avec échelle en kW (ajustée automatiquement)

**Approche de conception** :
- Inspiré de `WindRoseChartVisualizer` mais pour la puissance au lieu de la fréquence
- Utilise `go.Barpolar` de Plotly pour graphiques polaires
- Grille de subplots avec `specs=[{"type": "polar"}]`
- Gradient de couleurs pour visualisation rapide des performances

---

## 📐 Conventions de code

### Style

- **PEP 8** : Respecter les conventions Python
- **Limite de ligne** : 79-88 caractères (flexible pour lisibilité)
- **Docstrings** : Format Google/NumPy style
- **Type hints** : Utiliser partout où possible

### Nommage

- **Fichiers** : `snake_case.py`
- **Classes** : `PascalCase`
- **Fonctions/méthodes** : `snake_case()`
- **Constants** : `UPPER_SNAKE_CASE`
- **Variables privées** : `_leading_underscore`

### Imports

**Ordre standard :**
```python
# 1. Imports standard library
import sys
from pathlib import Path
from typing import Dict, Any

# 2. Imports tiers (pandas, numpy, etc.)
import pandas as pd
import numpy as np

# 3. Imports locaux
from src.logger_config import get_logger
from src.wind_turbine_analytics.data_processing.analyzer.base_analyzer import BaseAnalyzer
```

---

## 🚀 Workflow de développement

### Ajout d'une nouvelle fonctionnalité

1. **Planifier** : Identifier où la fonctionnalité s'intègre (quelle couche ?)
2. **Coder** : Implémenter en respectant les patterns existants
3. **Tester** : Créer tests unitaires dans `tests/test_*.py`
4. **Exemple** : Créer un exemple d'utilisation dans `tests/example_*.py`
5. **Documenter** : Mettre à jour ce fichier CLAUDE.md si nécessaire
6. **Valider** : Exécuter `pytest` et les exemples

### Modification d'une classe existante

1. **Lire les tests** existants pour comprendre le comportement attendu
2. **Modifier** le code
3. **Mettre à jour** les tests si le comportement change
4. **Ajouter** de nouveaux tests pour les nouveaux cas
5. **Vérifier** : `pytest -v`

### Correction de bug

1. **Créer un test** qui reproduit le bug (test doit échouer)
2. **Corriger** le code
3. **Vérifier** que le test passe maintenant
4. **Commit** avec message explicite

---

## 📊 Décisions architecturales importantes

### Pourquoi `tests/` à la racine ?

**Décision** : Tests à la racine du projet, pas dans `src/`

**Raisons :**
- Convention Python standard (Django, Flask, pandas)
- Séparation claire code production vs tests
- Packaging propre (tests exclus du package)
- Découverte automatique par pytest

### Pourquoi un logger centralisé ?

**Décision** : Un seul point de configuration du logging

**Raisons :**
- Uniformité des logs dans tout le projet
- Facilite le debugging avec couleurs
- Configuration centralisée (facile de changer le format)

### Pourquoi Pattern Template Method ?

**Décision** : Classes de base abstraites pour analyseurs, workflows, managers

**Raisons :**
- Réutilisation du code commun
- Garantit une interface cohérente
- Facilite l'ajout de nouveaux types (nouvelles éoliennes, nouveaux analyseurs)
- Maintenabilité : modification dans la base = propagation automatique

### Pourquoi dataclasses frozen ?

**Décision** : `@dataclass(frozen=True)` pour les configurations

**Raisons :**
- Immutabilité = sécurité (pas de modification accidentelle)
- Hash automatique (utilisable dans sets/dicts)
- Thread-safe
- Intention claire : ce sont des données, pas des objets mutables

---

## 🔄 Historique des modifications majeures

### 2026-04-25 : Identification des arrêts non autorisés

**Changements :**
- Ajout de `get_unauthorized_stop_codes()` dans `NordexN311LogCodeManager`
- Tests unitaires dans `tests/test_unauthorized_stops.py`
- Exemple d'utilisation dans `tests/example_unauthorized_stops.py`

**Objectif :** Permettre d'identifier et filtrer les arrêts non autorisés (pannes) basé sur les données CSV.

**Critères d'un arrêt non autorisé (selon CSV Nordex) :**
- Affecte la disponibilité (`availability = "yes"`)
- Génère un arrêt immédiat (`dead_level >= 270`)

**Approche de conception :**
- Utilise les méthodes existantes `affects_availability()` et `is_critical_stop()`
- Pas de logique hardcodée (FM6, FM7) dans la classe de base
- Logique spécifique à Nordex reste dans `NordexN311LogCodeManager`
- Flexible : permet aux autres constructeurs de définir leurs propres critères

### 2026-04-25 : Ajout du système Reset Mode

**Changements :**
- Ajout de l'enum `ResetMode` dans `base_log_code.py`
- Nouvelles méthodes de filtrage par mode de reset
- Tests unitaires dans `tests/test_reset_mode.py`
- Exemple d'utilisation dans `tests/example_reset_mode_usage.py`

**Objectif :** Permettre de filtrer les données selon le mode de réinitialisation des codes d'erreur (automatique vs manuel).

### 2026-04-25 : Uniformisation du logger

**Changements :**
- Création de `src/logger_config.py`
- Migration de tous les `logging.getLogger()` vers `get_logger()`
- Support des couleurs multi-plateforme (colorama)

**Objectif :** Logs cohérents et lisibles dans tout le projet.

### 2026-04-25 : Structure des tests

**Changements :**
- Création du dossier `tests/` à la racine
- Configuration pytest dans `pytest.ini`
- `conftest.py` pour gestion du PYTHONPATH

**Objectif :** Suivre les conventions Python standard.

### 2026-04-26 : Implémentation des Analyseurs d'Autonomie et Disponibilité

**Changements :**
- Ajout de `AutonomousOperationAnalyzer` (critère 4 - redémarrages locaux)
- Ajout de `TestAvailabilityAnalyzer` (critère 5 - disponibilité)
- Correction du seuil de puissance nominale : 97.33% → 97%
- Création du script de diagnostic : `tests/debug_nominal_power_full_diagnostic.py`

**Objectif :** Compléter les 5 critères de validation RunTest.

**Résultats validés** (données réelles E1, E6, E8) :
1. ✅ Heures consécutives : ~120h
2. ✅ Cut-in à Cut-out : Validé (avec filtrage arrêts non autorisés)
3. ✅ Puissance nominale : 3.67h, 5.33h, 7.33h (seuil 97%)
4. ✅ Autonomie : 0 redémarrages manuels
5. ✅ Disponibilité : 100% (0h d'arrêt)

**Approche de conception :**
- Réutilisation de `NordexN311LogCodeManager` pour identifier les codes
- Algorithme de suivi d'état pour les événements ON/OFF
- Gestion des chevauchements de codes multiples
- Clipping des périodes dans la fenêtre de test

**Notes techniques :**
- Import circulaire résolu : `runtest_workflow.py` importe les analyseurs au niveau module
- Signature `_compute()` étendue : `operation_data, log_data, turbine_config, criteria`
- Les deux analyseurs reçoivent `log_data` déjà chargé par `BaseAnalyzer`

### 2026-04-28 : Ajout du visualiseur des pertes d'énergie (EbaLossVisualizer)

**Changements :**
- Ajout de `EbaLossVisualizer` dans `chart_builders/eba_loss_visualizer.py`
- Tests unitaires dans `tests/test_eba_loss_visualizer.py`
- Exemple d'utilisation dans `tests/example_eba_loss_visualizer.py`

**Objectif :** Visualiser les pertes d'énergie mensuelles par turbine sous forme d'histogramme avec échelle de couleurs.

**Caractéristiques :**
- **Type de graphique** : Histogramme groupé (barres par turbine et par mois)
- **Axe X** : Périodes mensuelles
- **Axe Y** : Pourcentage de perte d'énergie (calculé : 100 - performance)
- **Couleurs** : Dégradé du bleu (faibles pertes) au rouge (pertes élevées)
- **Palette** : Utilise `seaborn.color_palette("coolwarm")` pour générer le gradient
- **Format de sortie** : PNG + JSON (Plotly) pour intégration future dans dashboard web

**Utilisation typique :**
```python
from src.wind_turbine_analytics.data_processing.analyzer.logics.eba_manifacturer_analyzer import EbaManufacturerAnalyzer
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.eba_loss_visualizer import EbaLossVisualizer

# Analyser les turbines
analyzer = EbaManufacturerAnalyzer()
result = analyzer.analyze(turbine_farm, criteria)

# Générer le visualiseur
visualizer = EbaLossVisualizer()
output_paths = visualizer.generate(result)
# Retourne: {"png_path": "...", "json_path": "..."}
```

**Approche de conception :**
- Hérite de `BaseVisualizer` pour uniformité
- Calcul automatique des pertes : `loss_percent = 100 - performance`
- Normalisation des couleurs sur l'ensemble des données (min/max)
- Gestion des turbines multiples avec barres groupées (`barmode="group"`)
- Tooltips interactifs avec Plotly (hover sur les barres)

**Notes techniques :**
- Compatible avec `EbaManufacturerAnalyzer` (utilise `monthly_performance`)
- Largeur des barres ajustée dynamiquement selon le nombre de turbines
- Support des données manquantes (affiche 0 pour les mois sans données)
- Fichiers de sortie stockés dans `result.metadata["charts"]`

### 2026-04-28 : Implémentation du visualiseur Top Error Codes (TopErrorCodeFrequencyVisualizer)

**Changements :**
- Implémentation complète de `TopErrorCodeFrequencyVisualizer` dans `chart_builders/top_error_code_frequency_visualizer.py`
- Tests unitaires dans `tests/test_top_error_frequency_visualizer.py`
- Exemple d'utilisation dans `tests/example_top_error_frequency_visualizer.py`

**Objectif :** Visualiser le top 10 des codes d'erreur par fréquence et durée pour identifier les problèmes récurrents et impactants.

**Caractéristiques :**
- **Type de graphique** : Grille de subplots avec barres horizontales
  - **Une ligne par turbine** pour analyse individuelle
  - **Colonne gauche** : Top 10 par fréquence (nombre d'occurrences)
  - **Colonne droite** : Top 10 par durée totale (heures d'indisponibilité)
- **Couleurs par criticité** :
  - 🔴 Rouge (`#d62728`) : CRITICAL
  - 🟠 Orange (`#ff7f0e`) : HIGH
  - 🟡 Jaune (`#ffbb33`) : MEDIUM
  - 🟢 Vert (`#2ca02c`) : LOW
  - ⚫ Gris (`#7f7f7f`) : Unknown
- **Orientation** : Barres horizontales (meilleure lisibilité pour les codes)
- **Ordre** : Inversé pour avoir les valeurs les plus élevées en haut
- **Format de sortie** : PNG + JSON (Plotly) pour dashboard web

**Utilisation typique :**
```python
from src.wind_turbine_analytics.data_processing.analyzer.logics.code_error_analyzer import CodeErrorAnalyzer
from src.wind_turbine_analytics.data_processing.visualizer.chart_builders.top_error_code_frequency_visualizer import TopErrorCodeFrequencyVisualizer

# Analyser les codes d'erreur
analyzer = CodeErrorAnalyzer()
result = analyzer.analyze(turbine_farm, criteria)

# Générer le visualiseur
visualizer = TopErrorCodeFrequencyVisualizer()
output_paths = visualizer.generate(result)
# Retourne: {"png_path": "...", "json_path": "..."}
```

**Approche de conception :**
- Hérite de `BaseVisualizer` pour uniformité
- Utilise `make_subplots` de Plotly pour créer une grille (n_turbines x 2)
- Hauteur dynamique : `400 + (n_turbines * 350)` pixels
- Extrait `code_frequency` (fréquence) et `most_impactful_codes` (durée) du résultat
- Mapping automatique des couleurs selon criticité depuis `CodeErrorAnalyzer`
- Tooltips interactifs avec description complète des codes
- Affichage des valeurs sur les barres (`textposition="outside"`)
- Turbines triées alphabétiquement pour cohérence

**Insights fournis :**
- **Fréquence** : Identifie les codes qui apparaissent le plus souvent → problèmes récurrents
- **Durée** : Identifie les codes avec le plus d'impact temporel → priorités de maintenance
- **Criticité visuelle** : Permet de repérer rapidement les codes critiques (rouge/orange)
- **Comparaison** : Un code fréquent peut avoir une courte durée (reset rapide) vs code rare mais long
- **Analyse par turbine** : Identifie les problèmes spécifiques à chaque éolienne
- **Vue d'ensemble** : Permet de comparer la santé entre turbines du même parc

**Notes techniques :**
- Compatible avec `CodeErrorAnalyzer` (utilise `code_frequency` et `most_impactful_codes`)
- Gère plusieurs turbines simultanément (une ligne par turbine dans la grille)
- Inversion de l'ordre des données pour affichage top-down
- Troncature des descriptions à 50 caractères pour lisibilité
- `showlegend=False` car les noms des turbines sont dans les titres des subplots
- Axes X avec titre seulement sur la dernière ligne (évite répétition)
- Espacement vertical adaptatif : `0.08 / n_turbines` pour optimiser l'espace

### 2026-04-28 : Implémentation de l'Analyseur de Calibration de Direction du Vent

**Changements :**
- Ajout de `WindDirectionCalibrationAnalyzer` dans `analyzer/logics/wind_direction_calibration_analyzer.py`
- Ajout de `WindDirectionCalibrationVisualizer` dans `visualizer/chart_builders/wind_direction_calibration_visualizer.py`
- Tests unitaires complets dans `tests/test_wind_direction_calibration.py` (14 tests ✓)
- Tests du visualiseur dans `tests/test_wind_direction_calibration_visualizer.py` (8 tests ✓)
- Exemples d'utilisation : `tests/example_wind_direction_calibration.py` et `tests/example_wind_direction_calibration_visualizer.py`

**Objectif :** Analyser la qualité de la calibration de la nacelle par rapport à la direction du vent.

**Caractéristiques de l'analyseur :**
- **Critère** : Écart angulaire moyen journalier ≤ 5°
- **4 métriques par jour** : Écart moyen, écart-type, écart max, corrélation
- **Gestion du wraparound 360°/0°** : Calcul du chemin angulaire le plus court
- **Filtrage intelligent** : Uniquement périodes avec `wind_speed > cut-in`
- **Agrégation journalière** : Évite les graphiques trop lourds avec des milliers de points

**Caractéristiques du visualiseur :**
- **2 subplots par turbine** :
  1. Écart angulaire moyen journalier (ligne bleue) vs seuil 5° (ligne rouge)
  2. Corrélation journalière (ligne verte) vs référence 0.95 (ligne orange)
- **Annotation automatique** : `[OK]` (vert) ou `[!]` (rouge) selon critère
- **Zone colorée** : Vert si critère satisfait, rouge sinon
- **Format** : PNG (120K) + JSON (20K) pour dashboard web futur

**Validation :**
- Tous les tests unitaires passent (22 tests au total)
- Exemple généré avec 3 turbines synthétiques (bonne, limite, mauvaise calibration)
- Graphiques générés dans `output/charts/wind_direction_calibration.png`

**Approche de conception :**
- Fonction utilitaire `_calculate_angular_difference` pour wraparound : `min(|a1-a2|, 360-|a1-a2|)`
- Pattern d'agrégation journalière inspiré de `DataAvailabilityAnalyzer`
- Structure de retour similaire à `EbaManufacturerAnalyzer` (métriques globales + détails journaliers)
- Visualiseur utilise `make_subplots` comme `TopErrorCodeFrequencyVisualizer`
- Hauteur dynamique : `400 + (n_turbines * 350)` pixels

**Notes techniques :**
- Déjà intégré dans `scada_workflow.py` (ligne 11 : import existant)
- Compatible avec le système de configuration YAML existant
- Gère automatiquement les données manquantes (NaN dans `wind_direction` ou `nacelle_position`)
- Corrélation = NaN si variance nulle (tous les angles identiques)

### 2026-04-28 : Implémentation du PowerRoseChartVisualizer (Rose des Puissances)

**Changements :**
- Implémentation complète de `PowerRoseChartVisualizer` dans `visualizer/chart_builders/power_rose_chart_visualizer.py`
- Tests unitaires dans `tests/test_power_rose_chart_visualizer.py` (10 tests ✓)
- Exemple démontrant la relation avec `WindDirectionCalibrationVisualizer` : `tests/example_power_rose_calibration_relationship.py`

**Objectif :** Visualiser la puissance moyenne produite selon la direction du vent pour identifier les secteurs sous-performants.

**Relation avec WindDirectionCalibrationVisualizer :**
- **Approche complémentaire** :
  1. `WindDirectionCalibrationVisualizer` : **Diagnostic** → Détecte les écarts nacelle/vent
  2. `PowerRoseChartVisualizer` : **Impact** → Quantifie la perte de production par secteur
- **Utilisation combinée** : Secteur avec faible puissance + écart de calibration élevé = Priorité d'intervention

**Caractéristiques du visualiseur :**
- **16 secteurs directionnels** (22.5° chacun) : N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW
- **Graphique polaire** : Longueur des barres = puissance moyenne (kW)
- **Gradient de couleurs** : Rouge (faible) → Bleu (élevée) selon puissance normalisée
- **Grille multi-turbines** : Max 3 colonnes, ajustement automatique de hauteur
- **Tooltips interactifs** : Direction, puissance moyenne, nombre d'observations

**Insights fournis :**
- **Problèmes de calibration localisés** : Secteurs avec puissance réduite
- **Effets de sillage** : Turbines en aval sous-performent sur secteurs spécifiques
- **Obstacles environnementaux** : Bâtiments/arbres réduisent production sur certains secteurs
- **Validation de calibration** : Rose équilibrée = bonne calibration

**Validation :**
- Tous les tests passent (10/10)
- Exemple avec 3 turbines :
  - E01 : Bonne calibration (3°) → Rose uniforme
  - E02 : Problème secteur Nord → Puissance réduite 330-30°
  - E03 : Mauvaise calibration (8°) → Production globalement réduite
- Graphiques générés : `output/charts/power_rose_chart.png` (haute résolution)

**Approche de conception :**
- Inspiré de `WindRoseChartVisualizer` mais affiche puissance au lieu de fréquence
- Utilise `go.Barpolar` de Plotly pour graphiques polaires
- Binning directionnel avec gestion wraparound 360°/0° (décalage 11.25° pour centrer Nord)
- Normalisation des couleurs sur le max global pour comparaison inter-turbines
- Grille de subplots avec `specs=[{"type": "polar"}]`

**Notes techniques :**
- Requiert `chart_data` dans `AnalysisResult` avec colonnes `wind_direction` et `activation_power`
- Calcul de puissance moyenne par secteur (pas de somme)
- Échelle radiale en kW ajustée automatiquement
- Compatible avec tous les analyseurs qui fournissent ces colonnes

---

## 📝 Configuration YAML pour les mappings de colonnes

### Mapping des colonnes de logs (date/time)

Le système supporte **deux formats** pour les colonnes temporelles dans les logs :

#### **Format 1 : Date et Time séparés** (Recommandé pour fichiers avec colonnes séparées)
```yaml
mapping_log_data:
  start_date: ["date", "time"]  # LISTE de colonnes à fusionner
  end_date: ["date", "time"]
  name: name
  oper: oper
  status: status
```

#### **Format 2 : Colonne timestamp unique**
```yaml
mapping_log_data:
  start_date: timestamp  # STRING - colonne unique
  end_date: timestamp
  name: name
  oper: oper
```

### Utilisation dans le code

```python
from src.wind_turbine_analytics.application.utils.load_data import (
    load_csv,
    prepare_log_dataframe_with_mapping
)

# Charger le fichier
log_df = load_csv("path/to/log.csv")

# Préparer avec le mapping
log_prepared, start_col, end_col = prepare_log_dataframe_with_mapping(
    log_df, turbine_config.mapping_log_data
)

# Utiliser avec create_time_mask
mask = manager.create_time_mask(
    log_df=log_prepared,
    target_df=operation_df,
    code_column='oper',
    log_start_col=start_col,  # Utilise le nom préparé
    log_end_col=end_col,
    target_timestamp_col='timestamp'
)
```

### Avantages

✅ **Flexible** : Supporte les fichiers avec colonnes séparées ou timestamp unique  
✅ **Automatique** : `prepare_log_dataframe_with_mapping()` fusionne si nécessaire  
✅ **Type-safe** : Validation par `TurbineLogMapping` dataclass  
✅ **Rétrocompatible** : Fonctionne avec l'ancien format string

---

## 📚 Ressources et références

### Documentation interne

- Ce fichier : Architecture et conventions
- `tests/README.md` : Guide d'utilisation des tests
- `src/wind_turbine_analytics/data_processing/log_code/README.md` : Système de codes d'erreur

### Outils externes

- **pytest** : https://docs.pytest.org/
- **pandas** : https://pandas.pydata.org/docs/
- **colorama** : https://pypi.org/project/colorama/

---

## ✅ Checklist avant commit

- [ ] Tous les tests passent (`pytest -v`)
- [ ] Les nouveaux tests sont créés pour les modifications
- [ ] Les exemples fonctionnent (`python tests/example_*.py`)
- [ ] Le logger centralisé est utilisé (pas de `logging.getLogger()`)
- [ ] Les imports sont dans le bon ordre
- [ ] Les docstrings sont à jour
- [ ] Le fichier `.gitignore` exclut les fichiers temporaires
- [ ] CLAUDE.md est mis à jour si nécessaire

---

## 🆘 En cas de problème

### Import errors

**Problème** : `ModuleNotFoundError: No module named 'src'`

**Solution** :
```python
# Ajouter en haut du script
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### Tests ne passent pas

**Problème** : Tests échouent après modification

**Solution** :
1. Lire le message d'erreur complet
2. Vérifier que les fixtures sont correctes
3. Exécuter un test isolé : `pytest tests/test_file.py::TestClass::test_method -v`

### Encodage Windows

**Problème** : `UnicodeEncodeError` avec emojis

**Solution** :
```python
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
```

---

## 💡 Bonnes pratiques

1. **Lire le code existant** avant d'ajouter du nouveau code
2. **Tester localement** avant de commit
3. **Documenter** les décisions non-évidentes dans les commentaires
4. **Utiliser le logger** au lieu de `print()` pour le debugging
5. **Respecter les abstractions** (ne pas contourner les classes de base)
6. **Préférer la composition** à l'héritage quand c'est pertinent
7. **Fail fast** : Valider les entrées tôt, lever des exceptions claires

---

**Dernière mise à jour** : 2026-04-25  
**Mainteneur** : gjacquet  
**Contact** : Voir le projet pour coordonnées
