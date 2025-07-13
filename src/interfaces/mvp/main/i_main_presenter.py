from abc import abstractmethod
from typing import Any

from src.interfaces.mvp.general import IGeneralPresenter


class IMainPresenter(IGeneralPresenter):
    """Interface for main presenter."""

    @abstractmethod
    def initialize_application(self) -> None:
        """Initialize the application."""
        ...

    @abstractmethod
    def set_project_selection(self, project_dir: str) -> None:
        """Set project selection and update subprojects."""
        ...

    @abstractmethod
    def set_subproject_selection(self, subproject_dir: str) -> None:
        """Set subproject selection and update structures."""
        ...

    @abstractmethod
    def set_structure_selection(self, structure_dir: str) -> None:
        """Set structure selection."""
        ...

    @abstractmethod
    def get_available_projects(self) -> list[str]:
        """Get available projects."""
        ...

    @abstractmethod
    def get_available_subprojects(self) -> list[str]:
        """Get available subprojects for current project."""
        ...

    @abstractmethod
    def get_available_structures(self) -> list[str]:
        """Get available structures for current project/subproject."""
        ...

    @abstractmethod
    def open_data_converter(self) -> None:
        """Open data converter window."""
        ...

    @abstractmethod
    def open_intercalation_and_sorption(self) -> None:
        """Open intercalation and sorption window."""
        ...

    @abstractmethod
    def open_show_init_data(self) -> None:
        """Open show init data window."""
        ...

    @abstractmethod
    def save_application_state(self) -> None:
        """Save current application state."""
        ...

    @abstractmethod
    def restore_application_state(self) -> None:
        """Restore saved application state."""
        ...

    @abstractmethod
    def on_application_closing(self) -> None:
        """Handle application closing."""
        ...
