"""
Présentateur Word spécifique au workflow SCADA.

Utilise une stratégie de remplissage des tableaux par marqueurs invisibles.
Le template contient des marqueurs [TABLE:xxx] avant chaque tableau.
"""

from typing import Dict, Any, List
from docx import Document
from docx.table import Table
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re
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

    def _set_table_borders(self, table):
        """Force l'affichage des bordures noires sur tout le tableau."""
        tbl = table._element
        tblPr = tbl.xpath("w:tblPr")[0]

        # Création de l'élément de bordures
        tblBorders = OxmlElement("w:tblBorders")

        # Définition des types de bordures (top, left, bottom, right, insideH, insideV)
        for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            border = OxmlElement(f"w:{border_name}")
            border.set(qn("w:val"), "single")  # Ligne simple
            border.set(qn("w:sz"), "4")  # Épaisseur (1/8 pt)
            border.set(qn("w:space"), "0")
            border.set(qn("w:color"), "000000")  # Noir
            tblBorders.append(border)

        tblPr.append(tblBorders)

    def _process_tables(self, doc: Document, context: Dict[str, Any]) -> None:
        logger.info("Replacing markers with dynamic tables...")

        table_regex = re.compile(r"\[TABLE:\s*(.*?)\s*\]", re.IGNORECASE)

        # On parcourt les paragraphes du document
        for para in list(
            doc.paragraphs
        ):  # On utilise list() pour pouvoir modifier le doc en bouclant
            match = table_regex.search(para.text)

            if match:
                tag_content = match.group(1).strip().upper()
                logger.info(f"Marker found: {tag_content}")

                # Chercher les données
                data = None
                for k, v in context.items():
                    if k.strip().upper() == tag_content:
                        data = v
                        break

                if data and isinstance(data, list) and len(data) > 0:
                    # 1. Créer le tableau à l'endroit du paragraphe
                    new_table = self._insert_table_at_paragraph(doc, para, data)

                    # 2. Remplir le tableau
                    self._populate_table_dynamically(new_table, data)

                    # 3. Supprimer le paragraphe qui contenait le tag [TABLE:XXX]
                    self._remove_paragraph(para)

                    logger.info(
                        f"✅ Table '{tag_content}' created and replaced marker."
                    )
                else:
                    logger.warning(
                        f"⚠️ No data or empty list for '{tag_content}'. Marker left as is."
                    )

    def _insert_table_at_paragraph(
        self, doc: Document, para, data: List[Dict[str, Any]]
    ) -> Table:
        num_cols = len(data[0].keys())
        num_rows = 1

        table = doc.add_table(rows=num_rows, cols=num_cols)

        # On applique nos bordures manuelles au lieu du style qui plante
        self._set_table_borders(table)

        # Déplacer le tableau après le marqueur
        para._element.addnext(table._element)
        return table

    def _remove_paragraph(self, paragraph):
        """Supprime proprement un paragraphe du document."""
        p = paragraph._element
        p.getparent().remove(p)

    def _populate_table_dynamically(
        self, table: Table, data: List[Dict[str, Any]]
    ) -> None:
        """
        Remplit le tableau fraîchement créé.
        """
        headers = list(data[0].keys())

        # 1. Remplir et formater le Header (Ligne 0)
        for i, header_text in enumerate(headers):
            cell = table.cell(0, i)
            cell.text = str(header_text)
            # Mettre le texte en gras pour que ça ressemble à un vrai header
            paragraph = cell.paragraphs[0]
            run = paragraph.runs[0]
            run.font.bold = True

        # 2. Remplir les données
        for row_dict in data:
            new_row = table.add_row()
            for col_idx, header_name in enumerate(headers):
                val = row_dict.get(header_name, "")
                # Formatage des nombres
                text_val = f"{val:.2f}" if isinstance(val, float) else str(val)
                new_row.cells[col_idx].text = text_val
