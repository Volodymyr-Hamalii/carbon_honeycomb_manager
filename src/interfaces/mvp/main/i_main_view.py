from abc import abstractmethod
from typing import Any, Callable

from src.interfaces.mvp.general import IGeneralView


class IMainView(IGeneralView):
    """Interface for main view."""

    @abstractmethod
    def set_projects(self, projects: list[str]) -> None:
        """Set projects list in the UI."""
        ...

    @abstractmethod
    def set_subprojects(self, subprojects: list[str]) -> None:
        """Set subprojects list in the UI."""
        ...

    @abstractmethod
    def set_structures(self, structures: list[str]) -> None:
        """Set structures list in the UI."""
        ...

    @abstractmethod
    def get_selected_project(self) -> str:
        """Get selected project from the UI."""
        ...

    @abstractmethod
    def get_selected_subproject(self) -> str:
        """Get selected subproject from the UI."""
        ...

    @abstractmethod
    def get_selected_structure(self) -> str:
        """Get selected structure from the UI."""
        ...

    @abstractmethod
    def set_selected_project(self, project: str) -> None:
        """Set selected project in the UI."""
        ...

    @abstractmethod
    def set_selected_subproject(self, subproject: str) -> None:
        """Set selected subproject in the UI."""
        ...

    @abstractmethod
    def set_selected_structure(self, structure: str) -> None:
        """Set selected structure in the UI."""
        ...

    @abstractmethod
    def set_selection_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for selection changes."""
        ...

    @abstractmethod
    def set_action_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for action buttons."""
        ...

    @abstractmethod
    def show_status_message(self, message: str) -> None:
        """Show status message to user."""
        ...

    @abstractmethod
    def show_error_message(self, message: str) -> None:
        """Show error message to user."""
        ...

    @abstractmethod
    def enable_actions(self, enabled: bool) -> None:
        """Enable or disable action buttons."""
        ...

    @abstractmethod
    def set_application_settings(self, settings: dict[str, Any]) -> None:
        """Set application settings in the UI."""
        ...

    @abstractmethod
    def show_about_dialog(self) -> None:
        """Show about dialog."""
        ...
