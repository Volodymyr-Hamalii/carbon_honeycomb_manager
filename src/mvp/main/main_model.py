from pathlib import Path
from typing import Any
import json
from dataclasses import dataclass, asdict

from src.interfaces import IMainModel
from src.services import Constants, Logger, FileReader, FileWriter
from src.mvp.general import GeneralModel

logger = Logger("MainModel")


@dataclass
class ApplicationState:
    """State for main application."""
    current_selection: dict[str, str] = None
    application_settings: dict[str, Any] = None
    session_history: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.current_selection is None:
            self.current_selection = {"project_dir": "", "subproject_dir": "", "structure_dir": ""}
        if self.application_settings is None:
            self.application_settings = {}
        if self.session_history is None:
            self.session_history = []


class MainModel(GeneralModel, IMainModel):
    """Main application model."""
    mvp_name: str = "main"

    def __init__(self):
        super().__init__()
        self._state = ApplicationState()
        self._load_state()

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
        return self._state.current_selection.copy()

    def set_current_selection(self, selection: dict[str, str]) -> None:
        """Set current project/subproject/structure selection."""
        self._state.current_selection = selection
        self._save_state()

    def get_application_settings(self) -> dict[str, Any]:
        """Get application settings."""
        return self._state.application_settings.copy()

    def set_application_settings(self, settings: dict[str, Any]) -> None:
        """Set application settings."""
        self._state.application_settings = settings
        self._save_state()

    def save_session_state(self, state: dict[str, Any]) -> None:
        """Save current session state."""
        self._state.session_history.append(state)
        # Keep only last 50 sessions
        if len(self._state.session_history) > 50:
            self._state.session_history = self._state.session_history[-50:]
        self._save_state()

    def get_session_state(self) -> dict[str, Any]:
        """Get saved session state."""
        if self._state.session_history:
            return self._state.session_history[-1]
        return {}

    def _load_state(self) -> None:
        """Load state from file."""
        try:
            state_file = Constants.path.MVP_PARAMS_DATA_PATH / f"{self.mvp_name}_state.json"
            if state_file.exists():
                state_data = FileReader.read_json_file(
                    folder_path=Constants.path.MVP_PARAMS_DATA_PATH,
                    file_name=f"{self.mvp_name}_state.json",
                )
                if state_data:
                    self._state = ApplicationState(**state_data)
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
            self._state = ApplicationState()

    def _save_state(self) -> None:
        """Save state to file."""
        try:
            state_file = Constants.path.MVP_PARAMS_DATA_PATH / f"{self.mvp_name}_state.json"
            FileWriter.write_json_file(
                data=asdict(self._state),
                path_to_file=state_file,
            )
        except Exception as e:
            logger.warning(f"Failed to save state: {e}")
