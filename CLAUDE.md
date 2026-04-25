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

**Convention :**
- Méthode `analyze()` : Point d'entrée public
- Méthode `_compute()` : Implémentation spécifique (abstraite)
- Retourne toujours un `AnalysisResult`

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
