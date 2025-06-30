from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces import IPoints


class IPointsFilter(ABC):
    @classmethod
    @abstractmethod
    def filter_coordinates_related_to_plane(
            cls,
            coordinates: NDArray[np.float64],
            A: float, B: float, C: float, D: float,
            direction: bool,
            min_distance: float = 0,
    ) -> IPoints:
        ...

    @staticmethod
    @abstractmethod
    def filter_by_min_max_z(
            points_to_filter: IPoints,
            z_min: float,
            z_max: float,
            move_align_z: bool,
    ) -> IPoints:
        ...
