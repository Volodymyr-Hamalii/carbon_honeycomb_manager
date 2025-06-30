from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


class ILinesOperations(ABC):
    @staticmethod
    @abstractmethod
    def points_are_collinear(
            a: NDArray[np.float64],
            b: NDArray[np.float64],
            c: NDArray[np.float64],
            eps: float,
    ) -> bool:
        ...

    @staticmethod
    @abstractmethod
    def get_line_equation(
            a: NDArray[np.float64],
            b: NDArray[np.float64],
    ) -> tuple[float, float, float, float]:
        ...
