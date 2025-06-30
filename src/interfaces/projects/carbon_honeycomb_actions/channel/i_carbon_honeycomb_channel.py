from abc import abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints
from src.interfaces.entities.figures.carbon_honeycomb_components.i_ch_channel_plane import ICHChannelPlane


class ICarbonHoneycombChannel(IPoints):
    """Interface for carbon honeycomb channel."""

    @abstractmethod
    def planes(self) -> list[ICHChannelPlane]:
        ...

    @abstractmethod
    def channel_center(self) -> NDArray[np.float64]:
        ...

    @abstractmethod
    def ave_dist_between_closest_atoms(self) -> np.floating:
        ...

    @abstractmethod
    def ave_dist_between_closest_hexagon_centers(self) -> np.floating:
        ...
