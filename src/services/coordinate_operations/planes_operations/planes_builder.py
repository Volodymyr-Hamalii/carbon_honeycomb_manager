import numpy as np
from numpy.typing import NDArray

from src.interfaces import IPlanesBuilder


class PlanesBuilder(IPlanesBuilder):
    @staticmethod
    def build_plane_params(
            p1: NDArray[np.float64] | list[float],
            p2: NDArray[np.float64] | list[float],
            p3: NDArray[np.float64] | list[float],
    ) -> tuple[float, float, float, float]:
        """
        Define the plane like Ax + By + Cz + D = 0
        using the three provided points.

        Takes 3 points as a parameters as lists with 3 coordinates.
        Returns A, B, C, D parameters from the equation above.
        """

        p1_np: NDArray[np.float64] = np.array(p1)
        p2_np: NDArray[np.float64] = np.array(p2)
        p3_np: NDArray[np.float64] = np.array(p3)

        # Calculate the normal vector of the plane
        v1: NDArray[np.float64] = p2_np - p1_np
        v2: NDArray[np.float64] = p3_np - p1_np
        normal: NDArray[np.float64] = np.cross(v1, v2)

        A: float = normal[0]
        B: float = normal[1]
        C: float = normal[2]
        D: float = -np.dot(normal, p1_np)

        if B < 0:
            # Actually, I don't know why we need this check, but atoms filtering related planes
            # only works correctly under this condition.
            return -A, -B, -C, -D

        return A, B, C, D
