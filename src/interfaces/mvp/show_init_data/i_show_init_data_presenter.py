from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class IShowInitDataPresenter(ABC):
    """Interface for show init data presenter."""

    @abstractmethod
    def show_init_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Show initial structure visualization."""
        ...

    @abstractmethod
    def show_one_channel_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Show one channel structure visualization."""
        ...

    @abstractmethod
    def show_2d_channel_scheme(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Show 2D channel scheme."""
        ...

    @abstractmethod
    def get_channel_params(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> pd.DataFrame:
        """Get channel parameters."""
        ...

    @abstractmethod
    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        ...

    @abstractmethod
    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits."""
        ...

    @abstractmethod
    def set_channel_display_settings(self, settings: dict[str, Any]) -> None:
        """Set channel display settings."""
        ...

    @abstractmethod
    def on_visualization_completed(self, visualization_type: str) -> None:
        """Handle visualization completion."""
        ...

    @abstractmethod
    def on_visualization_failed(self, visualization_type: str, error: Exception) -> None:
        """Handle visualization failure."""
        ...