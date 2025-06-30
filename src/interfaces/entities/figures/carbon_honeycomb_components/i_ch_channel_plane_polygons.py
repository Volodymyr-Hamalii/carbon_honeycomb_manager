from abc import abstractmethod
import numpy as np

from src.interfaces.entities.figures.i_flat_figure import IFlatFigure

__all__: list[str] = [
    "ICHChannelPlanePolygon",
    "ICHChannelPlaneHexagon",
    "ICHChannelPlanePentagon",
]


class ICHChannelPlanePolygon(IFlatFigure):
    """Interface for carbon honeycomb channel plane polygon."""

    @abstractmethod
    def get_direction_to_center(self, channel_center: np.ndarray) -> bool:
        ...


class ICHChannelPlaneHexagon(ICHChannelPlanePolygon):
    """Interface for carbon honeycomb channel plane hexagon."""

    pass


class ICHChannelPlanePentagon(ICHChannelPlanePolygon):
    """Interface for carbon honeycomb channel plane pentagon."""

    pass
