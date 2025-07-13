from pathlib import Path
from typing import Any
import json
from dataclasses import dataclass, asdict

from src.interfaces import IDataConverterModel
from src.services import Constants, Logger, FileReader, FileWriter

logger = Logger("DataConverterModel")


@dataclass
class ConversionState:
    """State for data conversion operations."""
    last_project_dir: str = ""
    last_subproject_dir: str = ""
    last_structure_dir: str = ""
    last_file_name: str = ""
    last_target_format: str = ""
    conversion_history: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.conversion_history is None:
            self.conversion_history = []


class DataConverterModel(IDataConverterModel):
    """Model for data converter functionality."""

    def __init__(self):
        self.mvp_name = "data_converter"
        self._state = ConversionState()
        self._load_state()

    def get_available_formats(self) -> list[str]:
        """Get list of available file formats."""
        return ["xlsx", "dat", "pdb"]

    def get_conversion_state(self) -> dict[str, Any]:
        """Get current conversion state."""
        return asdict(self._state)

    def set_conversion_state(self, state: dict[str, Any]) -> None:
        """Set conversion state."""
        self._state = ConversionState(**state)
        self._save_state()

    def save_conversion_history(self, conversion_info: dict[str, Any]) -> None:
        """Save conversion operation to history."""
        self._state.conversion_history.append(conversion_info)
        # Keep only last 100 conversions
        if len(self._state.conversion_history) > 100:
            self._state.conversion_history = self._state.conversion_history[-100:]
        self._save_state()

    def get_conversion_history(self) -> list[dict[str, Any]]:
        """Get conversion history."""
        return self._state.conversion_history.copy()

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
                    self._state = ConversionState(**state_data)
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
            self._state = ConversionState()

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