from dataclasses import dataclass

from src.interfaces.entities.params.p_coordinate_limits import ICoordinateLimits


@dataclass(frozen=True)
class CoordinateLimits(ICoordinateLimits):
    x_min: float = -float("inf")
    x_max: float = float("inf")

    y_min: float = -float("inf")
    y_max: float = float("inf")

    z_min: float = -float("inf")
    z_max: float = float("inf")
