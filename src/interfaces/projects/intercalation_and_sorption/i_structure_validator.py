from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints
from src.interfaces.entities.params.p_validation_targets import PValidationTargets
from src.interfaces.projects.carbon_honeycomb_actions.channel.i_carbon_honeycomb_channel import (
    ICarbonHoneycombChannel,
)


class IStructureValidator(ABC):
    """
    Interface for the numeric validation report of an intercalated structure.

    The validator only measures and flags: it takes every target and tolerance as a parameter and
    never decides whether a structure is acceptable. That decision belongs to the caller (a skill),
    so different sets of rules can reuse the same validator.
    """

    @classmethod
    @abstractmethod
    def build_report(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            inter_atoms: IPoints,
            targets: PValidationTargets,
    ) -> dict[str, Any]:
        ...

    @classmethod
    @abstractmethod
    def find_z_period(
            cls,
            points: NDArray[np.float64],
            tolerance: float,
    ) -> float | None:
        ...

    @classmethod
    @abstractmethod
    def find_min_z_period_multiplier(
            cls,
            points: NDArray[np.float64],
            z_period: float,
            tolerance: float,
            max_multiplier: int,
    ) -> int | None:
        ...

    @classmethod
    @abstractmethod
    def check_z_periodicity(
            cls,
            points: NDArray[np.float64],
            z_period: float,
            tolerance: float,
            max_multiplier: int,
    ) -> dict[str, Any]:
        ...
