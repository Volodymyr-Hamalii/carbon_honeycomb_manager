"""Model for init data functionality."""
from pathlib import Path
from typing import Any

from src.interfaces import IShowInitDataModel, PMvpParams
from src.mvp.general import GeneralModel
from src.services import Logger, FileReader, PathBuilder
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller


logger = Logger("InitDataModel")


class InitDataModel(GeneralModel, IShowInitDataModel):
    """Model for init data functionality."""
    mvp_name: str = "init_data"

    def __init__(self) -> None:
        super().__init__()

    def get_visualization_settings(self) -> dict[str, Any]:
        """Get visualization settings."""
        params: PMvpParams = self.get_mvp_params()
        return {
            "to_build_bonds": params.to_build_bonds,
            "to_show_coordinates": params.to_show_coordinates,
            "to_show_c_indexes": params.to_show_c_indexes,
            "bonds_num_of_min_distances": params.bonds_num_of_min_distances,
            "bonds_skip_first_distances": params.bonds_skip_first_distances,
        }

    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        params: PMvpParams = self.get_mvp_params()
        for key, value in settings.items():
            if hasattr(params, key):
                setattr(params, key, value)
        self.set_mvp_params(params)

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits."""
        params: PMvpParams = self.get_mvp_params()
        return {
            "x_min": params.x_min,
            "x_max": params.x_max,
            "y_min": params.y_min,
            "y_max": params.y_max,
            "z_min": params.z_min,
            "z_max": params.z_max,
        }

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits."""
        params: PMvpParams = self.get_mvp_params()
        for key, value in limits.items():
            if hasattr(params, key):
                setattr(params, key, value)
        self.set_mvp_params(params)

    def get_channel_display_settings(self) -> dict[str, Any]:
        """Get channel display settings."""
        params: PMvpParams = self.get_mvp_params()
        return {
            "to_show_dists_to_plane": params.to_show_dists_to_plane,
            "to_show_channel_angles": params.to_show_channel_angles,
            "to_show_dists_to_edges": params.to_show_dists_to_edges,
            "to_show_plane_lengths": params.to_show_plane_lengths,
        }

    def set_channel_display_settings(self, settings: dict[str, Any]) -> None:
        """Set channel display settings."""
        params: PMvpParams = self.get_mvp_params()
        for key, value in settings.items():
            if hasattr(params, key):
                setattr(params, key, value)
        self.set_mvp_params(params)

    def save_view_state(self, state: dict[str, Any]) -> None:
        """Save current view state."""
        params: PMvpParams = self.get_mvp_params()
        params.session_history.append({"type": "init_data_view", **state})
        # Keep only last 50 states
        if len(params.session_history) > 50:
            params.session_history = params.session_history[-50:]
        self.set_mvp_params(params)

    def get_view_state(self) -> dict[str, Any]:
        """Get saved view state."""
        params: PMvpParams = self.get_mvp_params()
        init_data_states = [
            item for item in params.session_history
            if item.get("type") == "init_data_view"
        ]
        return init_data_states[-1] if init_data_states else {}

    def get_channel_parameters(self, structure_info: dict[str, str]) -> Any:
        """Get channel parameters for the structure."""
        params: PMvpParams = self.get_mvp_params()
        return CarbonHoneycombModeller.get_channel_params(
            project_dir=structure_info["project_dir"],
            subproject_dir=structure_info["subproject_dir"],
            structure_dir=structure_info["structure_dir"],
            params=params,
        )

    # Additional methods for business operations
    def get_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> list[str]:
        """Get list of available files in init_data directory."""
        try:
            path: Path = PathBuilder.build_path_to_init_data_dir(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
            )
            files = FileReader.read_list_of_files(path, to_include_nested_files=True)
            return files or ["None"]
        except Exception as e:
            logger.error(f"Failed to get available files: {e}")
            return ["None"]

    def show_init_structure(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Show 3D model of initial structure."""
        params: PMvpParams = self.get_mvp_params()
        CarbonHoneycombModeller.show_init_structure(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            params=params,
        )

    def show_one_channel_structure(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Show one channel structure."""
        params: PMvpParams = self.get_mvp_params()
        CarbonHoneycombModeller.show_one_channel_structure(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            params=params,
        )

    def show_2d_channel_scheme(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Show 2D channel scheme."""
        params: PMvpParams = self.get_mvp_params()
        CarbonHoneycombModeller.show_2d_channel_scheme(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            params=params,
        )
