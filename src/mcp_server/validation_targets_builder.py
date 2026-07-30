"""Default validation targets resolved from the per-element and per-structure constants."""

import numpy as np
from numpy.typing import NDArray
import pandas as pd

from src.interfaces import ICarbonHoneycombChannel
from src.entities import ValidationTargets
from src.projects.intercalation_and_sorption import IntercalationAndSorption, StructureValidator

from .serializers import name_value_df_to_dict


class ValidationTargetsBuilder:
    """
    Builds `ValidationTargets` for a structure, resolving unset values from the project constants.

    Nothing here is hardcoded per element: the equilibrium distances come from
    `IntercalationAndSorption.get_inter_chc_constants()`, which resolves them through
    `ATOM_PARAMS_MAP[element]` and the carbon geometry of the structure itself. The caller can
    override any of them, which is what makes the same tool usable by skills that follow different
    rules.
    """

    AVERAGE_CARBON_DIST_KEY_SUFFIX: str = "-C distance (Å)"
    DIST_BETWEEN_ATOMS_KEY: str = "Distance between atoms (Å)"
    HARD_MIN_DIST_KEY: str = "Distance to remove too close atoms (Å)"

    @classmethod
    def build(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            carbon_channel: ICarbonHoneycombChannel,
            target_dist_to_carbon: float | None = None,
            target_dist_between_inter_atoms: float | None = None,
            hard_min_dist_between_inter_atoms: float | None = None,
            max_compression_percent: float = 8.0,
            max_expansion_percent: float = 10.0,
            carbon_z_period: float | None = None,
            z_period_tolerance: float = 0.1,
            max_z_period_multiplier: int = 10,
            opposite_position_tolerance: float | None = None,
            near_wall_max_dist_to_plane: float | None = None,
    ) -> ValidationTargets:
        """Build the validation targets, filling every unset value with the project default."""
        constants: dict[str, float] = cls.get_constants(project_dir, subproject_dir, structure_dir)

        if target_dist_to_carbon is None:
            target_dist_to_carbon = cls._get_average_carbon_dist(constants)

        if target_dist_between_inter_atoms is None:
            target_dist_between_inter_atoms = float(constants[cls.DIST_BETWEEN_ATOMS_KEY])

        if hard_min_dist_between_inter_atoms is None:
            hard_min_dist_between_inter_atoms = float(constants[cls.HARD_MIN_DIST_KEY])

        if carbon_z_period is None:
            carbon_z_period = cls.get_carbon_z_period(carbon_channel, z_period_tolerance)

        if opposite_position_tolerance is None:
            # Half of the C-C bond length: an atom placed further off the normal than that is
            # closer to a neighbouring wall feature than to this one.
            opposite_position_tolerance = float(carbon_channel.ave_dist_between_closest_atoms) / 2

        return ValidationTargets(
            target_dist_to_carbon=target_dist_to_carbon,
            target_dist_between_inter_atoms=target_dist_between_inter_atoms,
            hard_min_dist_between_inter_atoms=hard_min_dist_between_inter_atoms,
            carbon_z_period=carbon_z_period,
            opposite_position_tolerance=opposite_position_tolerance,
            max_compression_percent=max_compression_percent,
            max_expansion_percent=max_expansion_percent,
            z_period_tolerance=z_period_tolerance,
            max_z_period_multiplier=max_z_period_multiplier,
            near_wall_max_dist_to_plane=near_wall_max_dist_to_plane,
        )

    @staticmethod
    def get_constants(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> dict[str, float]:
        """Read the intercalation constants of the element + structure pair as a flat dict."""
        constants_df: pd.DataFrame = IntercalationAndSorption.get_inter_chc_constants(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
        )
        return name_value_df_to_dict(constants_df)

    @staticmethod
    def get_carbon_z_period(
            carbon_channel: ICarbonHoneycombChannel,
            tolerance: float = 0.1,
    ) -> float:
        """
        Find the z self-repeat period of the carbon channel.

        Falls back to the full z extent of the channel when no shorter period is detected.
        """
        carbon_points: NDArray[np.float64] = carbon_channel.points
        z_period: float | None = StructureValidator.find_z_period(carbon_points, tolerance=tolerance)

        if z_period is not None:
            return z_period

        return float(carbon_points[:, 2].max() - carbon_points[:, 2].min())

    @classmethod
    def _get_average_carbon_dist(cls, constants: dict[str, float]) -> float:
        """
        Pick the `Average {element}-C distance (Å)` value out of the constants.

        The key carries the element symbol, so it is matched by suffix instead of being spelled out.
        """
        for name, value in constants.items():
            if name.startswith("Average ") and name.endswith(cls.AVERAGE_CARBON_DIST_KEY_SUFFIX):
                return float(value)

        raise KeyError(
            f"No 'Average <element>-C distance (Å)' constant found among: {sorted(constants)}."
        )
