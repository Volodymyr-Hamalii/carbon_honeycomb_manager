"""Cell parameters (a, b, c, angles) and basis vectors for `cell_params.txt`."""

from dataclasses import dataclass
from math import acos, degrees, hypot, sqrt

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import ConvexHull

from src.interfaces import ICarbonHoneycombChannel


@dataclass(frozen=True)
class CellParams:
    """Cell parameters: in-plane lattice vector P1P2 = (x, y) and the height `c`."""

    x: float
    y: float
    c: float

    @property
    def a_length(self) -> float:
        """Length of the in-plane basis vectors."""
        return hypot(self.x, self.y)

    @property
    def is_hexagonal(self) -> bool:
        """True for a hexagonal lattice (the angle between a and b is 120 degrees)."""
        return abs(self.x / self.y - sqrt(3)) < CellParamsBuilder.HEXAGONAL_TOLERANCE

    @property
    def gamma(self) -> float:
        """Angle between the basis vectors a = (-x, y) and b = (x, y), in degrees."""
        return degrees(acos((self.y ** 2 - self.x ** 2) / (self.x ** 2 + self.y ** 2)))


class CellParamsBuilder:
    """Build cell parameters from the xy projection of a carbon channel and format `cell_params.txt`."""

    HEXAGONAL_TOLERANCE: float = 0.01
    _VERTEX_TOLERANCE: float = 1e-3

    @classmethod
    def build(cls, channel: ICarbonHoneycombChannel, cell_height: float) -> CellParams:
        """
        Build cell parameters from one full channel.

        P1 is the left end of the bottom edge of the channel hull, P2 is the vertex with the largest X;
        the in-plane lattice vector is P2 - P1.
        """
        x_value, y_value = cls.find_lattice_vector(channel.points)

        return CellParams(x=x_value, y=y_value, c=cell_height)

    @classmethod
    def find_lattice_vector(cls, channel_points: NDArray[np.float64]) -> tuple[float, float]:
        """Return (X, Y) of the vector P1P2 for the convex hull of the channel xy projection."""
        xy_points: NDArray[np.float64] = np.unique(np.round(channel_points[:, :2], 6), axis=0)
        if len(xy_points) < 3:
            raise ValueError("Not enough channel points to build the xy hull.")

        vertices: NDArray[np.float64] = xy_points[ConvexHull(xy_points).vertices]

        bottom: NDArray[np.float64] = vertices[
            vertices[:, 1] <= vertices[:, 1].min() + cls._VERTEX_TOLERANCE
        ]
        p1: NDArray[np.float64] = bottom[np.argmin(bottom[:, 0])]

        rightmost: NDArray[np.float64] = vertices[
            vertices[:, 0] >= vertices[:, 0].max() - cls._VERTEX_TOLERANCE
        ]
        p2: NDArray[np.float64] = np.array([float(rightmost[:, 0].max()), float(rightmost[:, 1].mean())])

        return float(p2[0] - p1[0]), float(p2[1] - p1[1])

    @classmethod
    def format_params(cls, params: CellParams) -> str:
        """Format the content of `cell_params.txt`."""
        fmt = cls._format_number
        lines: list[str] = []

        if params.is_hexagonal:
            lines.append(f"a={fmt(params.a_length)}")
        else:
            lines.extend([
                "α=β=90",
                f"γ={fmt(params.gamma)}",
                "",
                f"a=b={fmt(params.a_length)}",
            ])

        lines.extend([
            f"c={fmt(params.c)}",
            "",
            "Basis:",
            f"a = ({fmt(-params.x)}, {fmt(params.y)}, 0)",
            f"b = ({fmt(params.x)}, {fmt(params.y)}, 0)",
            f"c = (0, 0, {fmt(params.c)})",
        ])

        return "\n".join(lines) + "\n"

    @staticmethod
    def _format_number(value: float) -> str:
        """Three decimals without trailing zeros (4.61, 14.18, 0)."""
        text: str = f"{value:.3f}".rstrip("0").rstrip(".")

        return "0" if text in ("-0", "") else text
