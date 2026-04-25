# Tests - Wind Turbine Analytics

Ce dossier contient les tests unitaires et les exemples d'utilisation du projet.

## 📁 Structure

```
tests/
├── __init__.py                      # Package tests
├── conftest.py                      # Configuration pytest (PYTHONPATH)
├── test_reset_mode.py               # Tests unitaires pour Reset Mode
├── example_reset_mode_usage.py      # Exemple d'utilisation Reset Mode
└── README.md                        # Ce fichier
```

## 🚀 Exécution des tests

### Tous les tests
```bash
pytest
```

### Tests spécifiques
```bash
# Tests Reset Mode uniquement
pytest tests/test_reset_mode.py -v

# Un test spécifique
pytest tests/test_reset_mode.py::TestResetModeEnum::test_reset_mode_values -v
```

### Avec couverture
```bash
pytest --cov=src --cov-report=html
```

## 📝 Exemples

### Exécuter l'exemple Reset Mode
```bash
python tests/example_reset_mode_usage.py
```

## 🔧 Configuration

La configuration pytest se trouve dans `pytest.ini` à la racine du projet.

Le fichier `conftest.py` ajoute automatiquement le répertoire racine au `PYTHONPATH` pour permettre les imports depuis `src/`.

## ✅ Tests disponibles

### `test_reset_mode.py`

- **TestResetModeEnum** : Tests de l'énumération ResetMode
- **TestNordexN311ResetMode** : Tests des méthodes de filtrage par reset mode
- **TestResetModeFiltering** : Tests du filtrage des données
- **TestOperationalImpactAnalysis** : Tests de l'analyse d'impact opérationnel

## 📊 Résultat attendu

```
13 passed in 0.88s
```

Tous les tests doivent passer ! ✅
