from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints


class IPointsMover(ABC):
    @staticmethod
    @abstractmethod
    def move_on_vector(
            points: IPoints,
            vector: NDArray[np.float64],
            axis: list[str] = ["x", "y", "z"],
    ) -> IPoints:
        ...

    @staticmethod
    @abstractmethod
    def reflect_through_vertical_axis(
            points: IPoints,
    ) -> IPoints:
        ...
