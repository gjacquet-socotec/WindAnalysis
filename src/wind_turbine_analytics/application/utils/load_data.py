import pandas as pd
from pathlib import Path
from typing import Optional, Union, List
from src.logger_config import get_logger

logger = get_logger(__name__)


class CSVLoadError(Exception):
    """Exception levée lors d'erreurs de chargement CSV."""
    pass


def load_csv(
    file_path: Union[str, Path],
    sep: Optional[str] = None,
    encoding: Optional[str] = None,
    decimal: str = '.',
    parse_dates: Optional[List[str]] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Charge un fichier CSV avec gestion robuste des différents formats.

    Args:
        file_path: Chemin vers le fichier CSV
        sep: Séparateur de colonnes (auto-détecté si None)
        encoding: Encodage du fichier (auto-détecté si None)
        decimal: Séparateur décimal ('.' ou ',')
        parse_dates: Liste des colonnes à parser en dates
        **kwargs: Arguments supplémentaires pour pd.read_csv

    Returns:
        DataFrame pandas avec les données chargées

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
    encodings = [encoding] if encoding else ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']

    # Séparateurs à tester
    separators = [sep] if sep else [',', ';', '\t', '|']

    errors = []

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

                # Vérifier qu'il y a au moins 2 colonnes (sinon mauvais séparateur)
                if len(df.columns) < 2 and len(separators) > 1:
                    continue

                logger.info(
                    f"Fichier chargé avec succès: {file_path.name} "
                    f"(encoding={enc}, sep='{sep_char}', shape={df.shape})"
                )

                return df

            except Exception as e:
                errors.append(f"Tentative (encoding={enc}, sep='{sep_char}'): {str(e)}")
                continue

    # Si aucune combinaison n'a fonctionné
    error_msg = f"Impossible de charger {file_path}. Tentatives:\n" + "\n".join(errors)
    raise CSVLoadError(error_msg)
