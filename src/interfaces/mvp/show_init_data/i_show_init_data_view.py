from abc import abstractmethod
from typing import Any, Callable
import pandas as pd

from src.interfaces.mvp.general import IGeneralView


class IShowInitDataView(IGeneralView):
    """Interface for show init data view."""

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
    def set_channel_display_settings(self, settings: dict[str, Any]) -> None:
        """Set channel display settings in the UI."""
        ...

    @abstractmethod
    def get_channel_display_settings(self) -> dict[str, Any]:
        """Get channel display settings from the UI."""
        ...

    @abstractmethod
    def show_visualization_progress(self, message: str) -> None:
        """Show visualization progress to user."""
        ...

    @abstractmethod
    def show_visualization_success(self, message: str) -> None:
        """Show successful visualization result."""
        ...

    @abstractmethod
    def show_visualization_error(self, error_message: str) -> None:
        """Show visualization error to user."""
        ...

    @abstractmethod
    def display_channel_parameters(self, parameters: pd.DataFrame) -> None:
        """Display channel parameters in the UI."""
        ...

    @abstractmethod
    def set_visualization_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for visualization buttons."""
        ...

    @abstractmethod
    def enable_controls(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        ...

    @abstractmethod
    def reset_form(self) -> None:
        """Reset the form to default values."""
        ...
