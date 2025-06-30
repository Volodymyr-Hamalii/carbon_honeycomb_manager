from abc import abstractmethod
import numpy as np

from src.interfaces.entities.figures.i_flat_figure import IFlatFigure


class ICHChannelPlane(IFlatFigure):
    @abstractmethod
    def pentagons(self) -> list[IFlatFigure]:
        ...

    @abstractmethod
    def hexagons(self) -> list[IFlatFigure]:
        ...

    @abstractmethod
    def edge_holes(self) -> np.ndarray:
        ...

    @abstractmethod
    def get_direction_to_center(self, channel_center: np.ndarray) -> bool:
        ...
