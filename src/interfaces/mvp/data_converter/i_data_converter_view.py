from abc import abstractmethod
from pathlib import Path
from typing import Callable

from src.interfaces.mvp.general import IGeneralView


class IDataConverterView(IGeneralView):
    """Interface for data converter view."""

    @abstractmethod
    def set_available_formats(self, formats: list[str]) -> None:
        """Set available formats in the UI."""
        ...

    @abstractmethod
    def show_conversion_progress(self, message: str) -> None:
        """Show conversion progress to user."""
        ...

    @abstractmethod
    def show_conversion_success(self, output_path: Path) -> None:
        """Show successful conversion result."""
        ...

    @abstractmethod
    def show_conversion_error(self, error_message: str) -> None:
        """Show conversion error to user."""
        ...

    @abstractmethod
    def get_conversion_parameters(self) -> dict[str, str]:
        """Get conversion parameters from UI."""
        ...

    @abstractmethod
    def set_conversion_callback(self, callback: Callable) -> None:
        """Set callback for conversion button."""
        ...

    @abstractmethod
    def reset_form(self) -> None:
        """Reset the conversion form."""
        ...
