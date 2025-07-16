from abc import abstractmethod
from typing import Any

from src.interfaces.mvp.general import IGeneralModel


class IDataConverterModel(IGeneralModel):
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

    @abstractmethod
    def get_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> list[str]:
        """Get list of available files for conversion."""
        ...
