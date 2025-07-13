from typing import Any

from src.interfaces import IDataConverterModel
from src.mvp.general import GeneralModel
from src.entities import MvpParams
from src.services import Logger

logger = Logger("DataConverterModel")


class DataConverterModel(GeneralModel, IDataConverterModel):
    """Model for data converter functionality."""
    mvp_name: str = "data_converter"

    def __init__(self) -> None:
        super().__init__()

    def get_available_formats(self) -> list[str]:
        """Get list of available file formats."""
        return ["xlsx", "dat", "pdb"]

    def get_conversion_state(self) -> dict[str, Any]:
        """Get current conversion state."""
        params = self.get_mvp_params()
        return {
            "last_project_dir": params.current_selection.get("project_dir", ""),
            "last_subproject_dir": params.current_selection.get("subproject_dir", ""),
            "last_structure_dir": params.current_selection.get("structure_dir", ""),
            "last_file_name": params.file_name or "",
            "last_target_format": params.file_format or "",
        }

    def set_conversion_state(self, state: dict[str, Any]) -> None:
        """Set conversion state."""
        params = self.get_mvp_params()
        if "last_project_dir" in state:
            params.current_selection["project_dir"] = state["last_project_dir"]
        if "last_subproject_dir" in state:
            params.current_selection["subproject_dir"] = state["last_subproject_dir"]
        if "last_structure_dir" in state:
            params.current_selection["structure_dir"] = state["last_structure_dir"]
        if "last_file_name" in state:
            params.file_name = state["last_file_name"]
        if "last_target_format" in state:
            params.file_format = state["last_target_format"]
        self.set_mvp_params(params)

    def save_conversion_history(self, conversion_info: dict[str, Any]) -> None:
        """Save conversion operation to history."""
        params = self.get_mvp_params()
        params.session_history.append({"type": "conversion", **conversion_info})
        # Keep only last 100 operations
        if len(params.session_history) > 100:
            params.session_history = params.session_history[-100:]
        self.set_mvp_params(params)

    def get_conversion_history(self) -> list[dict[str, Any]]:
        """Get conversion history."""
        params = self.get_mvp_params()
        return [item for item in params.session_history if item.get("type") == "conversion"]

