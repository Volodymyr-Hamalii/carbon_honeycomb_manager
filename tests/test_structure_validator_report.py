"""Tests for the validation report distances and for the rule 3 (opposite polygons) classification."""

from dataclasses import replace
from math import sqrt
from typing import Any, Callable

import pytest

from src.entities import Points, ValidationTargets
from src.interfaces import ICarbonHoneycombChannel, PValidationTargets
from src.projects.intercalation_and_sorption import StructureValidator

from .conftest import (
    BOND_LENGTH,
    HEXAGON_RADIUS,
    WALL_0_EDGE_HOLES,
    WALL_0_HEXAGON_CENTERS,
    WALL_0_PLANE_Y,
    Z_PERIOD,
    build_atom_opposite,
)


NORMAL_DISTANCE: float = 2.4


PointsFactory = Callable[[list[list[float]]], Points]


@pytest.fixture
def report_for(
        synthetic_channel: ICarbonHoneycombChannel,
        targets: PValidationTargets,
        points_factory: PointsFactory,
) -> Callable[[list[list[float]]], dict[str, Any]]:
    """Build a validation report for the given atom coordinates."""
    def _build(coordinates: list[list[float]]) -> dict[str, Any]:
        return StructureValidator.build_report(
            carbon_channel=synthetic_channel,
            inter_atoms=points_factory(coordinates),
            targets=targets,
        )

    return _build


### DISTANCES ###


def test_distance_to_carbon_matches_the_hexagon_geometry(report_for) -> None:
    # An atom on the normal of a hexagon center is equidistant from all 6 atoms of that hexagon.
    expected_dist: float = sqrt(NORMAL_DISTANCE ** 2 + HEXAGON_RADIUS ** 2)
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE)]
    )

    atom: dict[str, Any] = report["atoms"][0]

    assert atom["min_dist_to_carbon"] == pytest.approx(expected_dist, abs=1e-3)
    assert atom["min_dist_to_plane"] == pytest.approx(NORMAL_DISTANCE, abs=1e-3)
    assert atom["nearest_carbon_spread"] == pytest.approx(0.0, abs=1e-3)
    assert atom["nearest_carbon_distances"] == pytest.approx(
        [expected_dist] * 6, abs=1e-3
    )


def test_deviation_percent_is_measured_against_the_target(report_for) -> None:
    report: dict[str, Any] = report_for([
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE),
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[1], NORMAL_DISTANCE),
    ])

    # The two hexagon centers are exactly one carbon z period apart.
    assert report["atoms"][0]["min_dist_to_inter"] == pytest.approx(Z_PERIOD, abs=1e-3)
    # targets.target_dist_between_inter_atoms is 4.0.
    assert report["atoms"][0]["dev_from_target_inter_percent"] == pytest.approx(
        (Z_PERIOD - 4.0) / 4.0 * 100, abs=1e-2
    )

    expected_dist: float = sqrt(NORMAL_DISTANCE ** 2 + HEXAGON_RADIUS ** 2)
    # targets.target_dist_to_carbon is 3.0.
    assert report["atoms"][0]["dev_from_target_carbon_percent"] == pytest.approx(
        (expected_dist - 3.0) / 3.0 * 100, abs=1e-2
    )


def test_single_atom_has_no_distance_to_other_intercalated_atoms(report_for) -> None:
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE)]
    )

    assert report["atoms"][0]["min_dist_to_inter"] is None
    assert report["atoms"][0]["dev_from_target_inter_percent"] is None
    assert report["summary"]["min_dist_to_inter"]["min"] is None
    assert report["hard_floor_check"]["passed"] is True


def test_summary_aggregates_the_per_atom_distances(report_for) -> None:
    report: dict[str, Any] = report_for([
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], 2.0),
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[1], 3.0),
    ])

    summary: dict[str, Any] = report["summary"]

    assert summary["min_dist_to_plane"]["min"] == pytest.approx(2.0, abs=1e-3)
    assert summary["min_dist_to_plane"]["max"] == pytest.approx(3.0, abs=1e-3)
    assert summary["min_dist_to_plane"]["mean"] == pytest.approx(2.5, abs=1e-3)
    assert report["num_of_atoms"] == 2


### HARD FLOOR AND CORRIDOR ###


def test_hard_floor_violation_is_reported(report_for) -> None:
    # Two atoms 1.0 A apart, well below the 2.0 A floor of the `targets` fixture.
    report: dict[str, Any] = report_for([
        [0.0, WALL_0_PLANE_Y - 2.4, 5.04],
        [0.0, WALL_0_PLANE_Y - 2.4, 6.04],
    ])

    check: dict[str, Any] = report["hard_floor_check"]

    assert check["passed"] is False
    assert check["min_pair_distance"] == pytest.approx(1.0, abs=1e-3)
    assert check["violations"][0]["atom_indexes"] == [0, 1]
    assert "hard_min_dist_between_inter_atoms" in report["violations"]


def test_distance_above_the_corridor_is_reported(report_for) -> None:
    # 4.32 A apart against a 4.0 A target: +8%, inside the +10% corridor.
    inside: dict[str, Any] = report_for([
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE),
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[1], NORMAL_DISTANCE),
    ])
    assert inside["dist_between_inter_atoms_corridor_check"]["passed"] is True

    # 8.64 A apart: far above the corridor.
    outside: dict[str, Any] = report_for([
        [0.0, WALL_0_PLANE_Y - 2.4, 0.72],
        [0.0, WALL_0_PLANE_Y - 2.4, 9.36],
    ])
    check: dict[str, Any] = outside["dist_between_inter_atoms_corridor_check"]

    assert check["passed"] is False
    assert check["atom_indexes_above"] == [0, 1]
    assert check["atom_indexes_below"] == []


### NEAR-WALL VS CENTRAL ATOMS (rule 1 applies to the near-wall ones only) ###


def test_near_wall_atom_is_flagged_as_such(report_for) -> None:
    # targets.target_dist_to_carbon is 3.0 with +10% expansion, so the near-wall limit is 3.3 A.
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE)]
    )

    assert report["atoms"][0]["is_near_wall"] is True
    assert report["summary"]["num_of_near_wall_atoms"] == 1
    assert report["summary"]["num_of_central_atoms"] == 0


def test_atom_on_the_channel_axis_is_central(report_for) -> None:
    # The channel axis is about 6 A from every wall - far beyond the 3.3 A near-wall limit.
    report: dict[str, Any] = report_for([[0.0, 0.0, 5.04]])
    atom: dict[str, Any] = report["atoms"][0]

    assert atom["is_near_wall"] is False
    assert atom["min_dist_to_plane"] > 3.3
    assert report["summary"]["num_of_central_atoms"] == 1


def test_central_atom_is_exempt_from_the_carbon_corridor(report_for) -> None:
    # The shape of the `ar/C2-7_h3` reference: a near-wall shell plus a central atom that sits far
    # above the carbon corridor. The central atom must not be reported as a violation.
    report: dict[str, Any] = report_for([
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE),
        [0.0, 0.0, 5.04],
    ])
    check: dict[str, Any] = report["dist_to_carbon_corridor_check"]

    assert report["atoms"][1]["min_dist_to_carbon"] > check["upper_bound"]
    assert check["atom_indexes_exempt"] == [1]
    assert check["atom_indexes_above"] == []
    assert check["num_of_atoms_checked"] == 1
    assert check["passed"] is True
    assert "dist_to_carbon_corridor" not in report["violations"]


def test_near_wall_atom_outside_the_carbon_corridor_is_still_a_violation(report_for) -> None:
    # 1.0 A from the wall: near-wall, and far below the corridor - this must be caught.
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], 1.0)]
    )
    check: dict[str, Any] = report["dist_to_carbon_corridor_check"]

    assert report["atoms"][0]["is_near_wall"] is True
    assert check["atom_indexes_below"] == [0]
    assert check["passed"] is False
    assert "dist_to_carbon_corridor" in report["violations"]


def test_summary_splits_the_carbon_distances_by_population(report_for) -> None:
    report: dict[str, Any] = report_for([
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE),
        [0.0, 0.0, 5.04],
    ])
    summary: dict[str, Any] = report["summary"]

    near_wall_dist: float = report["atoms"][0]["min_dist_to_carbon"]
    central_dist: float = report["atoms"][1]["min_dist_to_carbon"]

    assert summary["min_dist_to_carbon_near_wall"]["max"] == pytest.approx(near_wall_dist, abs=1e-3)
    assert summary["min_dist_to_carbon_central"]["min"] == pytest.approx(central_dist, abs=1e-3)
    # The undivided statistic still covers both, which is why rule 1 must not be read off it.
    assert summary["min_dist_to_carbon"]["max"] == pytest.approx(central_dist, abs=1e-3)


def test_near_wall_limit_can_be_overridden(
        synthetic_channel: ICarbonHoneycombChannel,
        targets: ValidationTargets,
        points_factory: PointsFactory,
) -> None:
    # Raising the limit past the channel radius makes every atom near-wall again.
    wide_targets: ValidationTargets = replace(targets, near_wall_max_dist_to_plane=10.0)

    report: dict[str, Any] = StructureValidator.build_report(
        carbon_channel=synthetic_channel,
        inter_atoms=points_factory([[0.0, 0.0, 5.04]]),
        targets=wide_targets,
    )

    assert report["atoms"][0]["is_near_wall"] is True
    assert report["dist_to_carbon_corridor_check"]["atom_indexes_exempt"] == []
    assert report["dist_to_carbon_corridor_check"]["passed"] is False
    assert report["targets"]["near_wall_dist_to_plane_limit"] == 10.0


def test_near_wall_limit_defaults_to_the_carbon_corridor_upper_bound(report_for) -> None:
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE)]
    )

    assert report["targets"]["near_wall_dist_to_plane_limit"] == report["targets"][
        "dist_to_carbon_upper_bound"
    ]


def test_compromise_is_both_when_no_trade_off_is_needed(report_for) -> None:
    report: dict[str, Any] = report_for([
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE),
        build_atom_opposite(WALL_0_HEXAGON_CENTERS[1], NORMAL_DISTANCE),
    ])

    assert report["z_periodicity_check"]["passed"] is True
    assert report["dist_between_inter_atoms_corridor_check"]["passed"] is True
    assert report["compromise"] == "both"


def test_compromise_names_rule_4_when_the_corridor_is_left(
        synthetic_channel: ICarbonHoneycombChannel,
        targets: ValidationTargets,
        points_factory: PointsFactory,
) -> None:
    # The same structure - one atom per carbon z period, 4.32 A apart - judged against a narrower
    # corridor: it still repeats along z, but the distances no longer fit the corridor.
    narrow_targets: ValidationTargets = replace(
        targets, max_compression_percent=1.0, max_expansion_percent=1.0
    )

    report: dict[str, Any] = StructureValidator.build_report(
        carbon_channel=synthetic_channel,
        inter_atoms=points_factory([
            build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE),
            build_atom_opposite(WALL_0_HEXAGON_CENTERS[1], NORMAL_DISTANCE),
        ]),
        targets=narrow_targets,
    )

    assert report["z_periodicity_check"]["passed"] is True
    assert report["dist_between_inter_atoms_corridor_check"]["passed"] is False
    assert report["compromise"] == "rule_4_over_corridor"


### RULE 3: PLACEMENT OPPOSITE WALL FEATURES ###


def test_atom_on_the_hexagon_normal_is_classified_as_opposite_a_hexagon(report_for) -> None:
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE)]
    )
    atom: dict[str, Any] = report["atoms"][0]

    assert atom["opposite_feature"] == "hexagon"
    assert atom["opposite_plane_index"] == 0
    assert atom["opposite_normal_dist"] == pytest.approx(NORMAL_DISTANCE, abs=1e-3)
    assert atom["opposite_in_plane_offset"] == pytest.approx(0.0, abs=1e-3)
    assert report["summary"]["num_of_atoms_opposite"]["hexagon"] == 1


def test_atom_on_the_edge_hole_normal_is_classified_as_opposite_an_edge_hole(report_for) -> None:
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_EDGE_HOLES[0], NORMAL_DISTANCE)]
    )
    atom: dict[str, Any] = report["atoms"][0]

    assert atom["opposite_feature"] == "edge_hole"
    assert atom["opposite_plane_index"] == 0
    assert atom["opposite_normal_dist"] == pytest.approx(NORMAL_DISTANCE, abs=1e-3)
    assert report["summary"]["num_of_atoms_opposite"]["edge_hole"] == 1


def test_atom_off_the_normal_is_not_classified_as_opposite_anything(report_for) -> None:
    # Half a hexagon height off the center: further from the normal than the 0.7 A tolerance.
    off_center: list[float] = build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE)
    off_center[2] += BOND_LENGTH

    report: dict[str, Any] = report_for([off_center])
    atom: dict[str, Any] = report["atoms"][0]

    assert atom["opposite_feature"] is None
    # The measured offset is still reported, so the caller can see how far off it is.
    assert atom["opposite_in_plane_offset"] == pytest.approx(BOND_LENGTH, abs=1e-3)
    assert report["summary"]["num_of_atoms_opposite"]["none"] == 1


def test_report_exposes_the_targets_it_used(report_for) -> None:
    report: dict[str, Any] = report_for(
        [build_atom_opposite(WALL_0_HEXAGON_CENTERS[0], NORMAL_DISTANCE)]
    )

    assert report["targets"]["target_dist_to_carbon"] == 3.0
    assert report["targets"]["target_dist_between_inter_atoms"] == 4.0
    assert report["targets"]["carbon_z_period"] == Z_PERIOD


def test_empty_structure_is_rejected(
        synthetic_channel: ICarbonHoneycombChannel,
        targets: PValidationTargets,
        points_factory: PointsFactory,
) -> None:
    with pytest.raises(ValueError):
        StructureValidator.build_report(
            carbon_channel=synthetic_channel,
            inter_atoms=points_factory([]),
            targets=targets,
        )
