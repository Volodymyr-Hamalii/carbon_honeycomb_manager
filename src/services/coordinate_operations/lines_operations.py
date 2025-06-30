import numpy as np
from numpy.typing import NDArray

from src.interfaces import ILinesOperations
from src.services.utils import Logger


logger = Logger(__name__)


class LinesOperations(ILinesOperations):
    @staticmethod
    def points_are_collinear(
            a: NDArray[np.float64],
            b: NDArray[np.float64],
            c: NDArray[np.float64],
            eps: float = 1e-6,
    ) -> bool:
        """
        Returns True if points a, b, c lie on the same line in 3D,
        i.e. the norm of the cross product is near zero.
        """
        cross_prod: np.ndarray = np.cross(b - a, c - a)
        return bool(np.linalg.norm(cross_prod) < eps)

    @staticmethod
    def get_line_equation(
            a: NDArray[np.float64],
            b: NDArray[np.float64],
    ) -> tuple[float, float, float, float]:
        """
        Get line equation from 2 points.

        The line equation is of the form:
        ax + by + cz + d = 0
        where a, b, c are the components of the normal vector to the line,
        and d is the distance from the origin to the line.

        Returns tuple (a, b, c, d).
        """
        # Check if the points have z coordinate (set it to 0 if not)
        if len(a) == 2:
            a = np.append(a, 0)
        if len(b) == 2:
            b = np.append(b, 0)

        # Calculate the direction vector of the line
        direction_vector: np.ndarray = b - a

        # Calculate the normal vector of the line
        normal_vector: np.ndarray = np.cross(direction_vector, np.array([0, 0, 1]))

        # Calculate the line equation
        line_equation: tuple[float, float, float, float] = (
            normal_vector[0], normal_vector[1], normal_vector[2], -np.dot(normal_vector, a))
        return line_equation
