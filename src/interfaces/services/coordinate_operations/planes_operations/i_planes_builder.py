from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


class IPlanesBuilder(ABC):
    @staticmethod
    @abstractmethod
    def build_plane_params(
            p1: NDArray[np.float64] | list[float],
            p2: NDArray[np.float64] | list[float],
            p3: NDArray[np.float64] | list[float],
    ) -> tuple[float, float, float, float]:
        ...
