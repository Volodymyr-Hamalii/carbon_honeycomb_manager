from typing import Protocol


class PCoordinateLimits(Protocol):
    """Protocol for coordinate limits."""
    x_min: float
    x_max: float

    y_min: float
    y_max: float

    z_min: float
    z_max: float
