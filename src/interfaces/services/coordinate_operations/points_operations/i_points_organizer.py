from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


class IPointsOrganizer(ABC):
    @staticmethod
    @abstractmethod
    def group_by_unique_xy(
            coordinates: NDArray[np.float64],
    ) -> dict[tuple[np.float32, np.float32], np.ndarray]:
        ...

    @classmethod
    @abstractmethod
    def group_by_the_xy_lines(
            cls,
            groups_by_xy: dict[tuple[np.float32, np.float32], np.ndarray],
            coordinates_to_group: NDArray[np.float64],
            epsilon: float,
            min_points_in_line: int,
    ) -> list[dict[tuple[np.float32, np.float32], np.ndarray]]:
        ...

    @classmethod
    @abstractmethod
    def group_by_lines(
            cls,
            points: np.ndarray | list[np.ndarray],
            epsilon: float,
            min_points_in_line: int,
    ) -> list[np.ndarray]:
        ...
