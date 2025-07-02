from abc import abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_flat_figure import IFlatFigure

from .plane_polygons import ICarbonHoneycombPentagon, ICarbonHoneycombHexagon


class ICarbonHoneycombPlane(IFlatFigure):
    @property
    @abstractmethod
    def pentagons(self) -> list[ICarbonHoneycombPentagon]:
        ...

    @property
    @abstractmethod
    def hexagons(self) -> list[ICarbonHoneycombHexagon]:
        ...

    @property
    @abstractmethod
    def edge_holes(self) -> NDArray[np.float64]:
        ...

    @abstractmethod
    def get_direction_to_center(self, channel_center: NDArray[np.float64]) -> bool:
        ...
