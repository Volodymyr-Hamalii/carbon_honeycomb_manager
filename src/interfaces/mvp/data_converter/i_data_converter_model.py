from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class IDataConverterModel(ABC):
    """Interface for data converter model."""

    @abstractmethod
    def get_available_formats(self) -> list[str]:
        """Get list of available file formats."""
        ...

    @abstractmethod
    def get_conversion_state(self) -> dict[str, Any]:
        """Get current conversion state."""
        ...

    @abstractmethod
    def set_conversion_state(self, state: dict[str, Any]) -> None:
        """Set conversion state."""
        ...

    @abstractmethod
    def save_conversion_history(self, conversion_info: dict[str, Any]) -> None:
        """Save conversion operation to history."""
        ...

    @abstractmethod
    def get_conversion_history(self) -> list[dict[str, Any]]:
        """Get conversion history."""
        ...