from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import pandas as pd


class IIntercalationAndSorptionPresenter(ABC):
    """Interface for intercalation and sorption presenter."""

    @abstractmethod
    def plot_inter_in_c_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Plot intercalated atoms in carbon structure."""
        ...

    @abstractmethod
    def generate_inter_plane_coordinates_file(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Generate intercalated atoms plane coordinates file."""
        ...

    @abstractmethod
    def update_inter_plane_coordinates_file(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Update intercalated atoms plane coordinates file."""
        ...

    @abstractmethod
    def translate_inter_atoms_to_other_planes(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Translate intercalated atoms to other planes."""
        ...

    @abstractmethod
    def update_inter_channel_coordinates(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Update intercalated atoms channel coordinates."""
        ...

    @abstractmethod
    def save_inter_in_channel_details(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Save intercalated atoms in channel details."""
        ...

    @abstractmethod
    def get_inter_in_channel_details(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> pd.DataFrame:
        """Get intercalated atoms in channel details."""
        ...

    @abstractmethod
    def translate_inter_to_all_channels_plot(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Plot intercalated atoms translated to all channels."""
        ...

    @abstractmethod
    def translate_inter_to_all_channels_generate_files(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> tuple[Path, Path, Path]:
        """Generate files for intercalated atoms in all channels."""
        ...

    @abstractmethod
    def set_intercalation_parameters(self, parameters: dict[str, Any]) -> None:
        """Set intercalation parameters."""
        ...

    @abstractmethod
    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        ...

    @abstractmethod
    def on_operation_completed(self, operation_type: str, result: Any) -> None:
        """Handle operation completion."""
        ...

    @abstractmethod
    def on_operation_failed(self, operation_type: str, error: Exception) -> None:
        """Handle operation failure."""
        ...