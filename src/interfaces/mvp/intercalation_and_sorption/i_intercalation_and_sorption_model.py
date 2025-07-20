from abc import abstractmethod
from typing import Any
import pandas as pd

from src.interfaces.mvp.general import IGeneralModel


class IIntercalationAndSorptionModel(IGeneralModel):
    """Interface for intercalation and sorption model."""

    # @abstractmethod
    # def get_intercalation_parameters(self) -> dict[str, Any]:
    #     """Get intercalation parameters."""
    #     ...

    # @abstractmethod
    # def set_intercalation_parameters(self, parameters: dict[str, Any]) -> None:
    #     """Set intercalation parameters."""
    #     ...

    @abstractmethod
    def get_visualization_settings(self) -> dict[str, Any]:
        """Get visualization settings."""
        ...

    @abstractmethod
    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        ...

    @abstractmethod
    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits."""
        ...

    @abstractmethod
    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits."""
        ...

    @abstractmethod
    def save_operation_history(self, operation_info: dict[str, Any]) -> None:
        """Save operation to history."""
        ...

    @abstractmethod
    def get_operation_history(self) -> list[dict[str, Any]]:
        """Get operation history."""
        ...

    @abstractmethod
    def get_channel_constants(self, structure_info: dict[str, str]) -> pd.DataFrame:
        """Get intercalation constants for the structure."""
        ...

    @abstractmethod
    def get_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> list[str]:
        """Get list of available intercalated structure files (.xlsx) from result directory."""
        ...
