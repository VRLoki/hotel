"""Data collectors package."""

from .opera import OperaCollector
from .spa import SpaCollector
from .fb import FBCollector
from .incidents import IncidentsCollector
from .concierge import ConciergeCollector
from .villas import VillasCollector
from .m365 import M365Collector

ALL_COLLECTORS = [
    OperaCollector,
    SpaCollector,
    FBCollector,
    IncidentsCollector,
    ConciergeCollector,
    VillasCollector,
    M365Collector,
]

__all__ = [
    "OperaCollector", "SpaCollector", "FBCollector",
    "IncidentsCollector", "ConciergeCollector", "VillasCollector",
    "M365Collector", "ALL_COLLECTORS",
]
