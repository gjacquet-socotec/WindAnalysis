"""
Tests unitaires pour la fonction load_csv avec gestion des formats complexes.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import tempfile
from src.wind_turbine_analytics.application.utils.load_data import (
    load_csv,
    CSVLoadError,
    _detect_header_row,
    _clean_header_names,
    _merge_date_time_columns,
)


class TestHeaderDetection:
    """Tests pour la détection d'en-tête"""

    def test_detect_header_in_first_row(self):
        """Test détection d'en-tête en première ligne"""
        df = pd.DataFrame({
            'col1': ['index', 1, 2, 3],
            'col2': ['date', '01.01.2024', '02.01.2024', '03.01.2024'],
            'col3': ['time', '10:00:00', '11:00:00', '12:00:00'],
        })

        header_row = _detect_header_row(df)
        assert header_row == 0

    def test_detect_header_in_second_row(self):
        """Test détection d'en-tête en deuxième ligne"""
        df = pd.DataFrame({
            'col1': ['Title', 'index', 1, 2, 3],
            'col2': ['Report', 'date', '01.01', '02.01', '03.01'],
            'col3': ['Data', 'time', '10:00', '11:00', '12:00'],
        })

        header_row = _detect_header_row(df)
        assert header_row == 1

    def test_no_header_detected(self):
        """Test quand aucun en-tête n'est détecté"""
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4],
            'col2': [5, 6, 7, 8],
            'col3': [9, 10, 11, 12],
        })

        header_row = _detect_header_row(df)
        assert header_row is None


class TestHeaderCleaning:
    """Tests pour le nettoyage des en-têtes"""

    def test_clean_unnamed_columns(self):
        """Test nettoyage des colonnes Unnamed"""
        df = pd.DataFrame({
            'Alarm Log;01WEA95986;Generated 06.02.2026 13:19:29': [
                'index', '1', '2'
            ],
            'Unnamed: 1': ['date', '03.02.2026', '02.02.2026'],
            'Unnamed: 2': ['time', '12:46:01', '11:56:23'],
            'Unnamed: 3': ['oper', '14885', '0'],
        })

        df_cleaned = _clean_header_names(df)

        # Vérifier que les colonnes ont été nettoyées
        assert 'index' in df_cleaned.columns
        assert 'date' in df_cleaned.columns
        assert 'time' in df_cleaned.columns
        assert 'oper' in df_cleaned.columns


class TestDateTimeMerge:
    """Tests pour la fusion date/time"""

    def test_merge_date_time_columns(self):
        """Test fusion des colonnes date et time"""
        df = pd.DataFrame({
            'index': [1, 2, 3],
            'date': ['01.01.2024', '02.01.2024', '03.01.2024'],
            'time': ['10:00:00', '11:00:00', '12:00:00'],
            'oper': [100, 200, 300],
        })

        df_merged = _merge_date_time_columns(df)

        # Vérifier que timestamp a été créé
        assert 'timestamp' in df_merged.columns

        # Vérifier que date et time ont été supprimées
        assert 'date' not in df_merged.columns
        assert 'time' not in df_merged.columns

        # Vérifier le contenu
        assert '01.01.2024 10:00:00' in df_merged['timestamp'].values

    def test_no_merge_when_timestamp_exists(self):
        """Test pas de fusion si timestamp existe déjà"""
        df = pd.DataFrame({
            'index': [1, 2, 3],
            'timestamp': ['2024-01-01 10:00:00', '2024-01-02', '2024-01-03'],
            'oper': [100, 200, 300],
        })

        df_result = _merge_date_time_columns(df)

        # Ne devrait rien changer
        assert 'timestamp' in df_result.columns
        assert len(df_result.columns) == 3

    def test_no_merge_when_only_date(self):
        """Test pas de fusion si seulement date présente"""
        df = pd.DataFrame({
            'index': [1, 2, 3],
            'date': ['01.01.2024', '02.01.2024', '03.01.2024'],
            'oper': [100, 200, 300],
        })

        df_result = _merge_date_time_columns(df)

        # Ne devrait rien changer
        assert 'date' in df_result.columns
        assert 'timestamp' not in df_result.columns


class TestLoadCSVIntegration:
    """Tests d'intégration pour load_csv"""

    def test_load_csv_with_header_on_second_line(self):
        """Test chargement CSV avec en-tête en 2ème ligne"""
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv', encoding='utf-8'
        ) as f:
            f.write('Alarm Log;Generated 06.02.2026;Extra;Info;Data;Report\n')
            f.write('index;date;time;oper;name;message\n')
            f.write('1;03.02.2026;12:46:01;14885;FM0;WTG System ok\n')
            f.write('2;02.02.2026;11:56:23;0;FE400;Wind Dir Stop\n')
            temp_path = f.name

        try:
            df = load_csv(temp_path)

            # Vérifier que les colonnes importantes sont présentes
            columns_lower = [c.lower() for c in df.columns]

            # Au moins 'oper' et 'name' doivent être présents
            assert any('oper' in c for c in columns_lower)
            assert any('name' in c for c in columns_lower)

            # Vérifier qu'on a bien les données (au moins 2 lignes)
            assert len(df) >= 2

        finally:
            Path(temp_path).unlink()

    def test_load_csv_with_date_time_merge(self):
        """Test chargement CSV avec fusion date/time"""
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv', encoding='utf-8'
        ) as f:
            f.write('index;date;time;oper;name\n')
            f.write('1;03.02.2026;12:46:01;14885;FM0\n')
            f.write('2;02.02.2026;11:56:23;0;FE400\n')
            temp_path = f.name

        try:
            df = load_csv(temp_path)

            # Vérifier que timestamp a été créé
            assert 'timestamp' in df.columns

            # Vérifier que date et time ont disparu
            assert 'date' not in df.columns
            assert 'time' not in df.columns

        finally:
            Path(temp_path).unlink()

    def test_load_csv_file_not_found(self):
        """Test erreur si fichier inexistant"""
        with pytest.raises(CSVLoadError, match="Fichier introuvable"):
            load_csv("nonexistent_file.csv")

    def test_load_csv_empty_file(self):
        """Test erreur si fichier vide"""
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv'
        ) as f:
            temp_path = f.name

        try:
            with pytest.raises(CSVLoadError, match="Fichier vide"):
                load_csv(temp_path)
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
