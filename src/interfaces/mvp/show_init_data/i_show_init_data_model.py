from abc import abstractmethod
from typing import Any
import pandas as pd

from src.interfaces.mvp.general import IGeneralModel


class IShowInitDataModel(IGeneralModel):
    """Interface for show init data model."""

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
    def get_channel_display_settings(self) -> dict[str, Any]:
        """Get channel display settings."""
        ...

    @abstractmethod
    def set_channel_display_settings(self, settings: dict[str, Any]) -> None:
        """Set channel display settings."""
        ...

    @abstractmethod
    def save_view_state(self, state: dict[str, Any]) -> None:
        """Save current view state."""
        ...

    @abstractmethod
    def get_view_state(self) -> dict[str, Any]:
        """Get saved view state."""
        ...

    @abstractmethod
    def get_channel_parameters(self, structure_info: dict[str, str]) -> pd.DataFrame:
        """Get channel parameters for the structure."""
        ...

    @abstractmethod
    def get_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> list[str]:
        """Get list of available files in init_data directory."""
        ...

    @abstractmethod
    def show_init_structure(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Show 3D model of initial structure."""
        ...

    @abstractmethod
    def show_one_channel_structure(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Show one channel structure."""
        ...

    @abstractmethod
    def show_2d_channel_scheme(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Show 2D channel scheme."""
        ...
