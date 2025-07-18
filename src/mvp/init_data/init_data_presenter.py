"""Presenter for init data functionality."""
from typing import Any
import pandas as pd

from src.interfaces import (
    PMvpParams,
    IShowInitDataPresenter,
    IShowInitDataModel,
    IShowInitDataView,
)
from src.mvp.general import GeneralPresenter
from src.services import Logger
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller

logger = Logger("InitDataPresenter")


class InitDataPresenter(GeneralPresenter, IShowInitDataPresenter):
    """Presenter for init data functionality."""

    def __init__(self, model: IShowInitDataModel, view: IShowInitDataView) -> None:
        self.model: IShowInitDataModel = model
        self.view: IShowInitDataView = view
        self.logger = Logger(self.__class__.__name__)
        self._current_context: dict[str, str] = {}
        self._setup_view_callbacks()

    def show_init_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Show initial structure visualization."""
        try:
            CarbonHoneycombModeller.show_init_structure(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                params=self.model.get_mvp_params(),
            )
            self.on_visualization_completed("init_structure")
        except Exception as e:
            self.on_visualization_failed("init_structure", e)

    def show_one_channel_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Show one channel structure visualization."""
        try:
            CarbonHoneycombModeller.show_one_channel_structure(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                params=self.model.get_mvp_params(),
            )
            self.on_visualization_completed("one_channel_structure")
        except Exception as e:
            self.on_visualization_failed("one_channel_structure", e)

    def show_2d_channel_scheme(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Show 2D channel scheme."""
        try:
            CarbonHoneycombModeller.show_2d_channel_scheme(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                params=self.model.get_mvp_params(),
            )
            self.on_visualization_completed("2d_channel_scheme")
        except Exception as e:
            self.on_visualization_failed("2d_channel_scheme", e)

    def get_channel_params(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> pd.DataFrame:
        """Get channel parameters."""
        try:
            structure_info = {
                "project_dir": project_dir,
                "subproject_dir": subproject_dir,
                "structure_dir": structure_dir,
            }
            return self.model.get_channel_parameters(structure_info)
        except Exception as e:
            self.handle_error("get channel parameters", e)
            return pd.DataFrame()

    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        try:
            self.model.set_visualization_settings(settings)
            self.handle_success("update visualization settings")
        except Exception as e:
            self.handle_error("update visualization settings", e)

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits."""
        try:
            self.model.set_coordinate_limits(limits)
            self.handle_success("update coordinate limits")
        except Exception as e:
            self.handle_error("update coordinate limits", e)

    def set_channel_display_settings(self, settings: dict[str, Any]) -> None:
        """Set channel display settings."""
        try:
            self.model.set_channel_display_settings(settings)
            self.handle_success("update channel display settings")
        except Exception as e:
            self.handle_error("update channel display settings", e)

    def on_visualization_completed(self, visualization_type: str) -> None:
        """Handle visualization completion."""
        message = f"{visualization_type.replace('_', ' ').title()} visualization completed"
        self.handle_success("show visualization", message)

        # Save view state
        state = {
            "visualization_type": visualization_type,
            "timestamp": pd.Timestamp.now().isoformat(),
        }
        self.model.save_view_state(state)

    def on_visualization_failed(self, visualization_type: str, error: Exception) -> None:
        """Handle visualization failure."""
        self.handle_error(f"show {visualization_type} visualization", error)

    def get_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> list[str]:
        """Get available files for selection."""
        try:
            return self.model.get_available_files(project_dir, subproject_dir, structure_dir)
        except Exception as e:
            self.handle_error("get available files", e)
            return ["None"]

    def get_visualization_settings(self) -> dict[str, Any]:
        """Get current visualization settings."""
        try:
            return self.model.get_visualization_settings()
        except Exception as e:
            self.handle_error("get visualization settings", e)
            return {}

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get current coordinate limits."""
        try:
            return self.model.get_coordinate_limits()
        except Exception as e:
            self.handle_error("get coordinate limits", e)
            return {}

    def get_channel_display_settings(self) -> dict[str, Any]:
        """Get current channel display settings."""
        try:
            return self.model.get_channel_display_settings()
        except Exception as e:
            self.handle_error("get channel display settings", e)
            return {}

    def load_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Load available files for the given context."""
        try:
            # Store current context
            self._current_context = {
                "project_dir": project_dir,
                "subproject_dir": subproject_dir,
                "structure_dir": structure_dir,
            }

            files = self.get_available_files(project_dir, subproject_dir, structure_dir)
            self.view.set_available_files(files)
            logger.info(f"Loaded {len(files)} files for {project_dir}/{subproject_dir}/{structure_dir}")
        except Exception as e:
            logger.error(f"Failed to load available files: {e}")
            self.view.set_available_files(["None"])

    def _setup_view_callbacks(self) -> None:
        """Set up view callbacks for button handlers."""
        callbacks = {
            "show_init_structure": self._handle_show_init_structure,
            "show_one_channel_structure": self._handle_show_one_channel_structure,
            "show_2d_channel_scheme": self._handle_show_2d_channel_scheme,
            "get_channel_params": self._handle_get_channel_params,
        }
        self.view.set_visualization_callbacks(callbacks)

    def _handle_show_init_structure(self) -> None:
        """Handle show init structure callback."""
        try:
            if not self._current_context:
                self.view.show_visualization_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params: PMvpParams = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file not in ["None", "No files found"]:
                params.file_name = selected_file
                # Update the model with the new file name
                self.model.set_mvp_params(params)

            # Get visualization settings from view
            viz_settings: dict[str, Any] = self.view.get_visualization_settings()
            coord_limits: dict[str, float] = self.view.get_coordinate_limits()

            # Update params with view settings
            if "to_build_bonds" in viz_settings:
                params.to_build_bonds = viz_settings["to_build_bonds"]
            if "to_show_coordinates" in viz_settings:
                params.to_show_coordinates = viz_settings["to_show_coordinates"]
            if "to_show_c_indexes" in viz_settings:
                params.to_show_c_indexes = viz_settings["to_show_c_indexes"]
            if "bonds_num_of_min_distances" in viz_settings:
                params.bonds_num_of_min_distances = viz_settings["bonds_num_of_min_distances"]
            if "bonds_skip_first_distances" in viz_settings:
                params.bonds_skip_first_distances = viz_settings["bonds_skip_first_distances"]

            # Update coordinate limits (directly on params, not on frozen coordinate_limits property)
            if coord_limits:
                if "x_min" in coord_limits and "x_max" in coord_limits:
                    params.x_min = coord_limits["x_min"]
                    params.x_max = coord_limits["x_max"]
                if "y_min" in coord_limits and "y_max" in coord_limits:
                    params.y_min = coord_limits["y_min"]
                    params.y_max = coord_limits["y_max"]
                if "z_min" in coord_limits and "z_max" in coord_limits:
                    params.z_min = coord_limits["z_min"]
                    params.z_max = coord_limits["z_max"]

            self.show_init_structure(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
            )

        except Exception as e:
            self.on_visualization_failed("init_structure", e)

    def _handle_show_one_channel_structure(self) -> None:
        """Handle show one channel structure callback."""
        try:
            if not self._current_context:
                self.view.show_visualization_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file not in ["None", "No files found"]:
                params.file_name = selected_file
                # Update the model with the new file name
                self.model.set_mvp_params(params)

            # Get visualization settings from view
            viz_settings = self.view.get_visualization_settings()
            coord_limits = self.view.get_coordinate_limits()

            # Update params with view settings
            if "to_build_bonds" in viz_settings:
                params.to_build_bonds = viz_settings["to_build_bonds"]
            if "to_show_coordinates" in viz_settings:
                params.to_show_coordinates = viz_settings["to_show_coordinates"]
            if "to_show_c_indexes" in viz_settings:
                params.to_show_c_indexes = viz_settings["to_show_c_indexes"]
            if "bonds_num_of_min_distances" in viz_settings:
                params.bonds_num_of_min_distances = viz_settings["bonds_num_of_min_distances"]
            if "bonds_skip_first_distances" in viz_settings:
                params.bonds_skip_first_distances = viz_settings["bonds_skip_first_distances"]

            # Update coordinate limits (directly on params, not on frozen coordinate_limits property)
            if coord_limits:
                if "x_min" in coord_limits and "x_max" in coord_limits:
                    params.x_min = coord_limits["x_min"]
                    params.x_max = coord_limits["x_max"]
                if "y_min" in coord_limits and "y_max" in coord_limits:
                    params.y_min = coord_limits["y_min"]
                    params.y_max = coord_limits["y_max"]
                if "z_min" in coord_limits and "z_max" in coord_limits:
                    params.z_min = coord_limits["z_min"]
                    params.z_max = coord_limits["z_max"]

            self.show_one_channel_structure(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
            )

        except Exception as e:
            self.on_visualization_failed("one_channel_structure", e)

    def _handle_show_2d_channel_scheme(self) -> None:
        """Handle show 2D channel scheme callback."""
        try:
            if not self._current_context:
                self.view.show_visualization_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file not in ["None", "No files found"]:
                params.file_name = selected_file
                # Update the model with the new file name
                self.model.set_mvp_params(params)

            # Get visualization settings from view
            viz_settings = self.view.get_visualization_settings()
            coord_limits = self.view.get_coordinate_limits()

            # Update params with view settings
            if "to_build_bonds" in viz_settings:
                params.to_build_bonds = viz_settings["to_build_bonds"]
            if "to_show_coordinates" in viz_settings:
                params.to_show_coordinates = viz_settings["to_show_coordinates"]
            if "to_show_c_indexes" in viz_settings:
                params.to_show_c_indexes = viz_settings["to_show_c_indexes"]
            if "bonds_num_of_min_distances" in viz_settings:
                params.bonds_num_of_min_distances = viz_settings["bonds_num_of_min_distances"]
            if "bonds_skip_first_distances" in viz_settings:
                params.bonds_skip_first_distances = viz_settings["bonds_skip_first_distances"]

            # Update coordinate limits (directly on params, not on frozen coordinate_limits property)
            if coord_limits:
                if "x_min" in coord_limits and "x_max" in coord_limits:
                    params.x_min = coord_limits["x_min"]
                    params.x_max = coord_limits["x_max"]
                if "y_min" in coord_limits and "y_max" in coord_limits:
                    params.y_min = coord_limits["y_min"]
                    params.y_max = coord_limits["y_max"]
                if "z_min" in coord_limits and "z_max" in coord_limits:
                    params.z_min = coord_limits["z_min"]
                    params.z_max = coord_limits["z_max"]

            self.show_2d_channel_scheme(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
            )

        except Exception as e:
            self.on_visualization_failed("2d_channel_scheme", e)

    def _handle_get_channel_params(self) -> None:
        """Handle get channel parameters callback."""
        try:
            if not self._current_context:
                self.view.show_visualization_error("No context available. Please reload the window.")
                return

            params_df = self.get_channel_params(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
            )

            if not params_df.empty:
                self.view.display_channel_parameters(params_df)
                self.view.show_visualization_success("Channel parameters retrieved successfully")
            else:
                self.view.show_visualization_error("Failed to get channel parameters")

        except Exception as e:
            self.on_visualization_failed("get_channel_params", e)
