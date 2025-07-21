from abc import abstractmethod
from pathlib import Path
from typing import Any, Callable
import pandas as pd

from src.interfaces.mvp.general import IGeneralView


class IIntercalationAndSorptionView(IGeneralView):
    """Interface for intercalation and sorption view."""

    @abstractmethod
    def set_intercalation_parameters(self, parameters: dict[str, Any]) -> None:
        """Set intercalation parameters in the UI."""
        ...

    @abstractmethod
    def get_intercalation_parameters(self) -> dict[str, Any]:
        """Get intercalation parameters from the UI."""
        ...

    @abstractmethod
    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings in the UI."""
        ...

    @abstractmethod
    def get_visualization_settings(self) -> dict[str, Any]:
        """Get visualization settings from the UI."""
        ...

    @abstractmethod
    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits in the UI."""
        ...

    @abstractmethod
    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits from the UI."""
        ...

    @abstractmethod
    def show_operation_progress(self, message: str) -> None:
        """Show operation progress to user."""
        ...

    @abstractmethod
    def show_operation_success(self, message: str, result_path: Path | None = None) -> None:
        """Show successful operation result."""
        ...

    @abstractmethod
    def show_operation_error(self, error_message: str) -> None:
        """Show operation error to user."""
        ...

    @abstractmethod
    def display_channel_details(self, details: pd.DataFrame) -> None:
        """Display channel details in the UI."""
        ...

    @abstractmethod
    def display_channel_constants(self, constants: pd.DataFrame) -> None:
        """Display channel constants in the UI."""
        ...

    @abstractmethod
    def set_operation_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for operation buttons."""
        ...

    @abstractmethod
    def enable_controls(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        ...

    @abstractmethod
    def get_selected_file(self) -> str:
        """Get currently selected file."""
        ...

    @abstractmethod
    def set_available_files(self, files: list[str]) -> None:
        """Set available files in dropdown."""
        ...

    @abstractmethod
    def get_operation_settings(self) -> dict[str, Any]:
        """Get operation settings from the UI."""
        ...

    @abstractmethod
    def reset_form(self) -> None:
        """Reset the form to default values."""
        ...
