from abc import abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_flat_figure import IFlatFigure
from src.interfaces.entities.figures.i_points import IPoints


class ICHChannel(IPoints):
    @abstractmethod
    def planes(self) -> list[IFlatFigure]:
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
