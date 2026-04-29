"""SCADA report tables."""

from .table_eba_cut_in_cut_out import EbaCutInCutOutTabler
from .table_eba_manifacturer import EbaManufacturerTabler
from .table_eba_loss import EbaLossTabler
from .table_scada_summary import ScadaSummaryTabler

__all__ = [
    "EbaCutInCutOutTabler",
    "EbaManufacturerTabler",
    "EbaLossTabler",
    "ScadaSummaryTabler",
]
