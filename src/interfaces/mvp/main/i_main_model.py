from abc import ABC, abstractmethod
from typing import Any


class IMainModel(ABC):
    """Interface for main model."""

    @abstractmethod
    def get_projects(self) -> list[str]:
        """Get list of available projects."""
        ...

    @abstractmethod
    def get_subprojects(self, project_dir: str) -> list[str]:
        """Get list of subprojects for a given project."""
        ...

    @abstractmethod
    def get_structures(self, project_dir: str, subproject_dir: str) -> list[str]:
        """Get list of structures for a given project and subproject."""
        ...

    @abstractmethod
    def get_current_selection(self) -> dict[str, str]:
        """Get current project/subproject/structure selection."""
        ...

    @abstractmethod
    def set_current_selection(self, selection: dict[str, str]) -> None:
        """Set current project/subproject/structure selection."""
        ...

    @abstractmethod
    def get_application_settings(self) -> dict[str, Any]:
        """Get application settings."""
        ...

    @abstractmethod
    def set_application_settings(self, settings: dict[str, Any]) -> None:
        """Set application settings."""
        ...

    @abstractmethod
    def save_session_state(self, state: dict[str, Any]) -> None:
        """Save current session state."""
        ...

    @abstractmethod
    def get_session_state(self) -> dict[str, Any]:
        """Get saved session state."""
        ...