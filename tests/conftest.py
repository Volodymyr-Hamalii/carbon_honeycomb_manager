"""Shared fixtures: a synthetic carbon channel with a hand-computed geometry."""

import os
import sys
from dataclasses import dataclass, field
from functools import cached_property
from math import cos, radians, sin
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

_ROOT_DIR_PATH: Path = Path(__file__).resolve().parent.parent
if str(_ROOT_DIR_PATH) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR_PATH))

from src.entities import Points, ValidationTargets  # noqa: E402
from src.interfaces import ICarbonHoneycombChannel, ICarbonHoneycombPlane  # noqa: E402
from src.projects.carbon_honeycomb_actions import CarbonHoneycombPlane  # noqa: E402
from src.projects.carbon_honeycomb_actions.channel.carbon_honeycomb_channel_actions import (  # noqa: E402
    CarbonHoneycombChannelActions,
)


# Geometry of the synthetic channel: an ideal zigzag graphene wall repeated on 6 sides of a prism.
BOND_LENGTH: float = 1.44
Z_PERIOD: float = BOND_LENGTH * 3  # 4.32 - the z self-repeat period of an ideal zigzag wall
NUM_OF_Z_PERIODS: int = 3
NUM_OF_WALLS: int = 6
CHANNEL_RADIUS: float = 6.0

# In-plane offsets of the three atom columns of one wall, and their z offsets inside one period.
_COLUMN_OFFSETS: tuple[float, ...] = (0.0, BOND_LENGTH * 3 ** 0.5 / 2, BOND_LENGTH * 3 ** 0.5)
_COLUMN_Z_OFFSETS: tuple[tuple[float, ...], ...] = (
    (0.0, BOND_LENGTH),
    (BOND_LENGTH * 1.5, BOND_LENGTH * 2.5),
    (0.0, BOND_LENGTH),
)


def build_wall_points(wall_index: int) -> NDArray[np.float64]:
    """Build one flat zigzag wall of the synthetic channel."""
    angle: float = radians(60 * wall_index)
    along_wall: NDArray[np.float64] = np.array([cos(angle), sin(angle), 0.0])
    wall_origin: NDArray[np.float64] = np.array([
        CHANNEL_RADIUS * cos(angle + radians(90)),
        CHANNEL_RADIUS * sin(angle + radians(90)),
        0.0,
    ]) - along_wall * _COLUMN_OFFSETS[-1] / 2

    points: list[NDArray[np.float64]] = []
    for offset, z_offsets in zip(_COLUMN_OFFSETS, _COLUMN_Z_OFFSETS):
        for period in range(NUM_OF_Z_PERIODS):
            for z_offset in z_offsets:
                points.append(
                    wall_origin
                    + along_wall * offset
                    + np.array([0.0, 0.0, period * Z_PERIOD + z_offset])
                )

    return np.round(np.array(points), 3)


@dataclass(frozen=True)
class SyntheticCarbonChannel(ICarbonHoneycombChannel, Points):
    """
    A carbon channel whose walls are handed in instead of being derived from the raw coordinates.

    `CarbonHoneycombChannel` splits a channel into planes geometrically, which needs a full, properly
    connected structure. The tests only need well-defined walls, so this double takes them directly
    and keeps everything else (polygons, edge holes, plane equations) computed by the real code.
    """

    walls: tuple[NDArray[np.float64], ...] = field(default_factory=tuple)

    @cached_property
    def planes(self) -> list[ICarbonHoneycombPlane]:
        """The channel wall planes."""
        return [CarbonHoneycombPlane(points=wall) for wall in self.walls]

    @cached_property
    def channel_center(self) -> NDArray[np.float64]:
        """Coordinates of the channel center."""
        return self.points.mean(axis=0)

    @cached_property
    def ave_dist_between_closest_atoms(self) -> np.floating:
        """Average distance between the closest carbon atoms."""
        return CarbonHoneycombChannelActions.calculate_ave_dist_between_closest_atoms(self.points)

    @cached_property
    def ave_dist_between_closest_hexagon_centers(self) -> np.floating:
        """Average distance between the closest hexagon centers of all the planes."""
        return CarbonHoneycombChannelActions.calculate_ave_dist_between_closest_hexagon_centers(
            self.planes
        )


@pytest.fixture(scope="session")
def synthetic_channel() -> ICarbonHoneycombChannel:
    """A synthetic carbon channel: 6 ideal zigzag walls with a known z period of 4.32 A."""
    walls: list[NDArray[np.float64]] = [build_wall_points(i) for i in range(NUM_OF_WALLS)]
    points: NDArray[np.float64] = np.unique(np.vstack(walls), axis=0)
    return SyntheticCarbonChannel(points=points, walls=tuple(walls))


@pytest.fixture
def targets() -> ValidationTargets:
    """Validation targets with round numbers, so the expected deviations are easy to compute."""
    return ValidationTargets(
        target_dist_to_carbon=3.0,
        target_dist_between_inter_atoms=4.0,
        hard_min_dist_between_inter_atoms=2.0,
        carbon_z_period=Z_PERIOD,
        opposite_position_tolerance=0.7,
        max_compression_percent=8.0,
        max_expansion_percent=10.0,
        z_period_tolerance=0.1,
        max_z_period_multiplier=5,
    )


# Geometry of wall 0 of the synthetic channel, derived by hand from the constants above and used by
# the tests to build atoms at known positions.
WALL_0_PLANE_Y: float = CHANNEL_RADIUS
WALL_0_HEXAGON_CENTERS: tuple[tuple[float, float, float], ...] = (
    (0.0, WALL_0_PLANE_Y, 5.04),
    (0.0, WALL_0_PLANE_Y, 9.36),
)
WALL_0_EDGE_HOLES: tuple[tuple[float, float, float], ...] = (
    (-1.247, WALL_0_PLANE_Y, 2.88),
    (-1.247, WALL_0_PLANE_Y, 7.2),
    (1.247, WALL_0_PLANE_Y, 2.88),
    (1.247, WALL_0_PLANE_Y, 7.2),
)

# All 6 carbon atoms of a hexagon lie at exactly one bond length from its center.
HEXAGON_RADIUS: float = BOND_LENGTH


def build_atom_opposite(
        feature: tuple[float, float, float],
        normal_distance: float,
) -> list[float]:
    """Place an atom on the normal of wall 0 at `normal_distance` from the given wall feature."""
    return [feature[0], feature[1] - normal_distance, feature[2]]


@pytest.fixture
def points_factory():
    """Helper turning a list of `[x, y, z]` triples into `Points`."""
    def _build(coordinates: list[list[float]]) -> Points:
        return Points(points=np.array(coordinates, dtype=np.float64))

    return _build
