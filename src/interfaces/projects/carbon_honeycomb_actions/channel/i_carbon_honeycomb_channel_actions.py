from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints
from src.interfaces.entities.figures.carbon_honeycomb_components.i_ch_channel_plane import ICHChannelPlane


class ICarbonHoneycombChannelActions(ABC):
    """Interface for carbon honeycomb channel actions."""

    @classmethod
    @abstractmethod
    def build_planes(
            cls,
            points: NDArray[np.float64],
    ) -> list[ICHChannelPlane]:
        ...

    @staticmethod
    @abstractmethod
    def _build_neighbors(
            xy_sets: list[set[tuple[np.float32, np.float32]]],
    ) -> dict[int, list[int]]:
        ...

    @classmethod
    @abstractmethod
    def _find_first_and_second_plane(
            cls,
            xy_sets: list[set[tuple[np.float32, np.float32]]],
            base_point: tuple[float | np.float32, float | np.float32],
    ) -> tuple[int, int]:
        ...

    @staticmethod
    @abstractmethod
    def calculate_ave_dist_between_closest_atoms(
            points: NDArray[np.float64] | IPoints,
    ) -> np.floating:
        ...

    @staticmethod
    @abstractmethod
    def calculate_ave_dist_between_closest_hexagon_centers(
            planes: list[ICHChannelPlane],
    ) -> np.floating:
        ...
