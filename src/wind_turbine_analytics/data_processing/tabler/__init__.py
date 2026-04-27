"""
Module de génération de tableaux pour rapports Word.

Ce module fournit une architecture modulaire pour générer des tableaux
à partir des résultats d'analyse, en suivant le pattern Template Method.
"""

from src.wind_turbine_analytics.data_processing.tabler.base_tabler import BaseTabler

__all__ = ["BaseTabler"]
