"""Numeric validation report for an intercalated structure."""

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.distance import cdist

from src.interfaces import (
    ICarbonHoneycombChannel,
    ICarbonHoneycombPlane,
    IFlatFigure,
    IPoints,
    IStructureValidator,
    PValidationTargets,
)
from src.services import DistanceMeasurer, Logger


logger = Logger("StructureValidator")


class StructureValidator(IStructureValidator):
    """
    Numeric validation report for a set of intercalated atoms placed inside a carbon channel.

    The report is a plain nested dict, ready to be serialized. It contains measurements and
    violation flags only: every target and tolerance comes in as a `PValidationTargets` parameter,
    and the decision whether a structure is acceptable is left to the caller.
    """

    ROUND_DECIMALS: int = 3

    # An atom sitting opposite a hexagon center is roughly equidistant from the 6 carbon atoms of
    # that ring, so the spread of its 6 nearest carbon distances measures rule 3 even for the walls
    # that hold no complete polygon (see `_classify_opposite_features`).
    NUM_OF_NEAREST_CARBON_ATOMS: int = 6

    @classmethod
    def build_report(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            inter_atoms: IPoints,
            targets: PValidationTargets,
    ) -> dict[str, Any]:
        """Build the full validation report for the given intercalated atoms."""
        atoms: NDArray[np.float64] = np.asarray(inter_atoms.points, dtype=np.float64)

        if len(atoms) == 0:
            raise ValueError("Cannot validate an empty set of intercalated atoms.")

        carbon_points: NDArray[np.float64] = carbon_channel.points
        planes: list[ICarbonHoneycombPlane] = carbon_channel.planes

        dists_atoms_to_carbon: NDArray[np.float64] = cdist(atoms, carbon_points)
        dists_to_carbon: NDArray[np.float64] = np.min(dists_atoms_to_carbon, axis=1)
        nearest_carbon_dists: NDArray[np.float64] = np.sort(dists_atoms_to_carbon, axis=1)[
            :, :cls.NUM_OF_NEAREST_CARBON_ATOMS
        ]
        dists_to_inter: NDArray[np.float64] = cls._calculate_min_dists_to_other_atoms(atoms)
        dists_to_planes, nearest_plane_indexes = cls._calculate_dists_to_planes(atoms, planes)
        opposite_features: list[dict[str, Any]] = cls._classify_opposite_features(
            atoms, planes, targets.opposite_position_tolerance
        )

        # Only the atoms sitting near a wall are held to the intercalated-carbon equilibrium
        # distance. The atoms filling the middle of a wide channel are legitimately much further
        # from carbon - their spacing is governed by the intercalated-intercalated target instead.
        is_near_wall: NDArray[np.bool_] = dists_to_planes <= targets.near_wall_dist_to_plane_limit

        atom_rows: list[dict[str, Any]] = []
        for i, atom in enumerate(atoms):
            atom_rows.append({
                "index": i,
                "x": round(float(atom[0]), cls.ROUND_DECIMALS),
                "y": round(float(atom[1]), cls.ROUND_DECIMALS),
                "z": round(float(atom[2]), cls.ROUND_DECIMALS),
                "min_dist_to_carbon": round(float(dists_to_carbon[i]), cls.ROUND_DECIMALS),
                "dev_from_target_carbon_percent": cls._deviation_percent(
                    float(dists_to_carbon[i]), targets.target_dist_to_carbon
                ),
                "min_dist_to_inter": cls._round_or_none(dists_to_inter[i]),
                "dev_from_target_inter_percent": (
                    None if np.isnan(dists_to_inter[i])
                    else cls._deviation_percent(
                        float(dists_to_inter[i]), targets.target_dist_between_inter_atoms
                    )
                ),
                "min_dist_to_plane": round(float(dists_to_planes[i]), cls.ROUND_DECIMALS),
                "nearest_plane_index": int(nearest_plane_indexes[i]),
                "is_near_wall": bool(is_near_wall[i]),
                "nearest_carbon_distances": [
                    round(float(value), cls.ROUND_DECIMALS) for value in nearest_carbon_dists[i]
                ],
                "nearest_carbon_spread": round(
                    float(nearest_carbon_dists[i].max() - nearest_carbon_dists[i].min()),
                    cls.ROUND_DECIMALS,
                ),
                **opposite_features[i],
            })

        z_periodicity: dict[str, Any] = cls.check_z_periodicity(
            points=atoms,
            z_period=targets.carbon_z_period,
            tolerance=targets.z_period_tolerance,
            max_multiplier=targets.max_z_period_multiplier,
            required_multiplier=targets.required_z_period_multiplier,
        )
        hard_floor_check: dict[str, Any] = cls._check_hard_floor(
            atoms, targets.hard_min_dist_between_inter_atoms
        )
        cls._attach_periodic_seam_hard_floor(
            hard_floor_check,
            z_periodicity,
            targets.hard_min_dist_between_inter_atoms,
        )
        carbon_corridor_check: dict[str, Any] = cls._check_corridor(
            values=dists_to_carbon,
            lower_bound=targets.dist_to_carbon_lower_bound,
            upper_bound=targets.dist_to_carbon_upper_bound,
            mask=is_near_wall,
        )
        carbon_corridor_check["near_wall_dist_to_plane_limit"] = round(
            targets.near_wall_dist_to_plane_limit, 4
        )
        inter_corridor_check: dict[str, Any] = cls._check_corridor(
            values=dists_to_inter,
            lower_bound=targets.dist_between_inter_atoms_lower_bound,
            upper_bound=targets.dist_between_inter_atoms_upper_bound,
        )
        violations: list[str] = []
        if not hard_floor_check["passed"]:
            violations.append("hard_min_dist_between_inter_atoms")
        if not carbon_corridor_check["passed"]:
            violations.append("dist_to_carbon_corridor")
        if not inter_corridor_check["passed"]:
            violations.append("dist_between_inter_atoms_corridor")
        if not z_periodicity["passed"]:
            violations.append("z_self_repeatability")

        return {
            "num_of_atoms": len(atoms),
            "targets": targets.to_dict(),
            "atoms": atom_rows,
            "summary": cls._build_summary(
                atoms=atoms,
                dists_to_carbon=dists_to_carbon,
                dists_to_inter=dists_to_inter,
                dists_to_planes=dists_to_planes,
                nearest_carbon_spreads=nearest_carbon_dists.max(axis=1) - nearest_carbon_dists.min(axis=1),
                is_near_wall=is_near_wall,
                opposite_features=opposite_features,
                targets=targets,
            ),
            "hard_floor_check": hard_floor_check,
            "dist_to_carbon_corridor_check": carbon_corridor_check,
            "dist_between_inter_atoms_corridor_check": inter_corridor_check,
            "z_periodicity_check": z_periodicity,
            "violations": violations,
            "compromise": cls._describe_compromise(
                z_periodicity=z_periodicity,
                inter_corridor_check=inter_corridor_check,
            ),
        }

    ### Z SELF-REPEATABILITY ###

    @classmethod
    def find_z_period(
            cls,
            points: NDArray[np.float64],
            tolerance: float = 0.1,
    ) -> float | None:
        """
        Find the smallest positive shift along Oz that maps the point set onto itself.

        Candidate shifts are the differences between the distinct z coordinates of the set; the
        smallest one that passes `is_invariant_under_z_shift` over the overlap region is returned.
        Returns None when no candidate works.
        """
        z_coords: NDArray[np.float64] = np.unique(np.round(points[:, 2], cls.ROUND_DECIMALS))

        if len(z_coords) < 2:
            return None

        z_extent: float = float(z_coords[-1] - z_coords[0])
        candidates: NDArray[np.float64] = np.unique(np.round(z_coords - z_coords[0], cls.ROUND_DECIMALS))
        candidates = candidates[(candidates > tolerance) & (candidates < z_extent)]

        for candidate in candidates:
            if cls.is_invariant_under_z_shift(points, float(candidate), tolerance) is True:
                return float(candidate)

        return None

    @classmethod
    def find_min_z_period_multiplier(
            cls,
            points: NDArray[np.float64],
            z_period: float,
            tolerance: float = 0.1,
            max_multiplier: int = 10,
    ) -> int | None:
        """
        Find the smallest N for which shifting the set by `N * z_period` maps it onto itself.

        Returns None when no N up to `max_multiplier` works.
        """
        for multiplier in range(1, max_multiplier + 1):
            if cls.is_invariant_under_z_shift(points, z_period * multiplier, tolerance) is not False:
                return multiplier

        return None

    @classmethod
    def check_z_periodicity(
            cls,
            points: NDArray[np.float64],
            z_period: float,
            tolerance: float = 0.1,
            max_multiplier: int = 10,
            required_multiplier: int | None = None,
    ) -> dict[str, Any]:
        """
        Check rule 4 (self-repeatability along Oz).

        Reports the smallest number of carbon z periods after which the intercalated structure maps
        onto itself, the resulting repeat length, and whether the match could actually be verified
        against overlapping atoms (a structure shorter than one period has nothing to overlap with,
        so it repeats trivially and is reported with `verified_by_overlap = False`).
        """
        if z_period <= 0:
            raise ValueError(f"z_period must be positive, got {z_period}.")
        if required_multiplier is not None and not 1 <= required_multiplier <= max_multiplier:
            raise ValueError(
                "required_multiplier must be between 1 and max_multiplier inclusive."
            )

        results: list[dict[str, Any]] = []
        min_multiplier: int | None = None

        for multiplier in range(1, max_multiplier + 1):
            shift: float = z_period * multiplier
            is_invariant: bool | None = cls.is_invariant_under_z_shift(points, shift, tolerance)
            results.append({
                "multiplier": multiplier,
                "shift": round(shift, cls.ROUND_DECIMALS),
                "matches": is_invariant,
            })

            may_select: bool = (
                required_multiplier is None or multiplier == required_multiplier
            )
            if may_select and is_invariant is not False and min_multiplier is None:
                min_multiplier = multiplier

        repeat_length: float | None = (
            None if min_multiplier is None else z_period * min_multiplier
        )

        return {
            "carbon_z_period": round(z_period, cls.ROUND_DECIMALS),
            "tolerance": tolerance,
            "max_multiplier": max_multiplier,
            "required_multiplier": required_multiplier,
            "period_selection_mode": "automatic" if required_multiplier is None else "explicit",
            "min_period_multiplier": min_multiplier,
            "repeat_length": (
                None if repeat_length is None else round(repeat_length, cls.ROUND_DECIMALS)
            ),
            "verified_by_overlap": (
                None if min_multiplier is None
                else results[min_multiplier - 1]["matches"] is True
            ),
            "seam": (
                None if repeat_length is None
                else cls._measure_tiling_seam(points, repeat_length)
            ),
            "checked_multipliers": results,
            "passed": min_multiplier is not None,
        }

    @classmethod
    def _measure_tiling_seam(
            cls,
            points: NDArray[np.float64],
            repeat_length: float,
    ) -> dict[str, Any]:
        """
        Measure the distances across the seam produced by tiling the structure along Oz.

        The atoms are first reduced to one primitive cell (the ones with
        `z < z_min + repeat_length`), because a file may already hold several copies of the cell.
        `min_dist_across_seam` should be close to `min_dist_inside_cell`: a much smaller value means
        the tiling creates a clash, a much larger one means it leaves a gap.
        """
        z_min: float = float(points[:, 2].min())
        cell: NDArray[np.float64] = points[points[:, 2] < z_min + repeat_length]

        if len(cell) == 0:
            cell = points

        shifted: NDArray[np.float64] = cell + np.array([0.0, 0.0, repeat_length])
        min_dist_across_seam: float = float(np.min(cdist(cell, shifted)))

        min_dist_inside_cell: float | None = None
        if len(cell) > 1:
            min_dist_inside_cell = float(np.min(DistanceMeasurer.calculate_dist_matrix(cell)))

        return {
            "num_of_atoms_in_cell": len(cell),
            "min_dist_across_seam": round(min_dist_across_seam, cls.ROUND_DECIMALS),
            "min_dist_inside_cell": (
                None if min_dist_inside_cell is None
                else round(min_dist_inside_cell, cls.ROUND_DECIMALS)
            ),
        }

    @classmethod
    def is_invariant_under_z_shift(
            cls,
            points: NDArray[np.float64],
            shift: float,
            tolerance: float = 0.1,
    ) -> bool | None:
        """
        Check that shifting the point set along Oz by `shift` maps it onto itself.

        Only the region where the original and the shifted set overlap can be compared, so:
        - True  - the sets match inside the overlap region;
        - False - they do not match;
        - None  - the set is shorter than `shift`, so there is no overlap to compare (the tiling is
                  trivially consistent, but nothing was actually verified).
        """
        shifted: NDArray[np.float64] = points + np.array([0.0, 0.0, shift])

        z_min: float = float(points[:, 2].min())
        z_max: float = float(points[:, 2].max())

        overlap_min: float = z_min + shift - tolerance
        overlap_max: float = z_max + tolerance

        original_in_overlap: NDArray[np.float64] = points[
            (points[:, 2] >= overlap_min) & (points[:, 2] <= overlap_max)
        ]
        shifted_in_overlap: NDArray[np.float64] = shifted[
            (shifted[:, 2] >= overlap_min) & (shifted[:, 2] <= overlap_max)
        ]

        if len(original_in_overlap) == 0 and len(shifted_in_overlap) == 0:
            return None

        if len(original_in_overlap) != len(shifted_in_overlap):
            return False

        distances: NDArray[np.float64] = cdist(original_in_overlap, shifted_in_overlap)

        return bool(
            np.all(np.min(distances, axis=1) <= tolerance)
            and np.all(np.min(distances, axis=0) <= tolerance)
        )

    ### MEASUREMENTS ###

    @staticmethod
    def _calculate_min_dists_to_other_atoms(atoms: NDArray[np.float64]) -> NDArray[np.float64]:
        """Min distance from each atom to any other atom of the set (NaN for a single atom)."""
        if len(atoms) < 2:
            return np.array([np.nan] * len(atoms))

        return DistanceMeasurer.calculate_min_distances_between_points(atoms)

    @staticmethod
    def _calculate_dists_to_planes(
            atoms: NDArray[np.float64],
            planes: list[ICarbonHoneycombPlane],
    ) -> tuple[NDArray[np.float64], NDArray[np.int_]]:
        """Distance from each atom to the closest channel wall plane, and that plane index."""
        if not planes:
            return np.array([np.nan] * len(atoms)), np.array([-1] * len(atoms))

        dists: NDArray[np.float64] = np.array([
            [
                DistanceMeasurer.calculate_distance_from_plane(np.array([atom]), plane.plane_params)
                for plane in planes
            ]
            for atom in atoms
        ])

        return np.min(dists, axis=1), np.argmin(dists, axis=1)

    @classmethod
    def _classify_opposite_features(
            cls,
            atoms: NDArray[np.float64],
            planes: list[ICarbonHoneycombPlane],
            tolerance: float,
    ) -> list[dict[str, Any]]:
        """
        Find, for each atom, the wall feature it is placed opposite to (rule 3).

        An atom counts as placed opposite a feature when its projection onto the wall plane falls
        within `tolerance` of the feature: a hexagon center, a pentagon center or an edge hole.
        """
        features: list[tuple[str, int, int, NDArray[np.float64], tuple[float, float, float, float]]] = []

        for plane_index, plane in enumerate(planes):
            polygons_by_type: dict[str, list[IFlatFigure]] = {
                "hexagon": list(plane.hexagons),
                "pentagon": list(plane.pentagons),
            }
            for feature_type, polygons in polygons_by_type.items():
                for feature_index, polygon in enumerate(polygons):
                    features.append(
                        (feature_type, plane_index, feature_index, polygon.center, plane.plane_params)
                    )

            for feature_index, edge_hole in enumerate(plane.edge_holes):
                features.append(
                    ("edge_hole", plane_index, feature_index, edge_hole, plane.plane_params)
                )

        empty_result: dict[str, Any] = {
            "opposite_feature": None,
            "opposite_plane_index": None,
            "opposite_feature_index": None,
            "opposite_normal_dist": None,
            "opposite_in_plane_offset": None,
        }

        if not features:
            return [dict(empty_result) for _ in atoms]

        results: list[dict[str, Any]] = []

        for atom in atoms:
            best: dict[str, Any] = dict(empty_result)
            best_offset: float = float("inf")

            for feature_type, plane_index, feature_index, feature_point, plane_params in features:
                normal_dist, in_plane_offset = cls._split_offset_by_plane(
                    atom, feature_point, plane_params
                )

                if in_plane_offset < best_offset:
                    best_offset = in_plane_offset
                    best = {
                        "opposite_feature": feature_type,
                        "opposite_plane_index": plane_index,
                        "opposite_feature_index": feature_index,
                        "opposite_normal_dist": round(normal_dist, cls.ROUND_DECIMALS),
                        "opposite_in_plane_offset": round(in_plane_offset, cls.ROUND_DECIMALS),
                    }

            if best_offset > tolerance:
                # The closest feature is too far off the normal: the atom is not opposite anything.
                best = {**best, "opposite_feature": None}

            results.append(best)

        return results

    @staticmethod
    def _split_offset_by_plane(
            atom: NDArray[np.float64],
            feature_point: NDArray[np.float64],
            plane_params: tuple[float, float, float, float],
    ) -> tuple[float, float]:
        """
        Split the atom-to-feature offset into a normal and an in-plane component.

        Returns (distance along the plane normal, distance within the plane).
        """
        a, b, c, _ = plane_params
        normal: NDArray[np.float64] = np.array([a, b, c], dtype=np.float64)
        norm: np.floating = np.linalg.norm(normal)

        offset: NDArray[np.float64] = atom - feature_point

        if norm == 0:
            return float(np.linalg.norm(offset)), 0.0

        normal = normal / norm
        normal_component: float = float(np.dot(offset, normal))
        in_plane_offset: float = float(np.linalg.norm(offset - normal_component * normal))

        return abs(normal_component), in_plane_offset

    ### CHECKS ###

    @classmethod
    def _check_hard_floor(
            cls,
            atoms: NDArray[np.float64],
            hard_min_dist: float,
    ) -> dict[str, Any]:
        """Check that no pair of intercalated atoms is closer than the physical floor."""
        if len(atoms) < 2:
            return {
                "limit": round(hard_min_dist, 4),
                "min_pair_distance": None,
                "violations": [],
                "passed": True,
            }

        dist_matrix: NDArray[np.float64] = DistanceMeasurer.calculate_dist_matrix(atoms)
        violations: list[dict[str, Any]] = []

        for i, j in zip(*np.where(dist_matrix < hard_min_dist)):
            if i < j:
                violations.append({
                    "atom_indexes": [int(i), int(j)],
                    "distance": round(float(dist_matrix[i, j]), cls.ROUND_DECIMALS),
                })

        return {
            "limit": round(hard_min_dist, 4),
            "min_pair_distance": round(float(np.min(dist_matrix)), cls.ROUND_DECIMALS),
            "violations": violations,
            "passed": not violations,
        }

    @classmethod
    def _attach_periodic_seam_hard_floor(
            cls,
            hard_floor_check: dict[str, Any],
            z_periodicity: dict[str, Any],
            hard_min_dist: float,
    ) -> None:
        """Extend the hard-floor gate to the inferred periodic-cell seam."""
        seam: dict[str, Any] | None = z_periodicity.get("seam")
        seam_distance_value: Any = (
            None if seam is None else seam.get("min_dist_across_seam")
        )
        seam_distance: float | None = (
            None if seam_distance_value is None else float(seam_distance_value)
        )
        seam_passed: bool | None = (
            None if seam_distance is None else seam_distance >= hard_min_dist
        )
        hard_floor_check["periodic_seam_min_distance"] = cls._round_or_none(
            np.nan if seam_distance is None else seam_distance
        )
        hard_floor_check["periodic_seam_passed"] = seam_passed
        if seam_passed is False:
            hard_floor_check["passed"] = False

    @classmethod
    def _check_corridor(
            cls,
            values: NDArray[np.float64],
            lower_bound: float,
            upper_bound: float,
            mask: NDArray[np.bool_] | None = None,
    ) -> dict[str, Any]:
        """
        Check how many measured distances fall outside the allowed deviation corridor.

        `mask` selects the atoms the corridor applies to; the rest are reported as exempt and do not
        count as violations.
        """
        checked_mask: NDArray[np.bool_] = ~np.isnan(values)

        if mask is not None:
            exempt: list[int] = [int(i) for i in np.where(~mask)[0]]
            checked_mask = checked_mask & mask
        else:
            exempt = []

        below: list[int] = [int(i) for i in np.where(checked_mask & (values < lower_bound))[0]]
        above: list[int] = [int(i) for i in np.where(checked_mask & (values > upper_bound))[0]]

        return {
            "lower_bound": round(lower_bound, 4),
            "upper_bound": round(upper_bound, 4),
            "num_of_atoms_checked": int(np.sum(checked_mask)),
            "num_of_atoms_inside": int(np.sum(checked_mask)) - len(below) - len(above),
            "atom_indexes_below": below,
            "atom_indexes_above": above,
            "atom_indexes_exempt": exempt,
            "passed": not below and not above,
        }

    @staticmethod
    def _describe_compromise(
            z_periodicity: dict[str, Any],
            inter_corridor_check: dict[str, Any],
    ) -> str:
        """
        Describe which trade-off the structure represents (see rule 4 vs the deviation corridor).

        `rule_4_over_corridor` - the structure repeats along z but some intercalated distances leave
        the corridor; `corridor_over_rule_4` - the corridor is respected but the structure does not
        repeat; `both` - no trade-off was needed; `neither` - both checks fail.
        """
        repeats: bool = bool(z_periodicity["passed"])
        in_corridor: bool = bool(inter_corridor_check["passed"])

        if repeats and in_corridor:
            return "both"
        if repeats:
            return "rule_4_over_corridor"
        if in_corridor:
            return "corridor_over_rule_4"
        return "neither"

    ### SUMMARY ###

    @classmethod
    def _build_summary(
            cls,
            atoms: NDArray[np.float64],
            dists_to_carbon: NDArray[np.float64],
            dists_to_inter: NDArray[np.float64],
            dists_to_planes: NDArray[np.float64],
            nearest_carbon_spreads: NDArray[np.float64],
            is_near_wall: NDArray[np.bool_],
            opposite_features: list[dict[str, Any]],
            targets: PValidationTargets,
    ) -> dict[str, Any]:
        """Aggregate the per-atom measurements."""
        feature_counts: dict[str, int] = {"hexagon": 0, "pentagon": 0, "edge_hole": 0, "none": 0}
        for feature in opposite_features:
            key: str = feature["opposite_feature"] or "none"
            feature_counts[key] += 1

        dev_from_target_carbon: NDArray[np.float64] = cls._deviation_percents(
            dists_to_carbon, targets.target_dist_to_carbon
        )

        return {
            "num_of_near_wall_atoms": int(np.sum(is_near_wall)),
            "num_of_central_atoms": int(np.sum(~is_near_wall)),
            "min_dist_to_carbon": cls._describe_values(dists_to_carbon),
            "dev_from_target_carbon_percent": cls._describe_values(dev_from_target_carbon),
            # The values that rule 1 is actually judged on, and the central atoms it exempts.
            "min_dist_to_carbon_near_wall": cls._describe_values(dists_to_carbon[is_near_wall]),
            "dev_from_target_carbon_percent_near_wall": cls._describe_values(
                dev_from_target_carbon[is_near_wall]
            ),
            "min_dist_to_carbon_central": cls._describe_values(dists_to_carbon[~is_near_wall]),
            "min_dist_to_inter": cls._describe_values(dists_to_inter),
            "dev_from_target_inter_percent": cls._describe_values(
                cls._deviation_percents(dists_to_inter, targets.target_dist_between_inter_atoms)
            ),
            "min_dist_to_plane": cls._describe_values(dists_to_planes),
            "nearest_carbon_spread": cls._describe_values(nearest_carbon_spreads),
            "z_range": [
                round(float(atoms[:, 2].min()), cls.ROUND_DECIMALS),
                round(float(atoms[:, 2].max()), cls.ROUND_DECIMALS),
            ],
            "num_of_atoms_opposite": feature_counts,
        }

    @classmethod
    def _describe_values(cls, values: NDArray[np.float64]) -> dict[str, float | None]:
        """Min / max / mean / median of the values, ignoring NaNs."""
        finite: NDArray[np.float64] = values[~np.isnan(values)]

        if len(finite) == 0:
            return {"min": None, "max": None, "mean": None, "median": None}

        return {
            "min": round(float(np.min(finite)), cls.ROUND_DECIMALS),
            "max": round(float(np.max(finite)), cls.ROUND_DECIMALS),
            "mean": round(float(np.mean(finite)), cls.ROUND_DECIMALS),
            "median": round(float(np.median(finite)), cls.ROUND_DECIMALS),
        }

    @staticmethod
    def _deviation_percent(value: float, target: float) -> float | None:
        """Deviation of a measured distance from its target, in percent."""
        if target == 0:
            return None
        return round((value - target) / target * 100, 2)

    @staticmethod
    def _deviation_percents(values: NDArray[np.float64], target: float) -> NDArray[np.float64]:
        """Deviations of the measured distances from their target, in percent."""
        if target == 0:
            return np.array([np.nan] * len(values))
        return (values - target) / target * 100

    @classmethod
    def _round_or_none(cls, value: np.float64 | float) -> float | None:
        """Round a value, mapping NaN to None so it survives JSON serialization."""
        if np.isnan(value):
            return None
        return round(float(value), cls.ROUND_DECIMALS)
