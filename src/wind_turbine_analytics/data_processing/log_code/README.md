# Gestionnaire de Codes d'Erreur et de Warning

Ce module fournit une infrastructure pour gérer et analyser les codes d'erreur et de warning des éoliennes dans les analyses SCADA et RunTest.

## Architecture

### Classe de Base: `BaseLogCodeManager`

La classe `BaseLogCodeManager` fournit la logique commune pour tous les types de génératrices:

- **Chargement automatique** des codes constructeur depuis un fichier CSV
- **Classification** par criticité et système fonctionnel
- **Analyse** des logs pour identifier les codes problématiques
- **Filtrage** par criticité, système, ou type d'arrêt

### Classes Spécialisées

Chaque type de génératrice a sa propre classe qui hérite de `BaseLogCodeManager` et implémente:

- Classification spécifique des codes
- Règles de criticité adaptées au constructeur
- Regroupement fonctionnel selon la documentation constructeur

#### Actuellement Supporté

- **NORDEX N311**: `NordexN311LogCodeManager`

## Classification des Codes

### Par Criticité

Les codes sont classifiés selon 4 niveaux de criticité:

#### 1. **CRITICAL** (Critique)
- Dead Level ≥ 270
- Génèrent des arrêts immédiats
- Nécessitent une réinitialisation manuelle obligatoire
- Impact direct sur la production

**Exemple**: FM104 (overspeed detection)

#### 2. **HIGH** (Haute priorité)
- Occurrences > seuil défini (par défaut 50)
- Codes répétitifs révélant une dégradation
- Nécessitent une investigation prioritaire

**Exemple**: FM615 avec 292 occurrences

#### 3. **MEDIUM** (Priorité moyenne)
- Dead Level < 270
- Avertissements
- Maintenance conditionnelle
- Surveillance recommandée

**Exemple**: FM150 (température gearbox haute)

#### 4. **LOW** (Informatif)
- Codes informationnels
- Niveaux très bas ou nuls
- Suivi normal

**Exemple**: FM0 (WTG System OK)

### Par Système Fonctionnel

Les codes sont regroupés par système pour identifier les zones problématiques:

- **PITCH**: Angles des pales, batteries pitch (codes 1xxx, 5xxx)
- **GRID_CONVERTER**: Réseau électrique, convertisseur (codes 1201-1215, 300-342)
- **ENVIRONMENT**: Vent, température, givrage (codes 1002, 1005, 920)
- **ROTOR_BRAKE**: Frein rotor (codes 202, 251-270)
- **SAFETY**: Système de sécurité (codes 50-60, 5001-5203)
- **GENERATOR**: Générateur (codes 120-121)
- **GEARBOX**: Boîte de vitesses (codes 124, 150-162)
- **VIBRATION**: Vibrations (codes 57-65)
- **SYSTEM**: Système général WTG
- **OTHER**: Autres codes

## Utilisation

### 1. Initialisation

```python
from src.wind_turbine_analytics.data_processing.log_code.generator_type import (
    NordexN311LogCodeManager,
)

# Initialisation avec chemin par défaut (assets/NORDEX_codes.csv)
manager = NordexN311LogCodeManager()

# Ou avec un chemin personnalisé
from pathlib import Path
custom_path = Path("./path/to/custom_codes.csv")
manager = NordexN311LogCodeManager(custom_path)
```

### 2. Récupération d'un Code Spécifique

```python
code = manager.get_code("FM104")
if code:
    print(f"Code: {code.code}")
    print(f"Description: {code.description}")
    print(f"Criticité: {code.criticality.value}")
    print(f"Système: {code.functional_system.value}")
    print(f"Arrêt critique: {code.is_critical_stop()}")
    print(f"Reset manuel requis: {code.requires_manual_reset()}")
```

### 3. Analyse de Logs SCADA/RunTest

```python
import pandas as pd

# Charger vos logs (exemple)
log_df = pd.read_csv("path/to/log_file.csv")

# Analyser avec le nom de colonne approprié
# En pratique, utiliser turbine_config.mapping_log_data.oper
analysis = manager.analyze_log_codes(log_df, code_column='operator_code')

# Résultats
print(f"Codes uniques: {analysis['total_unique_codes']}")
print(f"Codes connus: {analysis['known_codes_count']}")
print(f"Codes inconnus: {analysis['unknown_codes_count']}")

# Codes d'arrêt critique détectés
for code in analysis['critical_stops']:
    print(f"  - {code}")
```

### 4. Intégration avec TurbineConfig

```python
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineConfig,
    TurbineLogMapping,
)

# Configuration de la turbine
log_mapping = TurbineLogMapping(
    start_date="2024-01-01 00:00:00",
    end_date="2024-01-31 23:59:59",
    name="turbine_name",
    oper="operator_code",  # Colonne contenant les codes
    status="status_column",
)

# Chargement des logs
log_df = pd.read_csv(turbine_config.general_information.path_log_data)

# Analyse avec le mapping configuré
manager = NordexN311LogCodeManager()
analysis = manager.analyze_log_codes(log_df, log_mapping.oper)
```

### 5. Filtrage par Criticité ou Système

```python
from src.wind_turbine_analytics.data_processing.log_code import (
    CodeCriticality,
    FunctionalSystem,
)

# Récupérer tous les codes critiques
critical_codes = manager.get_codes_by_criticality(CodeCriticality.CRITICAL)

# Récupérer tous les codes de vibration
vibration_codes = manager.get_codes_by_system(FunctionalSystem.VIBRATION)

# Récupérer tous les codes générant un arrêt critique
critical_stop_codes = manager.get_critical_stop_codes()
```

### 6. Mise à Jour de Criticité Basée sur les Occurrences

Certains codes avec un Dead Level bas peuvent devenir prioritaires s'ils se répètent fréquemment:

```python
# Compter les occurrences dans les logs
code_occurrences = log_df['operator_code'].value_counts().to_dict()

# Promouvoir les codes répétitifs en HIGH priority
manager.update_criticality_based_on_occurrences(
    code_occurrences,
    high_threshold=50  # Seuil personnalisable
)
```

### 7. Génération de Rapport

```python
# Générer un rapport textuel complet
report = manager.generate_report(log_df, code_column='operator_code')
print(report)

# Sauvegarder le rapport
with open("rapport_codes_erreur.txt", "w", encoding="utf-8") as f:
    f.write(report)
```

### 8. Récupération des Codes Prioritaires pour Investigation

```python
priority_codes = manager.get_priority_codes_for_investigation()

print("Codes CRITIQUES:")
for code in priority_codes['critical']:
    print(f"  {code.code}: {code.description}")

print("\nCodes HAUTE PRIORITÉ:")
for code in priority_codes['high']:
    print(f"  {code.code}: {code.description}")
```

### 9. Création de Masques Temporels et Filtrage de Données

**Cas d'usage principal**: Filtrer les données opérationnelles SCADA en fonction des périodes d'erreur.

#### A. Exclure les périodes d'erreur critique

```python
# Charger les données opérationnelles et les logs
operation_df = pd.read_csv("operation_data.csv")  # Colonnes: timestamp, power, wind_speed, etc.
log_df = pd.read_csv("log_data.csv")  # Colonnes: start_date, end_date, operator_code

# Filtrer pour exclure les codes CRITICAL
clean_data = manager.filter_by_codes(
    target_df=operation_df,
    log_df=log_df,
    code_column='operator_code',
    log_start_col='start_date',
    log_end_col='end_date',
    target_timestamp_col='timestamp',
    criticality_filter=[CodeCriticality.CRITICAL],
    exclude_error_periods=True  # Exclure les périodes d'erreur
)

# Maintenant clean_data ne contient que les données pendant les périodes normales
print(f"Disponibilité: {len(clean_data)/len(operation_df)*100:.1f}%")
```

#### B. Analyser UNIQUEMENT les périodes de vibration

```python
# Garder SEULEMENT les données pendant les événements de vibration
vibration_data = manager.filter_by_codes(
    target_df=operation_df,
    log_df=log_df,
    code_column='operator_code',
    log_start_col='start_date',
    log_end_col='end_date',
    target_timestamp_col='timestamp',
    system_filter=[FunctionalSystem.VIBRATION],
    exclude_error_periods=False  # False = garder les périodes d'erreur
)

# Analyser les conditions pendant les vibrations
print(f"Vitesse vent moyenne pendant vibrations: {vibration_data['wind_speed'].mean():.2f} m/s")
```

#### C. Utiliser des timestamps ponctuels (au lieu de périodes)

Si vos logs ont un timestamp unique au lieu de start_date/end_date:

```python
# Log avec timestamp ponctuel
log_df = pd.DataFrame({
    'timestamp': [...],
    'operator_code': [...]
})

# Filtrage avec timestamp ponctuel
clean_data = manager.filter_by_codes(
    target_df=operation_df,
    log_df=log_df,
    code_column='operator_code',
    log_timestamp_col='timestamp',  # Utiliser timestamp unique
    target_timestamp_col='timestamp',
    criticality_filter=[CodeCriticality.CRITICAL],
    exclude_error_periods=True
)
```

#### D. Créer un masque directement pour un contrôle fin

```python
# Créer un masque booléen
mask = manager.create_time_mask(
    log_df=log_df,
    target_df=operation_df,
    code_column='operator_code',
    log_start_col='start_date',
    log_end_col='end_date',
    target_timestamp_col='timestamp',
    criticality_filter=[CodeCriticality.CRITICAL],
)

# mask[i] = True: période normale
# mask[i] = False: période d'erreur

# Utilisation du masque
normal_data = operation_df[mask]      # Données sans erreurs
error_data = operation_df[~mask]      # Données pendant erreurs

# Comparaisons
print(f"Puissance moyenne (normal): {normal_data['power'].mean():.2f} kW")
print(f"Puissance moyenne (erreur): {error_data['power'].mean():.2f} kW")
```

#### E. Filtrer avec une liste personnalisée de codes

```python
# Exclure des codes spécifiques
problematic_codes = ['FM104', 'FM105', 'FM120']

filtered_data = manager.filter_by_codes(
    target_df=operation_df,
    log_df=log_df,
    code_column='operator_code',
    log_start_col='start_date',
    log_end_col='end_date',
    target_timestamp_col='timestamp',
    codes_to_filter=problematic_codes,
    exclude_error_periods=True
)
```

#### F. Intégration avec TurbineLogMapping

```python
from src.wind_turbine_analytics.application.configuration.config_models import (
    TurbineLogMapping,
)

# Configuration du mapping (normalement depuis YAML)
log_mapping = TurbineLogMapping(
    start_date="start_date",  # Nom de la colonne
    end_date="end_date",
    oper="operator_code",
    status="status",
)

# Utilisation directe du mapping
clean_data = manager.filter_by_codes(
    target_df=operation_df,
    log_df=log_df,
    code_column=log_mapping.oper,          # Utilise la config
    log_start_col=log_mapping.start_date,  # Utilise la config
    log_end_col=log_mapping.end_date,      # Utilise la config
    target_timestamp_col='timestamp',
    criticality_filter=[CodeCriticality.CRITICAL],
    exclude_error_periods=True
)
```

#### G. Combinaison de filtres

```python
# Exclure plusieurs catégories en une fois
clean_data = manager.filter_by_codes(
    target_df=operation_df,
    log_df=log_df,
    code_column='operator_code',
    log_start_col='start_date',
    log_end_col='end_date',
    target_timestamp_col='timestamp',
    criticality_filter=[CodeCriticality.CRITICAL, CodeCriticality.HIGH],
    system_filter=[FunctionalSystem.SAFETY],
    exclude_error_periods=True
)
```

## Structure des Données

### Classe `ErrorCode`

Représente un code d'erreur avec toutes ses métadonnées:

```python
@dataclass
class ErrorCode:
    code: str                          # Code (ex: "FM104")
    description: str                   # Description du code
    reset_level: int                   # Niveau de réinitialisation
    dead_level: int                    # Niveau de désactivation
    availability: str                  # Impact sur disponibilité ("yes"/"no")
    reset_mode: str                    # Mode de reset (A/M/SL/SR)
    brake_program: Optional[str]       # Programme de frein
    yaw_program: Optional[str]         # Programme de lacet
    criticality: CodeCriticality       # Criticité classifiée
    functional_system: FunctionalSystem # Système fonctionnel
```

**Méthodes utiles:**

- `is_critical_stop()`: Retourne `True` si Dead Level ≥ 270
- `requires_manual_reset()`: Retourne `True` si reset mode = M/SL/M(A)
- `affects_availability()`: Retourne `True` si affecte la disponibilité

### Énumérations

#### `CodeCriticality`

```python
class CodeCriticality(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

#### `FunctionalSystem`

```python
class FunctionalSystem(Enum):
    PITCH = "pitch"
    GRID_CONVERTER = "grid_converter"
    ENVIRONMENT = "environment"
    ROTOR_BRAKE = "rotor_brake"
    SAFETY = "safety"
    GENERATOR = "generator"
    GEARBOX = "gearbox"
    VIBRATION = "vibration"
    SYSTEM = "system"
    OTHER = "other"
```

## Format des Fichiers Constructeur

Les fichiers CSV constructeur doivent avoir au minimum ces colonnes:

- **Code**: Identifiant du code (ex: "FM104")
- **Description**: Description textuelle
- **Reset Level**: Niveau de réinitialisation (entier)
- **Dead Level**: Niveau de désactivation (entier)
- **Availability**: Impact disponibilité ("yes"/"no")
- **Reset Mode**: Mode de reset (A/M/SL/SR/M(A))

Colonnes optionnelles:

- **Brake Program**: Programme de frein
- **Yaw Program**: Programme de lacet
- **StatCom**: Statut StatCom

## Extension à d'Autres Génératrices

Pour ajouter le support d'un nouveau type de génératrice:

### 1. Créer une Nouvelle Classe

```python
# src/wind_turbine_analytics/data_processing/log_code/generator_type/vestas_v90.py

from ..base_log_code import (
    BaseLogCodeManager,
    CodeCriticality,
    FunctionalSystem,
)


class VestasV90LogCodeManager(BaseLogCodeManager):
    """Gestionnaire pour éoliennes Vestas V90"""

    def _classify_codes(self) -> None:
        """Implémentation spécifique Vestas V90"""
        # Logique de classification
        pass

    def _determine_criticality(self, code: str, dead_level: int, reset_level: int) -> CodeCriticality:
        """Règles de criticité Vestas V90"""
        # Logique spécifique
        pass

    def _determine_functional_system(self, code: str, description: str) -> FunctionalSystem:
        """Identification des systèmes Vestas V90"""
        # Logique spécifique
        pass
```

### 2. Ajouter le Fichier CSV Constructeur

Placer le fichier dans `assets/VESTAS_V90_codes.csv` avec le format approprié.

### 3. Mettre à Jour les Imports

```python
# src/wind_turbine_analytics/data_processing/log_code/generator_type/__init__.py

from .nordex_n311_log_code_manager import NordexN311LogCodeManager
from .vestas_v90 import VestasV90LogCodeManager

__all__ = [
    "NordexN311LogCodeManager",
    "VestasV90LogCodeManager",
]
```

## Exemples Complets

Voir `examples/example_log_code_analysis.py` pour des exemples d'utilisation détaillés.

## Tests

Exécuter les tests unitaires:

```bash
pytest tests/unit/data_processing/log_code/test_nordex_n311_log_code_manager.py -v
```

## Notes Importantes

- Les codes avec Dead Level ≥ 270 sont **toujours** classés comme CRITICAL
- La classification par système utilise à la fois les plages de codes et les mots-clés
- Les occurrences élevées peuvent promouvoir un code de MEDIUM à HIGH
- Les codes inconnus (non documentés) sont signalés dans l'analyse
- La criticité peut être mise à jour dynamiquement selon les observations terrain

## Références

- Documentation NORDEX N311: `assets/NORDEX_codes.csv`
- Configuration turbine: `config_models.py` - `TurbineLogMapping`
