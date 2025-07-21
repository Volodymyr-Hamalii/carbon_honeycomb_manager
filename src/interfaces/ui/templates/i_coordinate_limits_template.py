from abc import ABC, abstractmethod
from typing import Callable


class ICoordinateLimitsTemplate(ABC):
    """Interface for coordinate limits template."""

    @abstractmethod
    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits in the UI."""
        ...

    @abstractmethod
    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits from the UI."""
        ...

    @abstractmethod
    def set_change_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for coordinate limit changes."""
        ...

    @abstractmethod
    def pack(self, **kwargs) -> None:
        """Pack the coordinate limits template."""
        ...

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the coordinate limits template."""
        ...