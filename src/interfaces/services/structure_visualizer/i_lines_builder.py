from abc import ABC, abstractmethod

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import NDArray

from .i_visualization_params import IVisualizationParams


class ILinesBuilder(ABC):
    @classmethod
    @abstractmethod
    def add_lines(
            cls,
            coordinates: NDArray[np.float64],
            ax: Axes,
            num_of_min_distances: int,
            skip_first_distances: int,
            visual_params: IVisualizationParams,
    ) -> None:
        ...

    @classmethod
    @abstractmethod
    def _build_lines(
            cls,
            coordinates: NDArray[np.float64],
            num_of_min_distances: int,
            skip_first_distances: int,
    ) -> list[list[NDArray[np.float64]]]:
        ...

    @staticmethod
    @abstractmethod
    def _find_min_unique_values(
            arr: NDArray[np.float64],
            num_of_values: int,
            skip_first_values: int,
    ) -> NDArray[np.float64]:
        ...
