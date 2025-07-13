from pathlib import Path
from typing import Any

from src.interfaces import IMainModel
from src.services import Constants, Logger
from src.mvp.general import GeneralModel
from src.entities import MvpParams


logger = Logger("MainModel")


class MainModel(GeneralModel, IMainModel):
    """Main application model."""
    mvp_name: str = "main"

    def __init__(self) -> None:
        super().__init__()

    def get_projects(self) -> list[str]:
        """Get list of available projects."""
        try:
            projects_path = Constants.path.PROJECTS_DATA_PATH
            if not projects_path.exists():
                return []

            return [d.name for d in projects_path.iterdir() if d.is_dir()]
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []

    def get_subprojects(self, project_dir: str) -> list[str]:
        """Get list of subprojects for a given project."""
        try:
            project_path = Constants.path.PROJECTS_DATA_PATH / project_dir
            if not project_path.exists():
                return []

            return [d.name for d in project_path.iterdir() if d.is_dir()]
        except Exception as e:
            logger.error(f"Failed to get subprojects for {project_dir}: {e}")
            return []

    def get_structures(self, project_dir: str, subproject_dir: str) -> list[str]:
        """Get list of structures for a given project and subproject."""
        try:
            # Look in both init_data and result_data directories
            init_data_path = Constants.path.PROJECTS_DATA_PATH / project_dir / subproject_dir / "init_data"
            result_data_path = Constants.path.PROJECTS_DATA_PATH / project_dir / subproject_dir / "result_data"

            structures = set()

            if init_data_path.exists():
                structures.update(d.name for d in init_data_path.iterdir() if d.is_dir())

            if result_data_path.exists():
                structures.update(d.name for d in result_data_path.iterdir() if d.is_dir())

            return sorted(list(structures))
        except Exception as e:
            logger.error(f"Failed to get structures for {project_dir}/{subproject_dir}: {e}")
            return []

    def get_current_selection(self) -> dict[str, str]:
        """Get current project/subproject/structure selection."""
        params = self.get_mvp_params()
        return params.current_selection.copy()

    def set_current_selection(self, selection: dict[str, str]) -> None:
        """Set current project/subproject/structure selection."""
        params = self.get_mvp_params()
        params.current_selection = selection
        self.set_mvp_params(params)

    def get_application_settings(self) -> dict[str, Any]:
        """Get application settings."""
        params = self.get_mvp_params()
        return params.application_settings.copy()

    def set_application_settings(self, settings: dict[str, Any]) -> None:
        """Set application settings."""
        params = self.get_mvp_params()
        params.application_settings = settings
        self.set_mvp_params(params)

    def save_session_state(self, state: dict[str, Any]) -> None:
        """Save current session state."""
        params = self.get_mvp_params()
        params.session_history.append(state)
        # Keep only last 50 sessions
        if len(params.session_history) > 50:
            params.session_history = params.session_history[-50:]
        self.set_mvp_params(params)

    def get_session_state(self) -> dict[str, Any]:
        """Get saved session state."""
        params = self.get_mvp_params()
        if params.session_history:
            return params.session_history[-1]
        return {}

