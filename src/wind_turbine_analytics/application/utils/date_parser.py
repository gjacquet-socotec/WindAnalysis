import pandas as pd


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
