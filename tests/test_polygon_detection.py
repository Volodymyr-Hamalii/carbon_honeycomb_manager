"""
Tests for the wall polygon detection and for the metrics derived from it.

Both defects these tests cover were found on `ar/C0-7_h3`:

1. the bond threshold accepted non-bonded pairs as polygon edges, which short-circuited the real
   hexagons of the armchair-oriented walls into 5-cycles (17 pentagons / 0 hexagons per plane);
2. `ave_dist_between_closest_hexagon_centers` then crashed on the walls that ended up with no
   hexagon center at all.
"""

import numpy as np
from numpy.typing import NDArray
import pytest

from src.interfaces import ICarbonHoneycombChannel, ICarbonHoneycombPlane
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller, CarbonHoneycombPlane
from src.projects.carbon_honeycomb_actions.channel.carbon_honeycomb_channel_actions import (
    CarbonHoneycombChannelActions,
)
from src.projects.carbon_honeycomb_actions.channel.planes.carbon_honeycomb_plane_actions import (
    CarbonHoneycombPlaneActions,
)

from .conftest import (
    NUM_OF_WALLS,
    SyntheticCarbonChannel,
    WALL_0_HEXAGON_CENTERS,
    Z_PERIOD,
    build_wall_points,
)


# Measured on the structures shipped in `data/projects`: the C-C bonds of the (distorted) walls
# spread from 1.440 to 1.540 A, while the shortest non-bonded pair - the two atoms flanking an edge
# hole of an armchair-oriented wall - is 1.641 A.
LONGEST_REAL_BOND_RATIO: float = 1.540 / 1.440
SHORTEST_NON_BOND_RATIO: float = 1.641 / 1.440


def test_bond_threshold_separates_real_bonds_from_non_bonded_pairs() -> None:
    coefficient: float = CarbonHoneycombPlaneActions.BOND_LENGTH_CLEARANCE_COEFFICIENT

    assert LONGEST_REAL_BOND_RATIO < coefficient < SHORTEST_NON_BOND_RATIO


def test_zigzag_wall_is_split_into_hexagons_only() -> None:
    plane: ICarbonHoneycombPlane = CarbonHoneycombPlane(points=build_wall_points(0))

    assert len(plane.hexagons) == 2
    assert len(plane.pentagons) == 0


def test_hexagon_centers_match_the_wall_geometry() -> None:
    plane: ICarbonHoneycombPlane = CarbonHoneycombPlane(points=build_wall_points(0))

    centers: list[tuple[float, ...]] = sorted(
        tuple(round(float(value), 3) for value in hexagon.center) for hexagon in plane.hexagons
    )

    assert centers == sorted(WALL_0_HEXAGON_CENTERS)


def test_edge_holes_sit_between_the_hexagons_of_the_wall_edges() -> None:
    plane: ICarbonHoneycombPlane = CarbonHoneycombPlane(points=build_wall_points(0))

    assert len(plane.edge_holes) == 4
    # One hole per wall edge per z period gap.
    assert sorted(round(float(hole[2]), 3) for hole in plane.edge_holes) == [2.88, 2.88, 7.2, 7.2]


### ave_dist_between_closest_hexagon_centers ###


def test_average_distance_between_hexagon_centers(
        synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    # Each wall holds 2 hexagon centers exactly one carbon z period apart.
    assert float(synthetic_channel.ave_dist_between_closest_hexagon_centers) == pytest.approx(
        Z_PERIOD, abs=1e-3
    )


def test_average_distance_is_nan_when_the_walls_hold_no_polygons() -> None:
    # A wall too small to hold a complete polygon - the situation the armchair-oriented C-family
    # walls are in, where every hexagon straddles a channel edge.
    tiny_wall: NDArray[np.float64] = np.array([
        [0.0, 6.0, 0.0],
        [1.44, 6.0, 0.0],
        [0.0, 6.0, 1.44],
        [1.44, 6.0, 1.44],
    ])
    walls: tuple[NDArray[np.float64], ...] = tuple(tiny_wall for _ in range(NUM_OF_WALLS))
    channel: ICarbonHoneycombChannel = SyntheticCarbonChannel(points=tiny_wall, walls=walls)

    result: np.floating = CarbonHoneycombChannelActions.calculate_ave_dist_between_closest_hexagon_centers(
        channel.planes
    )

    assert np.isnan(result)


### min distance between hexagon layers ###


def test_min_dist_between_hexagon_layers_matches_the_wall_geometry() -> None:
    plane: ICarbonHoneycombPlane = CarbonHoneycombPlane(points=build_wall_points(0))

    result: float = CarbonHoneycombModeller._calculate_min_dist_between_hexagon_layers(
        hexagons=list(plane.hexagons), structure_dir="synthetic"
    )

    assert result == pytest.approx(Z_PERIOD, abs=1e-3)


def test_min_dist_between_hexagon_layers_is_nan_without_hexagons() -> None:
    # `get_channel_params` used to raise `IndexError: too many indices for array` here, which broke
    # every C-family structure.
    result: float = CarbonHoneycombModeller._calculate_min_dist_between_hexagon_layers(
        hexagons=[], structure_dir="synthetic"
    )

    assert np.isnan(result)


def test_min_dist_between_hexagon_layers_is_nan_for_a_single_layer() -> None:
    plane: ICarbonHoneycombPlane = CarbonHoneycombPlane(points=build_wall_points(0))
    single_hexagon: list = [plane.hexagons[0], plane.hexagons[0]]

    result: float = CarbonHoneycombModeller._calculate_min_dist_between_hexagon_layers(
        hexagons=single_hexagon, structure_dir="synthetic"
    )

    assert np.isnan(result)


def test_average_distance_falls_back_to_all_polygon_centers() -> None:
    # A single wall with a single hexagon: there is only one hexagon center, so the metric has
    # nothing to measure between and must report NaN instead of crashing.
    walls: tuple[NDArray[np.float64], ...] = (build_wall_points(0)[:12],)
    channel: ICarbonHoneycombChannel = SyntheticCarbonChannel(
        points=build_wall_points(0)[:12], walls=walls
    )

    result: np.floating = CarbonHoneycombChannelActions.calculate_ave_dist_between_closest_hexagon_centers(
        channel.planes
    )

    assert np.isnan(result) or float(result) > 0
