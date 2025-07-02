from abc import abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints
from .planes import ICarbonHoneycombPlane


class ICarbonHoneycombChannel(IPoints):
    """Interface for carbon honeycomb channel."""

    @property
    @abstractmethod
    def planes(self) -> list[ICarbonHoneycombPlane]:
        ...

    @property
    @abstractmethod
    def channel_center(self) -> NDArray[np.float64]:
        ...

    @property
    @abstractmethod
    def ave_dist_between_closest_atoms(self) -> np.floating:
        ...

    @property
    @abstractmethod
    def ave_dist_between_closest_hexagon_centers(self) -> np.floating:
        ...
