"""
Présentateur Word spécifique au workflow SCADA.

Utilise une stratégie de remplissage des tableaux par marqueurs invisibles.
Le template contient des marqueurs [TABLE:xxx] avant chaque tableau.
"""

from typing import Dict, Any, List
from docx import Document
from .word_presenter import WordPresenter
from src.logger_config import get_logger

logger = get_logger(__name__)


class ScadaWordPresenter(WordPresenter):
    """
    Présentateur Word pour les rapports SCADA.

    Stratégie de remplissage des tableaux:
    - Template contient des marqueurs invisibles [TABLE:xxx] avant chaque tableau
    - On cherche chaque marqueur et on trouve le tableau qui suit
    - Remplissage dynamique basé sur le nom du marqueur
    - Ordre flexible, nombre de tables variable
    - Supporte l'ajout/suppression de tables sans changer le code

    Marqueurs attendus dans le template SCADA:
    - [TABLE:CSV_FILES_TABLE]
    - [TABLE:SCADA_SUMMARY_TABLE]
    - [TABLE:EBA_CUT_IN_CUT_OUT_TABLE]
    - [TABLE:EBA_MANUFACTURER_TABLE]
    - [TABLE:EBA_LOSS_TABLE]
    - [TABLE:ERROR_CODES_TABLE]
    - [TABLE:DATA_AVAILABILITY_TABLE]
    - [TABLE:WIND_CALIBRATION_TABLE]
    - [TABLE:TIP_SPEED_RATIO_TABLE]
    - [TABLE:NORMATIVE_YIELD_TABLE]
    """

    def _process_tables(self, doc: Document, context: Dict[str, Any]) -> None:
        logger.info("Filling tables using SCADA marker-based strategy...")

        # On fait une copie de la liste des paragraphes pour pouvoir les manipuler
        for para_idx, para in enumerate(doc.paragraphs):
            clean_text = para.text.strip().upper()

            if clean_text.startswith("[TABLE:") and clean_text.endswith("]"):
                # On extrait le nom sans les crochets et sans le préfixe
                table_key = clean_text[7:-1].strip()
                logger.info(f"Marker found: {table_key}")

                table = self._find_next_table(doc, para_idx)

                # On cherche dans le contexte (en ignorant la casse)
                data = None
                for k, v in context.items():
                    if k.upper() == table_key:
                        data = v
                        break

                if table and data is not None:
                    if isinstance(data, list) and len(data) > 0:
                        self._populate_table_dynamically(table, data)
                        # SUPPRIMER LE MARQUEUR DU DOCUMENT
                        para.text = ""
                        logger.info(f"✅ Table '{table_key}' filled")
                    else:
                        logger.warning(f"⚠️ Empty data for '{table_key}'")
                else:
                    logger.warning(f"⚠️ Table or Data missing for '{table_key}'")

    def _find_next_table(self, doc: Document, para_idx: int):
        """
        Trouve la première table après le paragraphe marqueur.

        Utilise l'arbre XML du document pour parcourir les éléments.

        Args:
            doc: Document Word
            para_idx: Index du paragraphe marqueur

        Returns:
            Le tableau suivant ou None si non trouvé
        """
        # Parcourir les éléments après le paragraphe
        para_element = doc.paragraphs[para_idx]._element
        next_element = para_element.getnext()

        while next_element is not None:
            # Si c'est un tableau (<w:tbl> en XML)
            if next_element.tag.endswith("tbl"):
                # Trouver l'objet Table correspondant
                for table in doc.tables:
                    if table._element == next_element:
                        return table
            next_element = next_element.getnext()

        return None

    def _populate_table_dynamically(self, table, data: List[Dict[str, Any]]) -> None:
        """
        Remplit une table en ajustant dynamiquement le nombre de colonnes et de lignes.
        """
        if not data:
            return

        # 1. Récupérer les headers (clés du premier dictionnaire)
        headers = list(data[0].keys())
        num_cols_needed = len(headers)

        # 2. Ajuster le nombre de colonnes du header si nécessaire
        current_cols = len(table.columns)
        while len(table.columns) < num_cols_needed:
            table.add_column(
                table.columns[0].width
            )  # Ajoute une colonne avec la même largeur

        # 3. Mettre à jour les textes des headers (première ligne)
        for i, header_text in enumerate(headers):
            table.cell(0, i).text = str(header_text)
            # Optionnel : mettre en gras (nécessite d'accéder aux runs)
            # table.cell(0, i).paragraphs[0].runs[0].font.bold = True

        # 4. Supprimer les lignes de données existantes (sauf le header)
        while len(table.rows) > 1:
            table._element.remove(table.rows[-1]._element)

        # 5. Ajouter les nouvelles lignes de données
        for row_dict in data:
            new_row = table.add_row()
            # On parcourt les headers pour garantir que la donnée va dans la bonne colonne
            for col_idx, header_name in enumerate(headers):
                val = row_dict.get(header_name, "")
                # Formatage spécial si c'est un float (pour les pourcentages)
                if isinstance(val, float):
                    new_row.cells[col_idx].text = f"{val:.2f}"
                else:
                    new_row.cells[col_idx].text = str(val)
