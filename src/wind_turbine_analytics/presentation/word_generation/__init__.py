"""
Module de génération de rapports Word.

Contient les classes pour générer des rapports Word dynamiques pour différents workflows.
"""

from .word_presenter import WordPresenter
from .runtest_word_presenter import RunTestWordPresenter
from .scada_word_presenter import ScadaWordPresenter

__all__ = [
    "WordPresenter",
    "RunTestWordPresenter",
    "ScadaWordPresenter",
]
