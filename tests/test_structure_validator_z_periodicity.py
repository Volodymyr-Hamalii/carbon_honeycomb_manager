"""Tests for the rule 4 check: self-repeatability of a structure along the Oz axis."""

import numpy as np
from numpy.typing import NDArray

from src.projects.intercalation_and_sorption import StructureValidator

from .conftest import Z_PERIOD


def _column(z_values: list[float], x: float = 0.0, y: float = 0.0) -> NDArray[np.float64]:
    """Build a vertical column of atoms at the given z coordinates."""
    return np.array([[x, y, z] for z in z_values])


### is_invariant_under_z_shift ###


def test_uniform_column_is_invariant_under_its_own_step() -> None:
    points: NDArray[np.float64] = _column([0.0, 4.32, 8.64, 12.96])

    assert StructureValidator.is_invariant_under_z_shift(points, 4.32) is True


def test_uniform_column_is_not_invariant_under_a_wrong_shift() -> None:
    points: NDArray[np.float64] = _column([0.0, 4.32, 8.64, 12.96])

    assert StructureValidator.is_invariant_under_z_shift(points, 3.0) is False


def test_shift_longer_than_the_structure_cannot_be_verified() -> None:
    points: NDArray[np.float64] = _column([0.0, 4.32])

    assert StructureValidator.is_invariant_under_z_shift(points, 20.0) is None


def test_invariance_respects_the_xy_coordinates() -> None:
    # Two columns shifted in z by half a period: shifting by the full period keeps each column in
    # place, shifting by half a period would swap them and must therefore not match.
    points: NDArray[np.float64] = np.vstack([
        _column([0.0, 4.32, 8.64], x=0.0),
        _column([2.16, 6.48, 10.8], x=3.0),
    ])

    assert StructureValidator.is_invariant_under_z_shift(points, 4.32) is True
    assert StructureValidator.is_invariant_under_z_shift(points, 2.16) is False


def test_invariance_tolerates_deviations_within_the_tolerance() -> None:
    points: NDArray[np.float64] = _column([0.0, 4.32, 8.66, 12.96])

    assert StructureValidator.is_invariant_under_z_shift(points, 4.32, tolerance=0.1) is True
    assert StructureValidator.is_invariant_under_z_shift(points, 4.32, tolerance=0.01) is False


### find_z_period ###


def test_find_z_period_returns_the_smallest_repeating_step() -> None:
    points: NDArray[np.float64] = _column([0.0, 4.32, 8.64, 12.96, 17.28])

    assert StructureValidator.find_z_period(points) == 4.32


def test_find_z_period_ignores_a_step_that_only_matches_part_of_the_structure() -> None:
    # An AB stacking: the primitive period is 2 * 4.32, not 4.32.
    points: NDArray[np.float64] = np.array([
        [0.0, 0.0, 0.0],
        [3.0, 0.0, 4.32],
        [0.0, 0.0, 8.64],
        [3.0, 0.0, 12.96],
        [0.0, 0.0, 17.28],
    ])

    assert StructureValidator.find_z_period(points) == 8.64


def test_find_z_period_returns_none_for_a_single_atom() -> None:
    assert StructureValidator.find_z_period(np.array([[0.0, 0.0, 1.0]])) is None


### find_min_z_period_multiplier / check_z_periodicity ###


def test_one_belt_per_carbon_period_needs_a_single_period() -> None:
    # The shape of the `ar/A1-7_h3` reference: one atom per carbon z period.
    points: NDArray[np.float64] = _column([1.44, 1.44 + Z_PERIOD, 1.44 + 2 * Z_PERIOD])

    assert StructureValidator.find_min_z_period_multiplier(points, Z_PERIOD) == 1


def test_ab_stacking_needs_two_carbon_periods() -> None:
    points: NDArray[np.float64] = np.array([
        [0.0, 0.0, 1.0],
        [3.0, 0.0, 1.0 + Z_PERIOD],
        [0.0, 0.0, 1.0 + 2 * Z_PERIOD],
        [3.0, 0.0, 1.0 + 3 * Z_PERIOD],
        [0.0, 0.0, 1.0 + 4 * Z_PERIOD],
    ])

    assert StructureValidator.find_min_z_period_multiplier(points, Z_PERIOD) == 2


def test_check_z_periodicity_reports_the_repeat_length_and_the_seam() -> None:
    points: NDArray[np.float64] = _column([1.44, 1.44 + Z_PERIOD, 1.44 + 2 * Z_PERIOD])

    result: dict = StructureValidator.check_z_periodicity(points, Z_PERIOD, max_multiplier=5)

    assert result["passed"] is True
    assert result["min_period_multiplier"] == 1
    assert result["repeat_length"] == Z_PERIOD
    assert result["verified_by_overlap"] is True
    # The primitive cell holds a single atom, so tiling it reproduces the original spacing.
    assert result["seam"]["num_of_atoms_in_cell"] == 1
    assert result["seam"]["min_dist_across_seam"] == Z_PERIOD


def test_seam_excludes_a_floating_point_replica_on_the_cell_boundary() -> None:
    """A repeated AB file must not report a zero-distance seam from its boundary replica."""
    points: NDArray[np.float64] = np.array([
        [0.0, 0.0, 1.674],
        [1.384, 2.395, 4.168],
        [0.0, 0.0, 6.662],
        [1.384, 2.395, 9.156],
    ])

    result: dict = StructureValidator.check_z_periodicity(
        points, 4.988, max_multiplier=3, required_multiplier=1
    )

    assert result["seam"]["num_of_atoms_in_cell"] == 2
    assert result["seam"]["min_dist_across_seam"] > 3.45


def test_check_z_periodicity_fails_when_no_multiplier_matches() -> None:
    # A column with an irregular spacing that no multiple of the carbon period can reproduce.
    points: NDArray[np.float64] = _column([0.0, 2.0, 7.5, 9.1, 20.3])

    result: dict = StructureValidator.check_z_periodicity(points, Z_PERIOD, max_multiplier=3)

    assert result["passed"] is False
    assert result["min_period_multiplier"] is None
    assert result["repeat_length"] is None
    assert result["seam"] is None


def test_check_z_periodicity_marks_an_unverifiable_match() -> None:
    # A single elementary cell: nothing overlaps it, so the match cannot be verified by overlap.
    points: NDArray[np.float64] = _column([1.0, 1.0 + Z_PERIOD])

    result: dict = StructureValidator.check_z_periodicity(points, Z_PERIOD * 5, max_multiplier=3)

    assert result["passed"] is True
    assert result["min_period_multiplier"] == 1
    assert result["verified_by_overlap"] is False
    assert result["seam"]["num_of_atoms_in_cell"] == 2


def test_check_z_periodicity_can_require_the_intended_cell_multiplier() -> None:
    """Use the caller's multi-period cell instead of an incidental shorter match."""
    points: NDArray[np.float64] = _column([0.0, Z_PERIOD, 2 * Z_PERIOD])

    result: dict = StructureValidator.check_z_periodicity(
        points,
        Z_PERIOD,
        max_multiplier=5,
        required_multiplier=3,
    )

    assert result["passed"] is True
    assert result["min_period_multiplier"] == 3
    assert result["repeat_length"] == 3 * Z_PERIOD
    assert result["period_selection_mode"] == "explicit"
    assert result["required_multiplier"] == 3
