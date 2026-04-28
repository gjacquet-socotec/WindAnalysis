import pandas as pd
import re

def robust_date_parser(series):
    # 1. Nettoyage : s'assurer que les millisecondes à la fin sont précédées d'un point
    # Remplace ":" par "." uniquement s'il est suivi de 3 chiffres en fin de chaîne
    series = series.astype(str).str.replace(r":(\d{3})$", r".\1", regex=True)

    # 2. Détection intelligente :
    # Si la date commence par 4 chiffres (ex: 2024...), l'année est en premier
    # On teste sur la première valeur non nulle
    first_val = series.dropna().iloc[0] if not series.dropna().empty else ""

    is_year_first = False
    if len(first_val) >= 4 and first_val[:4].isdigit():
        is_year_first = True

    # 3. Conversion
    return pd.to_datetime(
        series,
        dayfirst=not is_year_first,  # False si l'année est en premier
        yearfirst=is_year_first,
        format="mixed",  # Pour Pandas 2.0+
        errors="coerce",
    )


def to_smart_timestamp(date_val:str) -> pd.Timestamp:
    """
    Convertit une chaîne de caractères unique en pd.Timestamp
    en gérant intelligemment le format (ISO vs Européen).
    """
    if pd.isna(date_val) or date_val == "":
        return pd.NaT

    # 1. Conversion en string et nettoyage des espaces
    date_str = str(date_val).strip()

    # 2. Correction du format des millisecondes (:450 -> .450)
    # On cherche ":" suivi de 3 chiffres à la toute fin de la chaîne
    date_str = re.sub(r":(\d{3})$", r".\1", date_str)

    # 3. Détection : Année en premier (2025-...) ou Jour en premier (03-...)
    # On regarde si les 4 premiers caractères sont des chiffres
    is_year_first = False
    first_four = date_str[:4]
    if len(first_four) == 4 and first_four.isdigit():
        is_year_first = True

    # 4. Conversion finale
    return pd.to_datetime(
        date_str,
        dayfirst=not is_year_first,  # True si l'année n'est pas en premier
        yearfirst=is_year_first,
        errors="coerce",
    )


def smart_date_converter(df: pd.DataFrame, column: str) -> pd.Series:
    # 1. On nettoie les espaces et on s'assure que c'est du texte
    s = df[column].astype(str).str.strip()

    # 2. On répare le problème des millisecondes (remplacer le dernier ":" par ".")
    s = s.str.replace(r":(\d{3})$", r".\1", regex=True)

    # 3. DETECTION LOGIQUE :
    # On regarde la première valeur non vide
    sample = s.dropna().iloc[0] if not s.dropna().empty else ""

    # Si la date commence par 4 chiffres (ex: 2025...), c'est du format ISO (Année en premier)
    if len(sample) >= 4 and sample[:4].isdigit():
        return pd.to_datetime(s, dayfirst=False, errors="coerce")

    # Sinon, on considère que c'est du format européen (Jour en premier)
    else:
        return pd.to_datetime(s, dayfirst=True, errors="coerce")
