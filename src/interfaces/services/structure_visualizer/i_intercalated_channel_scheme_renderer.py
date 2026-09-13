"""Contract for rendering an intercalated-channel scheme."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from src.entities import IntercalatedChannelSchemeData


class IIntercalatedChannelSchemeRenderer(ABC):
    """Render prepared scheme data without domain calculations."""

    @abstractmethod
    def render(self, data: IntercalatedChannelSchemeData) -> Figure:
        """Render both 2D schemes into one figure."""
        ...
