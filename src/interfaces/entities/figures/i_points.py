from abc import ABC, abstractmethod
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from src.interfaces.entities.params.p_coordinate_limits import PCoordinateLimits


T = TypeVar("T", bound="IPoints")


class IPoints(ABC):
    """Interface for points (any set of points in 3D space)."""

    points: NDArray[np.float64]

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def coordinate_limits(self) -> PCoordinateLimits:
        ...

    @abstractmethod
    def sorted_points(self) -> np.ndarray:
        ...

    @abstractmethod
    def center(self) -> np.ndarray:
        ...

    @abstractmethod
    def to_df(self, columns: list[str]) -> pd.DataFrame:
        ...

    @abstractmethod
    def copy(self: T) -> T:
        ...
