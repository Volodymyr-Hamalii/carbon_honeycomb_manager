"""Contract for preparing an intercalated-channel 2D scheme."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.entities import IntercalatedChannelSchemeData
    from src.interfaces.entities.figures import IPoints
    from src.interfaces.projects.carbon_honeycomb_actions import ICarbonHoneycombChannel
    from src.services.utils.constants_phys import ConstantsAtomParams


class IIntercalatedChannelSchemeBuilder(ABC):
    """Build immutable scheme data without plotting or file writes."""

    @abstractmethod
    def build(
        self,
        carbon_channel: ICarbonHoneycombChannel,
        inter_atoms: IPoints,
        atom_params: ConstantsAtomParams,
        file_name: str,
    ) -> IntercalatedChannelSchemeData:
        """Build data for both 2D intercalated-channel schemes."""
        ...
