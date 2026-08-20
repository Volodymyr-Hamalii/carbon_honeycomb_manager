from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment

from src.interfaces import ICandidateComparator, IPoints


class CandidateComparator(ICandidateComparator):
    """Compare unordered atom sets, optionally modulo a periodic z translation."""

    @staticmethod
    def compare(
            candidate_a: IPoints,
            candidate_b: IPoints,
            distinct_rmsd_threshold: float,
            z_period: float | None = None,
    ) -> dict[str, Any]:
        """Return the minimum assignment RMSD and whether the candidates are distinct."""
        if distinct_rmsd_threshold < 0:
            raise ValueError("distinct_rmsd_threshold must not be negative.")
        if z_period is not None and z_period <= 0:
            raise ValueError("z_period must be positive when provided.")

        count_a: int = len(candidate_a.points)
        count_b: int = len(candidate_b.points)
        if count_a != count_b:
            return {
                "same_atom_count": False,
                "num_of_atoms_a": count_a,
                "num_of_atoms_b": count_b,
                "min_assignment_rmsd": None,
                "best_z_shift": None,
                "distinct_rmsd_threshold": distinct_rmsd_threshold,
                "distinct": True,
            }
        if count_a == 0:
            return {
                "same_atom_count": True,
                "num_of_atoms_a": 0,
                "num_of_atoms_b": 0,
                "min_assignment_rmsd": 0.0,
                "best_z_shift": 0.0,
                "distinct_rmsd_threshold": distinct_rmsd_threshold,
                "distinct": False,
            }

        shifts: list[float] = [0.0]
        if z_period is not None:
            shifts = sorted({
                round(float((candidate_a.points[0, 2] - z_value) % z_period), 8)
                for z_value in candidate_b.points[:, 2]
            })

        best_rmsd: float = float("inf")
        best_shift: float = 0.0
        for shift in shifts:
            shifted_b: NDArray[np.float64] = candidate_b.points.copy()
            shifted_b[:, 2] += shift
            differences: NDArray[np.float64] = (
                candidate_a.points[:, np.newaxis, :] - shifted_b[np.newaxis, :, :]
            )
            if z_period is not None:
                z_differences: NDArray[np.float64] = differences[:, :, 2]
                differences[:, :, 2] = (
                    (z_differences + z_period / 2.0) % z_period - z_period / 2.0
                )
            squared_distances: NDArray[np.float64] = np.sum(differences ** 2, axis=2)
            row_indexes, column_indexes = linear_sum_assignment(squared_distances)
            rmsd: float = float(np.sqrt(np.mean(squared_distances[row_indexes, column_indexes])))
            if rmsd < best_rmsd:
                best_rmsd = rmsd
                best_shift = shift

        rounded_rmsd: float = round(best_rmsd, 4)
        return {
            "same_atom_count": True,
            "num_of_atoms_a": count_a,
            "num_of_atoms_b": count_b,
            "min_assignment_rmsd": rounded_rmsd,
            "best_z_shift": round(best_shift, 4),
            "distinct_rmsd_threshold": distinct_rmsd_threshold,
            "distinct": rounded_rmsd > distinct_rmsd_threshold,
        }
