from abc import ABC, abstractmethod
from typing import Type, Sequence
import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.params.p_coordinate_limits import PCoordinateLimits
from .plane_polygons import ICarbonHoneycombPolygon, ICarbonHoneycombPentagon, ICarbonHoneycombHexagon


class ICarbonHoneycombPlaneActions(ABC):
    """Interface for carbon honeycomb plane actions."""

    @classmethod
    @abstractmethod
    def define_plane_pentagons(
            cls,
            points: NDArray[np.float64],
    ) -> Sequence[ICarbonHoneycombPentagon]:
        ...

    @classmethod
    @abstractmethod
    def define_plane_hexagons(
            cls,
            points: NDArray[np.float64],
    ) -> Sequence[ICarbonHoneycombHexagon]:
        ...

    @classmethod
    @abstractmethod
    def _define_point_for_plane_polygon(
            cls,
            points: NDArray[np.float64],
            num_of_sides: int,
    ) -> tuple[list[NDArray[np.float64]], list[list[int]]]:
        ...

    @staticmethod
    @abstractmethod
    def _find_end_points(
            points_grouped_by_lines: list[NDArray[np.float64]],
    ) -> list[tuple[tuple, tuple]]:
        ...

    @staticmethod
    @abstractmethod
    def _build_plane_polygon(
            points_grouped_by_lines: list[NDArray[np.float64]],
            plane_hexagons_indexes: list[list[int]],
            polygon_class: Type[ICarbonHoneycombPolygon],
    ) -> Sequence[ICarbonHoneycombPolygon]:
        ...

    @classmethod
    @abstractmethod
    def calculate_edge_holes(
            cls,
            points: NDArray[np.float64],
            coordinate_limits: PCoordinateLimits,
    ) -> NDArray[np.float64]:
        ...

    @staticmethod
    @abstractmethod
    def _calc_holes_for_edge(
            edge_points: NDArray[np.float64],
    ) -> list[NDArray[np.float64]]:
        ...
