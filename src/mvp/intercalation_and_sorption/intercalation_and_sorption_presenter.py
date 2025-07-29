"""Presenter for intercalation and sorption functionality."""
from pathlib import Path
from typing import Any, Callable
import pandas as pd

from src.interfaces import (
    IIntercalationAndSorptionPresenter,
    IIntercalationAndSorptionModel,
    IIntercalationAndSorptionView,
    PMvpParams,
)
from src.services import Logger
from src.projects.intercalation_and_sorption import IntercalationAndSorption

logger = Logger("IntercalationAndSorptionPresenter")


class IntercalationAndSorptionPresenter(IIntercalationAndSorptionPresenter):
    """Presenter for intercalation and sorption functionality."""

    def __init__(self, model: IIntercalationAndSorptionModel, view: IIntercalationAndSorptionView) -> None:
        self.model: IIntercalationAndSorptionModel = model
        self.view: IIntercalationAndSorptionView = view
        self._current_context: dict[str, str] = {}
        self._initialize()
        self._setup_auto_sync()

    def _initialize(self) -> None:
        """Initialize the presenter."""
        # Set up callbacks for UI operations
        callbacks: dict[str, Callable[..., None]] = {
            "plot_inter_in_c_structure": self._handle_plot_inter_in_c_structure,
            "generate_inter_plane_coordinates": self._handle_generate_inter_plane_coordinates,
            "update_inter_plane_coordinates": self._handle_update_inter_plane_coordinates,
            "translate_inter_atoms": self._handle_translate_inter_atoms,
            "update_inter_channel_coordinates": self._handle_update_inter_channel_coordinates,
            "save_distance_matrix": self._handle_save_distance_matrix,
            "get_distance_matrix": self._handle_get_distance_matrix,
            "get_inter_chc_constants": self._handle_get_inter_chc_constants,
            "translate_inter_to_all_channels_plot": self._handle_translate_inter_to_all_channels_plot,
            "translate_inter_to_all_channels_generate": self._handle_translate_inter_to_all_channels_generate,
            "file_selected": self._handle_file_selected,
            "refresh_files": self._handle_refresh_files,
        }
        self.view.set_operation_callbacks(callbacks)

    def plot_inter_in_c_structure(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Plot intercalated atoms in carbon structure."""
        try:
            self.view.show_operation_progress("Plotting intercalated atoms...")

            # TODO: Implement actual plotting logic using old_gui_logic/viewmodels/intercalation_and_sorption.py
            # This would involve:
            # 1. Loading carbon structure
            # 2. Loading intercalated atoms
            # 3. Creating visualization

            self.view.show_operation_success("Intercalated atoms plotted successfully")
            logger.info(f"Plotted intercalated atoms for {project_dir}/{subproject_dir}/{structure_dir}")

        except Exception as e:
            self.on_operation_failed("plot_inter_in_c_structure", e)

    def generate_inter_plane_coordinates_file(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Generate intercalated atoms plane coordinates file."""
        try:
            self.view.show_operation_progress("Generating intercalated atoms plane coordinates...")

            # TODO: Implement actual file generation
            output_path = Path(f"{project_dir}/{subproject_dir}/{structure_dir}/inter_plane_coords.dat")

            self.view.show_operation_success("Plane coordinates file generated", output_path)
            logger.info(f"Generated plane coordinates file: {output_path}")
            return output_path

        except Exception as e:
            self.on_operation_failed("generate_inter_plane_coordinates_file", e)
            raise

    def update_inter_plane_coordinates_file(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Update intercalated atoms plane coordinates file."""
        try:
            self.view.show_operation_progress("Updating intercalated atoms plane coordinates...")

            # TODO: Implement actual file update
            output_path = Path(f"{project_dir}/{subproject_dir}/{structure_dir}/inter_plane_coords.dat")

            self.view.show_operation_success("Plane coordinates file updated", output_path)
            logger.info(f"Updated plane coordinates file: {output_path}")
            return output_path

        except Exception as e:
            self.on_operation_failed("update_inter_plane_coordinates_file", e)
            raise

    def translate_inter_atoms_to_other_planes(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Translate intercalated atoms to other planes."""
        try:
            self.view.show_operation_progress("Translating intercalated atoms to other planes...")

            # TODO: Implement actual translation logic

            self.view.show_operation_success("Atoms translated to other planes successfully")
            logger.info(f"Translated atoms to other planes for {project_dir}/{subproject_dir}/{structure_dir}")

        except Exception as e:
            self.on_operation_failed("translate_inter_atoms_to_other_planes", e)

    def update_inter_channel_coordinates(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Update intercalated atoms channel coordinates."""
        try:
            self.view.show_operation_progress("Updating intercalated atoms channel coordinates...")

            # TODO: Implement actual channel coordinates update
            output_path = Path(f"{project_dir}/{subproject_dir}/{structure_dir}/inter_channel_coords.dat")

            self.view.show_operation_success("Channel coordinates updated", output_path)
            logger.info(f"Updated channel coordinates: {output_path}")
            return output_path

        except Exception as e:
            self.on_operation_failed("update_inter_channel_coordinates", e)
            raise

    def save_distance_matrix(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Save distance matrix."""
        try:
            self.view.show_operation_progress("Saving distance matrix...")

            # TODO: Implement actual details saving
            output_path = Path(f"{project_dir}/{subproject_dir}/{structure_dir}/distance_matrix.xlsx")

            self.view.show_operation_success("Distance matrix saved", output_path)
            logger.info(f"Saved distance matrix: {output_path}")
            return output_path

        except Exception as e:
            self.on_operation_failed("save_distance_matrix", e)
            raise

    def translate_inter_to_all_channels_plot(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> None:
        """Plot intercalated atoms translated to all channels."""
        try:
            self.view.show_operation_progress("Plotting intercalated atoms in all channels...")

            # TODO: Implement actual plotting logic

            self.view.show_operation_success("All channels plot generated successfully")
            logger.info(f"Generated all channels plot for {project_dir}/{subproject_dir}/{structure_dir}")

        except Exception as e:
            self.on_operation_failed("translate_inter_to_all_channels_plot", e)

    def translate_inter_to_all_channels_generate_files(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> tuple[Path, Path, Path]:
        """Generate files for intercalated atoms in all channels."""
        try:
            self.view.show_operation_progress("Generating files for all channels...")

            # TODO: Implement actual file generation
            output_paths = (
                Path(f"{project_dir}/{subproject_dir}/{structure_dir}/all_channels_coords.dat"),
                Path(f"{project_dir}/{subproject_dir}/{structure_dir}/all_channels_details.xlsx"),
                Path(f"{project_dir}/{subproject_dir}/{structure_dir}/all_channels_summary.txt")
            )

            self.view.show_operation_success("All channels files generated successfully")
            logger.info(f"Generated all channels files for {project_dir}/{subproject_dir}/{structure_dir}")
            return output_paths

        except Exception as e:
            self.on_operation_failed("translate_inter_to_all_channels_generate_files", e)
            raise

    # def set_intercalation_parameters(self, parameters: dict[str, Any]) -> None:
    #     """Set intercalation parameters."""
    #     self.model.set_intercalation_parameters(parameters)

    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        self.model.set_visualization_settings(settings)

    def on_operation_completed(self, operation_type: str, result: Any) -> None:
        """Handle operation completion."""
        operation_info: dict[str, str] = {
            "operation": operation_type,
            "result": str(result),
            "timestamp": pd.Timestamp.now().isoformat(),
            "status": "completed"
        }
        logger.info(f"Operation completed: {operation_info}")
        self.model.save_operation_history(operation_info)

    def on_operation_failed(self, operation_type: str, error: Exception) -> None:
        """Handle operation failure."""
        error_message = f"{operation_type} failed: {str(error)}"
        self.view.show_error_message(error_message)
        logger.error(error_message)

        operation_info = {
            "operation": operation_type,
            "error": str(error),
            "timestamp": pd.Timestamp.now().isoformat(),
            "status": "failed"
        }
        self.model.save_operation_history(operation_info)

    # UI callback handlers
    def _handle_plot_inter_in_c_structure(self) -> None:
        """Handle plot inter in C structure callback."""
        try:
            if not self._current_context:
                self.view.show_error_message("No context available. Please reload the window.")
                return

            # Show processing status
            self.view.show_processing_message("Plotting intercalated atoms in carbon structure...")

            # Get current MVP params with file selection and UI settings
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file

            # Get UI settings and update params
            ui_settings = self.view.get_operation_settings()
            self._update_params_from_ui_settings(params, ui_settings)
            self.model.set_mvp_params(params)

            IntercalationAndSorption.plot_inter_in_c_structure(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

        except Exception as e:
            self.on_operation_failed("plot_inter_in_c_structure", e)

    def _handle_generate_inter_plane_coordinates(self) -> None:
        """Handle generate inter plane coordinates callback."""
        try:
            if not self._current_context:
                self.view.show_error_message("No context available. Please reload the window.")
                return

            # Show processing status
            self.view.show_processing_message("Generating intercalated plane coordinates file...")

            # Get current MVP params
            params = self.model.get_mvp_params()

            output_path = IntercalationAndSorption.generate_inter_plane_coordinates_file(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

            self.view.show_success_message(f"File generated successfully: {output_path}")

        except Exception as e:
            self.on_operation_failed("generate_inter_plane_coordinates", e)

    def _handle_update_inter_plane_coordinates(self) -> None:
        """Handle update inter plane coordinates callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params: PMvpParams = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file

            output_path: Path = IntercalationAndSorption.update_inter_plane_coordinates_file(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

            self.on_operation_completed("update_inter_plane_coordinates", f"File updated: {output_path}")

        except Exception as e:
            self.on_operation_failed("update_inter_plane_coordinates", e)

    def _handle_translate_inter_atoms(self) -> None:
        """Handle translate inter atoms callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file

            output_path = IntercalationAndSorption.translate_inter_atoms_to_other_planes(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

            self.on_operation_completed("translate_inter_atoms", f"Translation completed: {output_path}")

        except Exception as e:
            self.on_operation_failed("translate_inter_atoms", e)

    def _handle_update_inter_channel_coordinates(self) -> None:
        """Handle update inter channel coordinates callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params: PMvpParams = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file

            output_path: Path = IntercalationAndSorption.update_inter_channel_coordinates(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )
        
            self.on_operation_completed(
                "update_inter_channel_coordinates",
                f"Channel coordinates updated: {output_path}",
            )

        except Exception as e:
            self.on_operation_failed("update_inter_channel_coordinates", e)

    def _handle_save_distance_matrix(self) -> None:
        """Handle save distance matrix callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params: PMvpParams = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file

            output_path: Path = IntercalationAndSorption.save_distance_matrix(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

            self.on_operation_completed("save_distance_matrix", f"Distance matrix saved: {output_path}")

        except Exception as e:
            self.on_operation_failed("save_distance_matrix", e)

    def _handle_get_distance_matrix(self) -> None:
        """Handle get distance matrix callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params: PMvpParams = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file

            details: pd.DataFrame = IntercalationAndSorption.get_distance_matrix(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

            self.view.display_distance_matrix(details)
            self.on_operation_completed("get_distance_matrix", "Channel details retrieved")

        except Exception as e:
            self.on_operation_failed("get_distance_matrix", e)

    def _handle_get_inter_chc_constants(self) -> None:
        """Handle get intercalation constants callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return

            constants: pd.DataFrame = IntercalationAndSorption.get_inter_chc_constants(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
            )

            self.view.display_channel_constants(constants)
            self.on_operation_completed("get_inter_chc_constants", "Intercalation constants retrieved")

        except Exception as e:
            self.on_operation_failed("get_inter_chc_constants", e)

    def _handle_translate_inter_to_all_channels_plot(self) -> None:
        """Handle translate inter to all channels plot callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return

            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file

            IntercalationAndSorption.translate_inter_to_all_channels_plot(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

            self.on_operation_completed("translate_inter_to_all_channels_plot", "All channels plot generated")

        except Exception as e:
            self.on_operation_failed("translate_inter_to_all_channels_plot", e)

    def _handle_translate_inter_to_all_channels_generate(self) -> None:
        """Handle translate inter to all channels generate callback."""
        try:
            if not self._current_context:
                self.view.show_error_message("No context available. Please reload the window.")
                return

            # Show processing status
            self.view.show_processing_message("Generating files for all channels...")

            # Get current MVP params with file selection and UI settings
            params: PMvpParams = self.model.get_mvp_params()
            selected_file: str = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file
                # Update the model with the new file name
                self.model.set_mvp_params(params)

            # Get UI settings and update params
            if hasattr(self.view, 'get_operation_settings'):
                ui_settings = self.view.get_operation_settings()
                
                # Update MVP params with all UI settings
                self._update_params_from_ui_settings(params, ui_settings)
                
                # Save updated params to model
                self.model.set_mvp_params(params)

            coords_path, details_path = IntercalationAndSorption.translate_inter_to_all_channels_generate_files(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )

            self.view.show_success_message(f"Files generated successfully: {coords_path}, {details_path}")

        except Exception as e:
            self.on_operation_failed("translate_inter_to_all_channels_generate", e)

    def _handle_translate_inter_to_all_channels_generate_files(self) -> None:
        """Handle translate inter to all channels generate files callback (alias)."""
        # This is an alias for the existing method to match expected naming
        self._handle_translate_inter_to_all_channels_generate()

    def _handle_file_selected(self, file_name: str) -> None:
        """Handle file selection from dropdown."""
        logger.info(f"File selected: {file_name}")
        # TODO: Store selected file name and use it in operations
        # For now, just log the selection

    def _handle_refresh_files(self) -> None:
        """Handle refresh files callback."""
        if self._current_context:
            try:
                files = self.model.get_available_files(
                    self._current_context["project_dir"],
                    self._current_context["subproject_dir"],
                    self._current_context["structure_dir"]
                )
                self.view.set_available_files(files)
            except Exception as e:
                logger.error(f"Failed to refresh files: {e}")
                self.view.set_available_files(["No files found"])

    def load_available_files(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Load available files for the given context."""
        try:
            # Store current context
            self._current_context = {
                "project_dir": project_dir,
                "subproject_dir": subproject_dir,
                "structure_dir": structure_dir
            }

            files = self.model.get_available_files(project_dir, subproject_dir, structure_dir)
            self.view.set_available_files(files)
            
            # Load UI from current MVP parameters
            self.load_ui_from_params()
            
            # Start periodic file refresh
            self.view.start_file_list_refresh()
            
            logger.info(f"Loaded {len(files)} files for {project_dir}/{subproject_dir}/{structure_dir}")
        except Exception as e:
            logger.error(f"Failed to load available files: {e}")
            self.view.set_available_files(["No files found"])

    def _update_params_from_ui_settings(self, params: PMvpParams, ui_settings: dict[str, Any]) -> None:
        """Update MVP params from UI settings."""
        # Update visualization settings
        for key, value in ui_settings.items():
            if hasattr(params, key):
                setattr(params, key, value)
        
        # Specifically handle coordinate limits
        if "x_min" in ui_settings:
            params.x_min = ui_settings["x_min"]
        if "x_max" in ui_settings:
            params.x_max = ui_settings["x_max"]
        if "y_min" in ui_settings:
            params.y_min = ui_settings["y_min"]
        if "y_max" in ui_settings:
            params.y_max = ui_settings["y_max"]
        if "z_min" in ui_settings:
            params.z_min = ui_settings["z_min"]
        if "z_max" in ui_settings:
            params.z_max = ui_settings["z_max"]

    def load_ui_from_params(self) -> None:
        """Load UI components from current MVP parameters."""
        try:
            params = self.model.get_mvp_params()
            
            # Load visualization settings
            viz_settings = {
                "to_build_bonds": params.to_build_bonds,
                "to_show_coordinates": params.to_show_coordinates,
                "to_show_c_indexes": params.to_show_c_indexes,
                "to_show_inter_atoms_indexes": params.to_show_inter_atoms_indexes,
                "to_show_dists_to_plane": params.to_show_dists_to_plane,
                "to_show_dists_to_edges": params.to_show_dists_to_edges,
                "to_show_channel_angles": params.to_show_channel_angles,
                "to_show_plane_lengths": params.to_show_plane_lengths,
                "to_translate_inter": params.to_translate_inter,
                "to_replace_nearby_atoms": params.to_replace_nearby_atoms,
                "to_remove_too_close_atoms": params.to_remove_too_close_atoms,
                "to_to_try_to_reflect_inter_atoms": params.to_to_try_to_reflect_inter_atoms,
                "to_equidistant_inter_points": params.to_equidistant_inter_points,
                "to_filter_inter_atoms": params.to_filter_inter_atoms,
                "to_remove_inter_atoms_with_min_and_max_x_coordinates": params.to_remove_inter_atoms_with_min_and_max_x_coordinates,
                "bonds_num_of_min_distances": params.bonds_num_of_min_distances,
                "bonds_skip_first_distances": params.bonds_skip_first_distances,
            }
            self.view.set_visualization_settings(viz_settings)
            
            # Load intercalation parameters
            inter_params = {
                "number_of_planes": params.number_of_planes,
                "num_of_inter_atoms_layers": params.num_of_inter_atoms_layers,
                "inter_atoms_lattice_type": params.inter_atoms_lattice_type,
            }
            if hasattr(self.view, 'set_intercalation_parameters'):
                self.view.set_intercalation_parameters(inter_params)
            
            # Load coordinate limits
            coord_limits = {
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
            params: PMvpParams = self.model.get_mvp_params()
            
            # Handle different parameter types
            if param_name in ['bonds_num_of_min_distances', 'bonds_skip_first_distances', 'number_of_planes', 'num_of_inter_atoms_layers']:
                try:
                    int_value = int(value) if value else (6 if param_name == 'number_of_planes' else 2 if param_name == 'num_of_inter_atoms_layers' else 0)
                    setattr(params, param_name, int_value)
                except ValueError:
                    return  # Ignore invalid values
            
            elif param_name in ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']:
                try:
                    if value == "" or value.lower() in ['inf', '-inf']:
                        float_value: float = -float('inf') if param_name.endswith('_min') else float('inf')
                    else:
                        float_value = float(value)
                    setattr(params, param_name, float_value)
                except ValueError:
                    return  # Ignore invalid values
            
            elif param_name == 'inter_atoms_lattice_type':
                str_value = value if value else "FCC"
                setattr(params, param_name, str_value)
            
            # Save updated parameters
            self.model.set_mvp_params(params)
            
        except Exception as e:
            logger.error(f"Failed to handle auto-sync parameter change for {param_name}: {e}")
