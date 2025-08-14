"""Presenter for init data functionality."""
from typing import Any, Callable
import pandas as pd
import numpy as np
from numpy.typing import NDArray

from src.interfaces import (
    PMvpParams,
    IShowInitDataPresenter,
    IShowInitDataModel,
    IShowInitDataView,
    ICarbonHoneycombChannel,
    IPoints,
)
from src.entities import Points
from src.mvp.general import GeneralPresenter
from src.services import Logger, FileReader, VisualizationParams
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller, CarbonHoneycombActions
from src.ui.components import PlotWindow, PlotWindowFactory

logger = Logger("InitDataPresenter")


class InitDataPresenter(GeneralPresenter, IShowInitDataPresenter):
    """Presenter for init data functionality."""

    def __init__(self, model: IShowInitDataModel, view: IShowInitDataView) -> None:
        self.model: IShowInitDataModel = model
        self.view: IShowInitDataView = view
        self.logger = Logger(self.__class__.__name__)
        self._current_context: dict[str, str] = {}
        self._setup_view_callbacks()
        self._setup_auto_sync()

    def show_init_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams | None = None,
    ) -> None:
        """Show initial structure visualization."""
        try:
            if params is None:
                params = self.model.get_mvp_params()

            file_name: str | None = params.file_name
            if file_name is None:
                raise ValueError("File name is required")

            # Get carbon structure coordinates
            carbon_coords: NDArray[np.float64] = FileReader.read_init_data_file(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                file_name=file_name,
            )

            # Create and show plot window
            plot_window: PlotWindow = PlotWindowFactory.show_structure_in_new_window(
                master=self.view,
                coordinates=carbon_coords,
                structure_visual_params=VisualizationParams.carbon,
                mvp_params=params,
                title=f"Initial Structure - {structure_dir}",
                label="Carbon",
            )

            logger.info(f"Opened plot window for initial structure: {structure_dir}")
            self.on_visualization_completed("init_structure")

        except Exception as e:
            logger.error(f"Failed to open plot window for initial structure: {e}")
            self.on_visualization_failed("plot_window", e)

    def show_one_channel_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams | None = None,
    ) -> None:
        """Show one channel structure visualization."""
        try:
            if params is None:
                params = self.model.get_mvp_params()

            file_name: str | None = params.file_name
            if file_name is None:
                raise ValueError("File name is required")

            # Get channel structure coordinates
            carbon_points: NDArray[np.float64] = FileReader.read_init_data_file(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                file_name=file_name,
            )

            carbon_channels: list[ICarbonHoneycombChannel] = CarbonHoneycombActions.split_init_structure_into_separate_channels(
                coordinates_carbon=Points(points=carbon_points))

            carbon_channel: ICarbonHoneycombChannel = carbon_channels[0]

            # Create and show plot window
            plot_window: PlotWindow = PlotWindowFactory.show_structure_in_new_window(
                master=self.view,
                coordinates=carbon_channel.points,
                structure_visual_params=VisualizationParams.carbon,
                mvp_params=params,
                title=f"Channel Structure - {structure_dir}",
                label="Carbon Channel",
            )

            logger.info(f"Opened plot window for channel structure: {structure_dir}")
            self.on_visualization_completed("one_channel_structure")

        except Exception as e:
            logger.error(f"Failed to open plot window for channel structure: {e}")
            self.on_visualization_failed("plot_window", e)

    def show_2d_channel_scheme(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams | None = None,
    ) -> None:
        """Show 2D channel scheme."""
        try:
            if params is None:
                params = self.model.get_mvp_params()

            CarbonHoneycombModeller.show_2d_channel_scheme(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                params=params,
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
        # message = f"{visualization_type.replace('_', ' ').title()} visualization completed"
        # self.view.show_success_message(message)

        # Save view state
        state = {
            "visualization_type": visualization_type,
            "timestamp": pd.Timestamp.now().isoformat(),
        }
        self.model.save_view_state(state)

    def on_visualization_failed(self, visualization_type: str, error: Exception) -> None:
        """Handle visualization failure."""
        error_message = f"Failed to show {visualization_type} visualization: {str(error)}"
        self.view.show_error_message(error_message)

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

            # Load UI from current MVP parameters
            self._load_ui_from_params()

            logger.info(f"Loaded {len(files)} files for {project_dir}/{subproject_dir}/{structure_dir}")
        except Exception as e:
            logger.error(f"Failed to load available files: {e}")
            self.view.set_available_files(["None"])

    def _setup_view_callbacks(self) -> None:
        """Set up view callbacks for button handlers."""
        callbacks: dict[str, Callable] = {
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
                self.view.show_error_message("No context available. Please reload the window.")
                return

            # Show processing status
            self.view.show_processing_message("Generating initial structure visualization...")

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
                params=params,
            )

        except Exception as e:
            self.on_visualization_failed("init_structure", e)

    def _handle_show_one_channel_structure(self) -> None:
        """Handle show one channel structure callback."""
        try:
            if not self._current_context:
                self.view.show_error_message("No context available. Please reload the window.")
                return

            # Show processing status
            self.view.show_processing_message("Generating one channel structure visualization...")

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
                params=params,
            )

        except Exception as e:
            self.on_visualization_failed("one_channel_structure", e)

    def _handle_show_2d_channel_scheme(self) -> None:
        """Handle show 2D channel scheme callback."""
        try:
            if not self._current_context:
                self.view.show_error_message("No context available. Please reload the window.")
                return

            # Show processing status
            self.view.show_processing_message("Generating 2D channel scheme visualization...")

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
                params=params,
            )

        except Exception as e:
            self.on_visualization_failed("2d_channel_scheme", e)

    def _handle_get_channel_params(self) -> None:
        """Handle get channel parameters callback."""
        try:
            if not self._current_context:
                self.view.show_error_message("No context available. Please reload the window.")
                return

            # Show processing status
            self.view.show_processing_message("Retrieving channel parameters...")

            params_df = self.get_channel_params(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
            )

            if not params_df.empty:
                self.view.display_channel_parameters(params_df)
                self.view.show_success_message("Channel parameters retrieved successfully")
            else:
                self.view.show_error_message("Failed to get channel parameters")

        except Exception as e:
            self.on_visualization_failed("get_channel_params", e)

    def _load_ui_from_params(self) -> None:
        """Load UI components from current MVP parameters."""
        try:
            params = self.model.get_mvp_params()

            # Load visualization settings
            viz_settings = {
                "to_build_bonds": params.to_build_bonds,
                "to_show_coordinates": params.to_show_coordinates,
                "to_show_c_indexes": params.to_show_c_indexes,
                "bonds_num_of_min_distances": params.bonds_num_of_min_distances,
                "bonds_skip_first_distances": params.bonds_skip_first_distances,
            }
            self.view.set_visualization_settings(viz_settings)

            # Load coordinate limits
            coord_limits: dict[str, float] = {
                "x_min": params.x_min,
                "x_max": params.x_max,
                "y_min": params.y_min,
                "y_max": params.y_max,
                "z_min": params.z_min,
                "z_max": params.z_max,
            }
            self.view.set_coordinate_limits(coord_limits)

        except Exception as e:
            logger.error(f"Failed to load UI from params: {e}")

    def _setup_auto_sync(self) -> None:
        """Setup auto-sync callback for input field changes."""
        self.view.set_auto_sync_callback(self._handle_auto_sync_parameter_change)

    def _handle_auto_sync_parameter_change(self, param_name: str, value: str) -> None:
        """Handle auto-sync parameter changes from UI."""
        try:
            params = self.model.get_mvp_params()

            # Handle different parameter types
            if param_name in ['bonds_num_of_min_distances', 'bonds_skip_first_distances']:
                try:
                    int_value = int(value) if value else 0
                    setattr(params, param_name, int_value)
                except ValueError:
                    return  # Ignore invalid values

            elif param_name in ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']:
                try:
                    if value == "" or value.lower() in ['inf', '-inf']:
                        float_value = -float('inf') if param_name.endswith('_min') else float('inf')
                    else:
                        float_value = float(value)
                    setattr(params, param_name, float_value)
                except ValueError:
                    return  # Ignore invalid values

            # Save updated parameters
            self.model.set_mvp_params(params)

        except Exception as e:
            logger.error(f"Failed to handle auto-sync parameter change for {param_name}: {e}")
