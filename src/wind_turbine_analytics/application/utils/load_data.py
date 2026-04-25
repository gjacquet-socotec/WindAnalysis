import pandas as pd
from pathlib import Path
from typing import Optional, Union, List
from src.logger_config import get_logger

logger = get_logger(__name__)


class CSVLoadError(Exception):
    """Exception levée lors d'erreurs de chargement CSV."""
    pass


def _detect_header_row(df: pd.DataFrame) -> Optional[int]:
    """
    Détecte la ligne d'en-tête réelle dans le DataFrame.

    Cherche une ligne contenant des noms de colonnes typiques
    comme 'index', 'date', 'time', 'oper', 'name', etc.

    Args:
        df: DataFrame brut

    Returns:
        Index de la ligne d'en-tête, ou None si non détecté
    """
    # Mots-clés typiques dans les en-têtes de fichiers logs
    header_keywords = [
        'index', 'date', 'time', 'oper', 'name',
        'message', 'group', 'status', 'timestamp'
    ]

    # Vérifier les 10 premières lignes
    for idx in range(min(10, len(df))):
        row_values = df.iloc[idx].astype(str).str.lower()

        # Compter combien de mots-clés sont présents
        matches = sum(
            any(keyword in str(val).lower() for keyword in header_keywords)
            for val in row_values
        )

        # Si au moins 3 mots-clés correspondent, c'est probablement l'en-tête
        if matches >= 3:
            logger.info(f"En-tête détecté à la ligne {idx}")
            return idx

    return None


def _clean_header_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie les noms de colonnes en supprimant les 'Unnamed' et espaces.

    Args:
        df: DataFrame avec colonnes potentiellement mal nommées

    Returns:
        DataFrame avec colonnes nettoyées
    """
    # Remplacer les colonnes 'Unnamed: X' par des noms vides temporairement
    new_columns = []
    for col in df.columns:
        if 'unnamed' in str(col).lower():
            new_columns.append('')
        else:
            new_columns.append(str(col).strip())

    df.columns = new_columns

    # Si la première ligne contient les vrais noms, les utiliser
    if df.iloc[0].notna().all() and not df.iloc[0].astype(str).str.isdigit().any():  # noqa: E501
        # La première ligne semble être un en-tête
        potential_header = df.iloc[0].astype(str).str.strip()

        # Vérifier si ces noms ont du sens
        valid_names = [
            name for name in potential_header
            if name and name.lower() not in ['nan', '']
        ]

        if len(valid_names) >= len(df.columns) * 0.5:
            # Utiliser la première ligne comme en-tête
            df.columns = potential_header
            df = df.iloc[1:].reset_index(drop=True)
            logger.info("En-tête extrait de la première ligne de données")

    return df


def _merge_date_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fusionne les colonnes 'date' et 'time' en une seule colonne 'timestamp'.

    Args:
        df: DataFrame avec colonnes date et time séparées

    Returns:
        DataFrame avec colonne timestamp fusionnée
    """
    # Normaliser les noms de colonnes (lowercase)
    col_map = {col: col.lower().strip() for col in df.columns}
    df_temp = df.rename(columns=col_map)

    # Vérifier si date et time existent séparément
    has_date = 'date' in df_temp.columns
    has_time = 'time' in df_temp.columns
    has_timestamp = 'timestamp' in df_temp.columns

    if has_date and has_time and not has_timestamp:
        logger.info("Fusion des colonnes 'date' et 'time' en 'timestamp'")

        # Fusionner date et time
        df_temp['timestamp'] = (
            df_temp['date'].astype(str) + ' ' + df_temp['time'].astype(str)
        )

        # Restaurer les noms de colonnes originaux (sauf date/time)
        reverse_map = {v: k for k, v in col_map.items()}
        rename_dict = {}
        for col in df_temp.columns:
            if col in reverse_map:
                if col not in ['date', 'time']:
                    rename_dict[col] = reverse_map[col]
            else:
                # timestamp est nouveau, garder en minuscule
                rename_dict[col] = col

        df_temp = df_temp.rename(columns=rename_dict)

        # Supprimer les colonnes date et time originales
        date_col = col_map.get('date', 'date')
        time_col = col_map.get('time', 'time')
        cols_to_drop = [c for c in df_temp.columns if c in [date_col, time_col]]  # noqa: E501
        if cols_to_drop:
            df_temp = df_temp.drop(columns=cols_to_drop)

        return df_temp

    # Restaurer les noms originaux si pas de fusion
    reverse_map = {v: k for k, v in col_map.items()}
    df_temp = df_temp.rename(columns=reverse_map)

    return df_temp


def load_csv(
    file_path: Union[str, Path],
    sep: Optional[str] = None,
    encoding: Optional[str] = None,
    decimal: str = '.',
    parse_dates: Optional[List[str]] = None,
    skip_header_detection: bool = False,
    **kwargs
) -> pd.DataFrame:
    """
    Charge un fichier CSV avec gestion robuste des différents formats.

    Gère automatiquement :
    - Détection d'en-têtes sur plusieurs lignes
    - Nettoyage des colonnes 'Unnamed'
    - Fusion des colonnes date/time en timestamp

    Args:
        file_path: Chemin vers le fichier CSV
        sep: Séparateur de colonnes (auto-détecté si None)
        encoding: Encodage du fichier (auto-détecté si None)
        decimal: Séparateur décimal ('.' ou ',')
        parse_dates: Liste des colonnes à parser en dates
        skip_header_detection: Skip automatic header detection
        **kwargs: Arguments supplémentaires pour pd.read_csv

    Returns:
        DataFrame pandas avec les données chargées et nettoyées

    Raises:
        CSVLoadError: Si le fichier ne peut pas être chargé
    """
    file_path = Path(file_path)

    # Vérifier l'existence du fichier
    if not file_path.exists():
        raise CSVLoadError(f"Fichier introuvable: {file_path}")

    if not file_path.is_file():
        raise CSVLoadError(f"Le chemin n'est pas un fichier: {file_path}")

    # Vérifier que le fichier n'est pas vide
    if file_path.stat().st_size == 0:
        raise CSVLoadError(f"Fichier vide: {file_path}")

    # Encodages à tester
    encodings = [encoding] if encoding else [
        'utf-8', 'latin1', 'cp1252', 'iso-8859-1'
    ]

    # Séparateurs à tester
    separators = [sep] if sep else [',', ';', '\t', '|']

    errors = []
    df = None

    for enc in encodings:
        for sep_char in separators:
            try:
                df = pd.read_csv(
                    file_path,
                    sep=sep_char,
                    encoding=enc,
                    decimal=decimal,
                    parse_dates=parse_dates,
                    **kwargs
                )

                # Vérifier que le DataFrame n'est pas vide
                if df.empty:
                    raise ValueError("DataFrame vide après chargement")

                # Vérifier qu'il y a au moins 2 colonnes
                if len(df.columns) < 2 and len(separators) > 1:
                    continue

                logger.info(
                    f"Fichier chargé: {file_path.name} "
                    f"(encoding={enc}, sep='{sep_char}', shape={df.shape})"
                )

                # Détecter et corriger la structure si nécessaire
                if not skip_header_detection:
                    # Détecter si l'en-tête est sur une autre ligne
                    header_row = _detect_header_row(df)
                    if header_row is not None and header_row > 0:
                        # Recharger avec le bon header
                        df = pd.read_csv(
                            file_path,
                            sep=sep_char,
                            encoding=enc,
                            decimal=decimal,
                            header=header_row,
                            **kwargs
                        )
                        logger.info(f"Fichier rechargé avec header={header_row}")

                    # Nettoyer les noms de colonnes
                    df = _clean_header_names(df)

                    # Fusionner date/time si nécessaire
                    df = _merge_date_time_columns(df)

                logger.info(
                    f"DataFrame final: shape={df.shape}, "
                    f"columns={list(df.columns)}"
                )

                return df

            except Exception as e:
                errors.append(
                    f"Tentative (encoding={enc}, sep='{sep_char}'): {str(e)}"
                )
                continue

    # Si aucune combinaison n'a fonctionné
    error_msg = (
        f"Impossible de charger {file_path}. Tentatives:\n"
        + "\n".join(errors)
    )
    raise CSVLoadError(error_msg)
