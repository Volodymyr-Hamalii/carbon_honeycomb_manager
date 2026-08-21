from dataclasses import dataclass, asdict

from src.interfaces import PValidationTargets


@dataclass(frozen=True)
class ValidationTargets(PValidationTargets):
    """Target distances and tolerances for validating an intercalated structure."""

    target_dist_to_carbon: float
    target_dist_between_inter_atoms: float
    hard_min_dist_between_inter_atoms: float
    carbon_z_period: float
    opposite_position_tolerance: float
    max_compression_percent: float = 8.0
    max_expansion_percent: float = 10.0
    z_period_tolerance: float = 0.1
    max_z_period_multiplier: int = 10
    required_z_period_multiplier: int | None = None
    near_wall_max_dist_to_plane: float | None = None

    @property
    def near_wall_dist_to_plane_limit(self) -> float:
        """
        Distance to the nearest wall plane up to which an atom counts as sitting near a wall.

        Defaults to `dist_to_carbon_upper_bound`: an atom whose perpendicular distance to the closest
        wall already exceeds the largest acceptable intercalated-carbon distance cannot be at
        equilibrium with that wall, so the intercalated-carbon target does not apply to it.
        """
        if self.near_wall_max_dist_to_plane is not None:
            return self.near_wall_max_dist_to_plane

        return self.dist_to_carbon_upper_bound

    @property
    def dist_to_carbon_lower_bound(self) -> float:
        """Lower edge of the allowed corridor around the intercalated-carbon equilibrium distance."""
        return self.target_dist_to_carbon * (1 - self.max_compression_percent / 100)

    @property
    def dist_to_carbon_upper_bound(self) -> float:
        """Upper edge of the allowed corridor around the intercalated-carbon equilibrium distance."""
        return self.target_dist_to_carbon * (1 + self.max_expansion_percent / 100)

    @property
    def dist_between_inter_atoms_lower_bound(self) -> float:
        """Lower edge of the allowed corridor around the intercalated-intercalated equilibrium distance."""
        return self.target_dist_between_inter_atoms * (1 - self.max_compression_percent / 100)

    @property
    def dist_between_inter_atoms_upper_bound(self) -> float:
        """Upper edge of the allowed corridor around the intercalated-intercalated equilibrium distance."""
        return self.target_dist_between_inter_atoms * (1 + self.max_expansion_percent / 100)

    def to_dict(self) -> dict[str, float | int]:
        """Return the targets together with the derived corridor bounds."""
        result: dict[str, float | int] = dict(asdict(self))
        result["dist_to_carbon_lower_bound"] = round(self.dist_to_carbon_lower_bound, 4)
        result["dist_to_carbon_upper_bound"] = round(self.dist_to_carbon_upper_bound, 4)
        result["dist_between_inter_atoms_lower_bound"] = round(self.dist_between_inter_atoms_lower_bound, 4)
        result["dist_between_inter_atoms_upper_bound"] = round(self.dist_between_inter_atoms_upper_bound, 4)
        result["near_wall_dist_to_plane_limit"] = round(self.near_wall_dist_to_plane_limit, 4)
        return result
