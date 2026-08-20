from abc import ABC, abstractmethod
from typing import Any

from src.interfaces.entities.figures.i_points import IPoints


class ICandidateComparator(ABC):
    """Interface for permutation-invariant structure comparison."""

    @staticmethod
    @abstractmethod
    def compare(
            candidate_a: IPoints,
            candidate_b: IPoints,
            distinct_rmsd_threshold: float,
            z_period: float | None = None,
    ) -> dict[str, Any]:
        ...
