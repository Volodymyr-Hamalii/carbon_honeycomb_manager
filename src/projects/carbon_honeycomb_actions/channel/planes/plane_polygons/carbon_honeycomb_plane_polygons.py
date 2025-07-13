import numpy as np
from dataclasses import dataclass

from src.interfaces import IFlatFigure, ICarbonHoneycombHexagon, ICarbonHoneycombPentagon


@dataclass(frozen=True)
class CarbonHoneycombPolygon(IFlatFigure):
    pass


@dataclass(frozen=True)
class CarbonHoneycombHexagon(ICarbonHoneycombHexagon, CarbonHoneycombPolygon):
    pass


@dataclass(frozen=True)
class CarbonHoneycombPentagon(ICarbonHoneycombPentagon, CarbonHoneycombPolygon):
    pass
