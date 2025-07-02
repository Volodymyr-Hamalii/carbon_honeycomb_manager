import numpy as np
from dataclasses import dataclass

from src_1.base_structure_classes import FlatFigure

from .carbon_honeycomb_plane_polygon_actions import CarbonHoneycombPolygonActions


@dataclass(frozen=True)
class CarbonHoneycombPolygon(FlatFigure):
    pass


@dataclass(frozen=True)
class CarbonHoneycombHexagon(CarbonHoneycombPolygon):
    pass


@dataclass(frozen=True)
class CarbonHoneycombPentagon(CarbonHoneycombPolygon):
    pass
