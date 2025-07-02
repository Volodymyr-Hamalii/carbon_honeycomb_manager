from abc import abstractmethod
from .i_points import IPoints


class IFlatFigure(IPoints):
    """Interface for flat figure (where all points lie in the same plane)."""

    @property
    @abstractmethod
    def plane_params(self) -> tuple[float, float, float, float]:
        ...

    @abstractmethod
    def get_plane_params(self) -> tuple[float, float, float, float]:
        ...
