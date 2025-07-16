"""Model for intercalation and sorption functionality."""
from pathlib import Path
from typing import Any
import pandas as pd

from src.interfaces import IIntercalationAndSorptionModel
from src.mvp.general import GeneralModel
from src.services import Logger, FileReader, PathBuilder

logger = Logger("IntercalationAndSorptionModel")


class IntercalationAndSorptionModel(GeneralModel, IIntercalationAndSorptionModel):
    """Model for intercalation and sorption functionality."""

    def __init__(self) -> None:
        super().__init__()
        self._intercalation_parameters: dict[str, Any] = {}
        self._visualization_settings: dict[str, Any] = {}
        self._coordinate_limits: dict[str, float] = {}
        self._operation_history: list[dict[str, Any]] = []

    def get_intercalation_parameters(self) -> dict[str, Any]:
        """Get intercalation parameters."""
        return self._intercalation_parameters.copy()

    def set_intercalation_parameters(self, parameters: dict[str, Any]) -> None:
        """Set intercalation parameters."""
        self._intercalation_parameters = parameters.copy()

    def get_visualization_settings(self) -> dict[str, Any]:
        """Get visualization settings."""
        return self._visualization_settings.copy()

    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        self._visualization_settings = settings.copy()

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits."""
        return self._coordinate_limits.copy()

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits."""
        self._coordinate_limits = limits.copy()

    def save_operation_history(self, operation_info: dict[str, Any]) -> None:
        """Save operation to history."""
        self._operation_history.append(operation_info)

    def get_operation_history(self) -> list[dict[str, Any]]:
        """Get operation history."""
        return self._operation_history.copy()

    def get_channel_constants(self, structure_info: dict[str, str]) -> pd.DataFrame:
        """Get intercalation constants for the structure."""
        # TODO: Implement actual constants calculation
        # This would typically involve reading structure files and calculating intercalation constants
        return pd.DataFrame({
            "Parameter": ["Channel Diameter", "Intercalation Energy", "Binding Strength"],
            "Value": [1.2, -0.5, 2.3],
            "Unit": ["Å", "eV", "eV/Å"]
        })

    def get_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> list[str]:
        """Get list of available intercalated structure files (.xlsx) from result directory."""
        try:
            # Look for .xlsx files in result_data directory (intercalated structure files)
            result_data_path: Path = PathBuilder.build_path_to_result_data_dir(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
            )
            
            if not result_data_path.exists():
                return ["No files found"]
            
            # Get .xlsx files specifically (intercalated structure files)
            files: list[str] = FileReader.read_list_of_files(result_data_path, format=".xlsx", to_include_nested_files=True)
            
            if not files:
                return ["No files found"]
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to get available files: {e}")
            return ["No files found"]
