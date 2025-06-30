from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces import IPoints


class IPointsRotator(ABC):
    @classmethod
    @abstractmethod
    def rotate_on_angle_related_center(
            cls,
            points: IPoints,
            angle_x: float = 0,
            angle_y: float = 0,
            angle_z: float = 0,
    ) -> IPoints:
        ...

    @staticmethod
    @abstractmethod
    def _get_rotation_matrix_x(angle_x: float) -> NDArray[np.float64]:
        ...

    @staticmethod
    @abstractmethod
    def _get_rotation_matrix_y(angle_y: float) -> NDArray[np.float64]:
        ...

    @staticmethod
    @abstractmethod
    def _get_rotation_matrix_z(angle_z: float) -> NDArray[np.float64]:
        ...

    @classmethod
    @abstractmethod
    def rotate_around_z_parallel_line(
            cls,
            points: IPoints,
            line_point: NDArray[np.float64],
            angle: float,
    ) -> IPoints:
        ...
