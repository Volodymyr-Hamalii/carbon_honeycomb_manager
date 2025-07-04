from dataclasses import dataclass
from src.interfaces import PCoordinateLimits


@dataclass(frozen=True)
class CoordinateLimits(PCoordinateLimits):
    """Class for coordinate limits."""
    x_min: float
    x_max: float

    y_min: float
    y_max: float

    z_min: float
    z_max: float
