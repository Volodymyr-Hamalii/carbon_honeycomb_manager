from functools import cached_property
from dataclasses import dataclass
import numpy as np

# Import services only when needed to avoid circular imports
from .points import Points


@dataclass(frozen=True)
class FlatFigure(Points):
    @cached_property
    def plane_params(self) -> tuple[float, float, float, float]:
        """ Compute and cache the result of the get_plane_params() method. """
        return self.get_plane_params()

    def get_plane_params(self) -> tuple[float, float, float, float]:
        """
        Define the plane like ax + by + cz + d = 0
        using the three provided points.

        Takes 3 non collinear points from self.points to define the plane.
        Returns a, b, c, d parameters from the equation above.
        """

        points: np.ndarray = self.points

        if points.shape[0] < 3:
            raise ValueError("At least 3 points are required to define a plane.")

        # 1) Pick first point p1
        p1: np.ndarray = points[0]

        # 2) Find a second point p2 that is not identical to p1
        p2: np.ndarray | None = None
        for i in range(1, len(points)):
            if not np.allclose(points[i], p1):
                p2 = points[i]
                break

        if p2 is None:
            raise ValueError("All points are identical. Cannot define a plane.")

        p3: np.ndarray | None = None
        for j in reversed(range(1, len(points))):
            c = points[j]
            # We already used p1, p2, but we might revisit them in the loop;
            # that's okay if they help us find a non-collinear point.
            # Import locally to avoid circular imports
            from src.services.coordinate_operations.lines_operations import LinesOperations
            if not LinesOperations.points_are_collinear(p1, p2, c):
                p3 = c
                break

        if p3 is None:
            raise ValueError("All points are collinear. Cannot define a plane.")

        # Import locally to avoid circular imports
        from src.services.coordinate_operations.planes_operations import PlanesBuilder
        return PlanesBuilder.build_plane_params(p1, p2, p3)
