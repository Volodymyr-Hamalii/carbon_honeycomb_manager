from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints


class IDistanceMeasurer(ABC):
    @staticmethod
    @abstractmethod
    def calculate_distance_between_2_points(
            p1: tuple | NDArray[np.float64],
            p2: tuple | NDArray[np.float64],
    ) -> float:
        ...

    @staticmethod
    @abstractmethod
    def calculate_distance_from_plane(
            points: NDArray[np.float64] | IPoints,
            line_params: tuple[float, float, float, float],
    ) -> float:
        ...

    @staticmethod
    @abstractmethod
    def calculate_signed_distance_from_plane(
            points: NDArray[np.float64] | IPoints,
            A: float,
            B: float,
            C: float,
            D: float,
    ) -> float:
        ...

    @staticmethod
    @abstractmethod
    def calculate_dist_matrix(
            points: NDArray[np.float64] | IPoints,
    ) -> NDArray[np.float64]:
        ...

    @staticmethod
    @abstractmethod
    def calculate_min_distances(
            points_1: NDArray[np.float64] | IPoints,
            points_2: NDArray[np.float64] | IPoints,
    ) -> NDArray[np.float64]:
        ...

    @classmethod
    @abstractmethod
    def calculate_min_distance_sum(
            cls,
            points_1: NDArray[np.float64] | IPoints,
            points_2: NDArray[np.float64] | IPoints,
    ) -> float:
        ...

    @classmethod
    @abstractmethod
    def calculate_min_distances_between_points(
            cls,
            points: NDArray[np.float64] | IPoints,
    ) -> NDArray[np.float64]:
        ...
