from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


class ICarbonHoneycombUtils(ABC):
    """Interface for carbon honeycomb utils."""

    @staticmethod
    @abstractmethod
    def find_end_points(
            points_on_line: NDArray[np.float64],
            coordinates_to_check: tuple[str, str],
    ) -> tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]:
        ...

    @classmethod
    @abstractmethod
    def find_end_points_of_honeycomb_planes_groups(
            cls,
            honeycomb_planes_groups: list[dict[tuple[np.float32, np.float32], NDArray[np.float64]]],
    ) -> list[tuple[tuple[np.float32, np.float32], tuple[np.float32, np.float32]]]:
        ...

    @staticmethod
    @abstractmethod
    def found_polygon_node_indexes(
            extreme_points_of_groups: list[tuple[tuple[np.float64, np.float64], tuple[np.float64, np.float64]]],
            num_of_nodes: int = 6,  # hexagon
    ) -> list[list[int]]:
        ...

    @staticmethod
    @abstractmethod
    def split_xy_groups_by_max_distances(
            groups_by_the_xy_lines: list[dict[tuple[np.float32, np.float32], NDArray[np.float64]]],
            max_distance_between_xy_groups: np.floating | float,
    ) -> list[dict[tuple[np.float32, np.float32], NDArray[np.float64]]]:
        ...

    @staticmethod
    @abstractmethod
    def split_groups_by_max_distances(
            points_grouped_by_lines: list[NDArray[np.float64]],
            max_distance_between_xy_groups: np.floating | float,
    ) -> list[NDArray[np.float64]]:
        ...
