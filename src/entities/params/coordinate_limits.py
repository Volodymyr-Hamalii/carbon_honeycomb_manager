from dataclasses import dataclass
from src.interfaces import PCoordinateLimits


@dataclass(frozen=True)
class CoordinateLimits(PCoordinateLimits):
    """Class for coordinate limits."""
    x_min: float = -float("inf")
    x_max: float = float("inf")

    y_min: float = -float("inf")
    y_max: float = float("inf")

    z_min: float = -float("inf")
    z_max: float = float("inf")
