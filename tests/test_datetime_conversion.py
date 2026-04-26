"""Test unitaire pour la conversion des dates."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest  # noqa: E402
import pandas as pd  # noqa: E402
from datetime import datetime  # noqa: E402


class TestDateTimeConversion:
    """Test de la conversion des dates pour éviter les problèmes."""

    def test_datetime_conversion_with_string_dates(self):
        """Test que les dates string sont correctement converties."""
        # Dates au format string (comme dans les YAML)
        test_start_str = "2024-01-01 00:00:00"
        test_end_str = "2024-01-03 00:00:00"  # 2 jours plus tard

        # Conversion comme dans le code
        test_start = pd.to_datetime(test_start_str).tz_localize(None)
        test_end = pd.to_datetime(test_end_str).tz_localize(None)

        # Vérifier la différence
        diff = test_end - test_start
        assert diff == pd.Timedelta(days=2), f"Expected 2 days, got {diff}"

    def test_datetime_conversion_with_datetime_objects(self):
        """Test que les objets datetime sont correctement convertis."""
        # Dates au format datetime
        test_start_dt = datetime(2024, 1, 1, 0, 0, 0)
        test_end_dt = datetime(2024, 1, 3, 0, 0, 0)  # 2 jours plus tard

        # Conversion comme dans le code
        test_start = pd.to_datetime(test_start_dt).tz_localize(None)
        test_end = pd.to_datetime(test_end_dt).tz_localize(None)

        # Vérifier la différence
        diff = test_end - test_start
        assert diff == pd.Timedelta(days=2), f"Expected 2 days, got {diff}"

    def test_datetime_comparison_with_dataframe(self):
        """Test que les comparaisons avec un DataFrame fonctionnent."""
        # Créer un DataFrame avec des timestamps
        timestamps = pd.date_range("2024-01-01", "2024-01-05", freq="1h")
        df = pd.DataFrame({
            "timestamp": timestamps,
            "value": range(len(timestamps))
        })

        # Dates de test
        test_start_str = "2024-01-02 00:00:00"
        test_end_str = "2024-01-04 00:00:00"

        # Conversion
        test_start = pd.to_datetime(test_start_str).tz_localize(None)
        test_end = pd.to_datetime(test_end_str).tz_localize(None)

        # S'assurer que le DataFrame n'a pas de timezone
        if df["timestamp"].dt.tz is not None:
            df["timestamp"] = df["timestamp"].dt.tz_localize(None)

        # Filtrage
        mask = (
            (df["timestamp"] >= test_start) &
            (df["timestamp"] <= test_end)
        )
        df_filtered = df[mask]

        # Vérifications
        assert len(df_filtered) > 0
        assert df_filtered["timestamp"].min() >= test_start
        assert df_filtered["timestamp"].max() <= test_end

    def test_problematic_case_120_days(self):
        """
        Test du cas problématique rapporté par l'utilisateur.
        Si test_end - test_start = 120 jours, les dates sont incorrectes.
        """
        # Simuler le cas problématique
        test_start_str = "2024-01-01 00:00:00"
        test_end_str = "2024-04-30 23:50:00"  # ~120 jours plus tard

        test_start = pd.to_datetime(test_start_str).tz_localize(None)
        test_end = pd.to_datetime(test_end_str).tz_localize(None)

        diff = test_end - test_start
        days = diff.days
        hours = diff.seconds / 3600

        print(f"\nCas problematique - Difference: {diff}")
        print(f"   - Jours: {days}")
        print(f"   - Heures supplementaires: {hours:.2f}")
        print(f"   - Total heures: {diff.total_seconds() / 3600:.2f}")

        # Vérifier que la conversion fonctionne (même si résultat inattendu)
        assert days == 120, "Ce test confirme le cas de 120 jours"

    def test_expected_case_2_days(self):
        """Test du cas attendu : 2 jours de différence."""
        # Ce que l'utilisateur s'attend à avoir
        test_start_str = "2024-01-01 00:00:00"
        test_end_str = "2024-01-03 00:00:00"  # Exactement 2 jours

        test_start = pd.to_datetime(test_start_str).tz_localize(None)
        test_end = pd.to_datetime(test_end_str).tz_localize(None)

        diff = test_end - test_start
        days = diff.days

        print(f"\nCas attendu - Difference: {diff}")
        print(f"   - Jours: {days}")

        assert days == 2, f"Expected 2 days, got {days}"


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v", "-s"])
