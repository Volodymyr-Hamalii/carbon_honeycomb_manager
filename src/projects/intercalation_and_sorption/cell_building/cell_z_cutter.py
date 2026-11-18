"""Cut an elementary cell along Oz: the minimal height after which carbon and intercalated atoms repeat."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist

from src.projects.intercalation_and_sorption.validation import StructureValidator
from src.services import Logger


logger = Logger("CellZCutter")


@dataclass(frozen=True)
class ZCellResult:
    """Result of the Oz cut of an elementary cell."""

    carbon: NDArray[np.float64]
    intercalated: NDArray[np.float64]
    carbon_z_period: float
    num_of_periods: int
    cell_height: float
    z_start: float
    verified: bool


class CellZCutter:
    """
    Find the cell height `c = n * c_C` and cut carbon and intercalated atoms to `[z0, z0 + c)`.

    `c_C` is the exact Oz period of the carbon structure, `n` is the smallest multiplier for which the
    intercalated atoms map onto themselves; carbon then repeats automatically. `z0` is the lowest carbon
    z coordinate.
    """

    TOLERANCE: float = 0.1
    MAX_NUM_OF_PERIODS: int = 20
    MIN_OVERLAP_ATOMS: int = 2

    # Atoms lying this close to the upper boundary of the window are numerical copies of the lower ones.
    BOUNDARY_TOLERANCE: float = 0.01

    @classmethod
    def build_cell(
            cls,
            carbon_all: NDArray[np.float64],
            carbon_in_prism: NDArray[np.float64],
            inter_in_prism: NDArray[np.float64],
            tolerance: float = TOLERANCE,
            min_overlap_atoms: int = MIN_OVERLAP_ATOMS,
    ) -> ZCellResult:
        """
        Cut carbon and intercalated atoms (both already filtered by the xy prism) to one elementary cell.

        Args:
            carbon_all: the whole initial carbon structure, used to measure the carbon period and `z0`.
            carbon_in_prism: carbon atoms inside the xy prism.
            inter_in_prism: intercalated atoms inside the xy prism, not clipped along Oz.
        """
        if len(inter_in_prism) == 0:
            raise ValueError("No intercalated atoms found inside the xy prism.")

        carbon_period: float = cls.find_exact_carbon_period(carbon_all, tolerance)
        z_start: float = float(carbon_all[:, 2].min())
        logger.info(f"Carbon z period: {carbon_period:.6f}, z start: {z_start:.6f}")

        num_of_periods: int | None = cls.find_num_of_periods(
            inter_in_prism, carbon_period, tolerance, min_overlap_atoms
        )
        verified: bool = num_of_periods is not None

        if num_of_periods is None:
            num_of_periods = cls.estimate_num_of_periods(inter_in_prism, carbon_period)
            logger.warning(
                "The z repeat is not confirmed by an overlap, "
                f"using the file height: {num_of_periods} carbon period(s)."
            )

        cell_height: float = num_of_periods * carbon_period
        lower_bound: float = z_start - cls.BOUNDARY_TOLERANCE

        carbon_one_period: NDArray[np.float64] = carbon_in_prism[
            (carbon_in_prism[:, 2] >= lower_bound)
            & (carbon_in_prism[:, 2] < lower_bound + carbon_period)
        ]
        if len(carbon_one_period) == 0:
            raise ValueError("No carbon atoms found inside the prism within one z period.")

        carbon_cell: NDArray[np.float64] = np.vstack([
            carbon_one_period + np.array([0.0, 0.0, k * carbon_period])
            for k in range(num_of_periods)
        ])

        inter_cell: NDArray[np.float64] = inter_in_prism[
            (inter_in_prism[:, 2] >= lower_bound)
            & (inter_in_prism[:, 2] < lower_bound + cell_height)
        ]
        if len(inter_cell) == 0:
            raise ValueError("No intercalated atoms found inside the cell height window.")

        return ZCellResult(
            carbon=carbon_cell[np.argsort(carbon_cell[:, 2], kind="stable")],
            intercalated=inter_cell[np.argsort(inter_cell[:, 2], kind="stable")],
            carbon_z_period=carbon_period,
            num_of_periods=num_of_periods,
            cell_height=cell_height,
            z_start=z_start,
            verified=verified,
        )

    @classmethod
    def find_exact_carbon_period(
            cls,
            carbon: NDArray[np.float64],
            tolerance: float = TOLERANCE,
    ) -> float:
        """Find the carbon Oz period and refine it to the unrounded value from matched atom pairs."""
        coarse_period: float | None = StructureValidator.find_z_period(carbon, tolerance)
        if coarse_period is None:
            raise ValueError("Cannot find the z period of the carbon structure.")

        z_min: float = float(carbon[:, 2].min())
        upper_atoms: NDArray[np.float64] = carbon[carbon[:, 2] >= z_min + coarse_period - tolerance]
        shift: NDArray[np.float64] = np.array([0.0, 0.0, coarse_period])

        distances, indexes = cKDTree(carbon).query(upper_atoms - shift)
        matched: NDArray[np.bool_] = distances <= tolerance
        if not np.any(matched):
            return coarse_period

        return float(np.mean(upper_atoms[matched, 2] - carbon[indexes[matched], 2]))

    @classmethod
    def check_shift(
            cls,
            points: NDArray[np.float64],
            shift: float,
            tolerance: float = TOLERANCE,
            min_overlap_atoms: int = MIN_OVERLAP_ATOMS,
    ) -> bool | None:
        """
        Check that shifting the points up by `shift` maps them onto themselves over the overlap region.

        True means a match confirmed by at least `min_overlap_atoms` atoms (or by the whole lowest layer
        when the z extent equals the shift), False a mismatch, None that nothing could be confirmed.
        """
        z_min: float = float(points[:, 2].min())
        z_max: float = float(points[:, 2].max())

        original: NDArray[np.float64] = points[points[:, 2] >= z_min + shift - tolerance]
        shifted_all: NDArray[np.float64] = points + np.array([0.0, 0.0, shift])
        shifted: NDArray[np.float64] = shifted_all[shifted_all[:, 2] <= z_max + tolerance]

        if len(original) != len(shifted):
            return False
        if len(original) == 0:
            return None

        distances: NDArray[np.float64] = cdist(original, shifted)
        if not (np.all(distances.min(axis=1) <= tolerance) and np.all(distances.min(axis=0) <= tolerance)):
            return False

        if len(original) >= min_overlap_atoms:
            return True

        # The file is the cell plus its own repeat: the whole lowest layer maps onto the whole top layer.
        spans_exactly_one_shift: bool = abs((z_max - z_min) - shift) <= tolerance
        return True if spans_exactly_one_shift else None

    @classmethod
    def find_num_of_periods(
            cls,
            inter: NDArray[np.float64],
            carbon_period: float,
            tolerance: float = TOLERANCE,
            min_overlap_atoms: int = MIN_OVERLAP_ATOMS,
    ) -> int | None:
        """Smallest `n` for which the intercalated atoms repeat after `n` carbon periods, or None."""
        for num_of_periods in range(1, cls.MAX_NUM_OF_PERIODS + 1):
            if cls.check_shift(inter, num_of_periods * carbon_period, tolerance, min_overlap_atoms) is True:
                return num_of_periods

        return None

    @classmethod
    def estimate_num_of_periods(cls, inter: NDArray[np.float64], carbon_period: float) -> int:
        """Fallback: the file height (z extent plus the median layer step) in carbon periods."""
        levels: NDArray[np.float64] = np.unique(np.round(inter[:, 2], 3))
        if len(levels) < 2:
            return 1

        extent: float = float(levels[-1] - levels[0])
        layer_step: float = float(np.median(np.diff(levels)))

        return max(1, int(round((extent + layer_step) / carbon_period)))
