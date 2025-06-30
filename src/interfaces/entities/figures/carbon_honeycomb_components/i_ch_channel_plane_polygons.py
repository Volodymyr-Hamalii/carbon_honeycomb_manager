from abc import abstractmethod
import numpy as np

from src.interfaces.entities.figures.i_flat_figure import IFlatFigure

__all__: list[str] = [
    "ICHChannelPlanePolygon",
    "ICHChannelPlaneHexagon",
    "ICHChannelPlanePentagon",
]


class ICHChannelPlanePolygon(IFlatFigure):
    @abstractmethod
    def get_direction_to_center(self, channel_center: np.ndarray) -> bool:
        ...


class ICHChannelPlaneHexagon(ICHChannelPlanePolygon):
    pass


class ICHChannelPlanePentagon(ICHChannelPlanePolygon):
    pass
