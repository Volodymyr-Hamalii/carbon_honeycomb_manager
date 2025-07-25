from dataclasses import dataclass
from src.interfaces import ICarbonHoneycombHexagon, ICarbonHoneycombPentagon
from src.entities import FlatFigure


@dataclass(frozen=True)
class CarbonHoneycombPolygon(FlatFigure):
    """Base class for carbon honeycomb polygons."""
    pass


@dataclass(frozen=True)
class CarbonHoneycombHexagon(CarbonHoneycombPolygon, ICarbonHoneycombHexagon):
    """Carbon honeycomb hexagon implementation."""
    pass


@dataclass(frozen=True)
class CarbonHoneycombPentagon(CarbonHoneycombPolygon, ICarbonHoneycombPentagon):
    """Carbon honeycomb pentagon implementation."""
    pass
