"""Tests for the validation target corridor bounds."""

from src.entities import ValidationTargets


def _build_targets(**overrides: float | int) -> ValidationTargets:
    """Build targets with round numbers, overriding any field."""
    defaults: dict[str, float | int] = {
        "target_dist_to_carbon": 2.0,
        "target_dist_between_inter_atoms": 4.0,
        "hard_min_dist_between_inter_atoms": 2.8,
        "carbon_z_period": 4.32,
        "opposite_position_tolerance": 0.7,
    }
    return ValidationTargets(**{**defaults, **overrides})  # type: ignore[arg-type]


def test_default_corridor_is_minus_8_plus_10_percent() -> None:
    targets: ValidationTargets = _build_targets()

    assert targets.dist_between_inter_atoms_lower_bound == 4.0 * 0.92
    assert targets.dist_between_inter_atoms_upper_bound == 4.0 * 1.10
    assert targets.dist_to_carbon_lower_bound == 2.0 * 0.92
    assert targets.dist_to_carbon_upper_bound == 2.0 * 1.10


def test_corridor_follows_the_provided_percentages() -> None:
    targets: ValidationTargets = _build_targets(
        max_compression_percent=0.0, max_expansion_percent=50.0
    )

    assert targets.dist_between_inter_atoms_lower_bound == 4.0
    assert targets.dist_between_inter_atoms_upper_bound == 6.0


def test_to_dict_exposes_the_derived_bounds() -> None:
    payload: dict[str, float | int] = _build_targets().to_dict()

    assert payload["target_dist_between_inter_atoms"] == 4.0
    assert payload["dist_between_inter_atoms_lower_bound"] == round(4.0 * 0.92, 4)
    assert payload["dist_between_inter_atoms_upper_bound"] == round(4.0 * 1.10, 4)
    assert payload["carbon_z_period"] == 4.32
