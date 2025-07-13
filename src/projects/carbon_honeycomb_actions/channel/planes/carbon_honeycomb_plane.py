from dataclasses import dataclass
from functools import cached_property
import numpy as np

from src.interfaces import ICarbonHoneycombPlane
from src.entities import FlatFigure

from .carbon_honeycomb_plane_actions import CarbonHoneycombPlaneActions
from .plane_polygons import CarbonHoneycombPentagon, CarbonHoneycombHexagon


@dataclass(frozen=True)
class CarbonHoneycombPlane(FlatFigure, ICarbonHoneycombPlane):
    @cached_property
    def pentagons(self) -> list[CarbonHoneycombPentagon]:
        """ List of the plane pentagons. """
        return list(CarbonHoneycombPlaneActions.define_plane_pentagons(self.points))

    @cached_property
    def hexagons(self) -> list[CarbonHoneycombHexagon]:
        """ List of the plane hexagons. """
        return list(CarbonHoneycombPlaneActions.define_plane_hexagons(self.points))

    @cached_property
    def edge_holes(self) -> np.ndarray:
        """
        Calculate the hole coordinates in the plane edges
        (points between polygon edges).
        """
        return CarbonHoneycombPlaneActions.calculate_edge_holes(self.points, self.coordinate_limits)

    def get_direction_to_center(self, channel_center: np.ndarray) -> bool:
        """ Get the direction to the center of the plane (e.g., to filter atoms). """
        return bool(self.center[1] <= channel_center[1])
