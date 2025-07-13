from abc import ABC, abstractmethod
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from ..params.p_coordinate_limits import PCoordinateLimits


T = TypeVar("T", bound="IPoints")


class IPoints(ABC):
    """Interface for points (any set of points in 3D space)."""

    points: NDArray[np.float64]

    @property
    @abstractmethod
    def __len__(self) -> int:
        ...

    @property
    @abstractmethod
    def coordinate_limits(self) -> PCoordinateLimits:
        ...

    @property
    @abstractmethod
    def sorted_points(self) -> NDArray[np.float64]:
        ...

    @property
    @abstractmethod
    def center(self) -> NDArray[np.float64]:
        ...

    @abstractmethod
    def to_df(self, columns: list[str]) -> pd.DataFrame:
        ...

    @abstractmethod
    def copy(self: T) -> T:
        ...
