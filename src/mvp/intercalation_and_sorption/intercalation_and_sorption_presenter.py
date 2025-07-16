"""Presenter for intercalation and sorption functionality."""
from pathlib import Path
from typing import Any, Callable
import pandas as pd

from src.interfaces import (
    IIntercalationAndSorptionPresenter,
    IIntercalationAndSorptionModel,
    IIntercalationAndSorptionView,
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

    def _initialize(self) -> None:
        """Initialize the presenter."""
        # Set up callbacks for UI operations
        callbacks: dict[str, Callable[[], None]] = {
            "plot_inter_in_c_structure": self._handle_plot_inter_in_c_structure,
            "generate_inter_plane_coordinates": self._handle_generate_inter_plane_coordinates,
            "update_inter_plane_coordinates": self._handle_update_inter_plane_coordinates,
            "translate_inter_atoms": self._handle_translate_inter_atoms,
            "update_inter_channel_coordinates": self._handle_update_inter_channel_coordinates,
            "save_inter_in_channel_details": self._handle_save_inter_in_channel_details,
            "get_inter_in_channel_details": self._handle_get_inter_in_channel_details,
            "translate_inter_to_all_channels_plot": self._handle_translate_inter_to_all_channels_plot,
            "translate_inter_to_all_channels_generate": self._handle_translate_inter_to_all_channels_generate,
            "file_selected": self._handle_file_selected,
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

    def save_inter_in_channel_details(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> Path:
        """Save intercalated atoms in channel details."""
        try:
            self.view.show_operation_progress("Saving intercalated atoms channel details...")

            # TODO: Implement actual details saving
            output_path = Path(f"{project_dir}/{subproject_dir}/{structure_dir}/inter_channel_details.xlsx")

            self.view.show_operation_success("Channel details saved", output_path)
            logger.info(f"Saved channel details: {output_path}")
            return output_path

        except Exception as e:
            self.on_operation_failed("save_inter_in_channel_details", e)
            raise

    def get_inter_in_channel_details(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> pd.DataFrame:
        """Get intercalated atoms in channel details."""
        try:
            self.view.show_operation_progress("Loading intercalated atoms channel details...")

            # TODO: Implement actual details loading
            details = pd.DataFrame({
                "Channel": [1, 2, 3],
                "Atom_Count": [5, 8, 3],
                "Average_Distance": [2.1, 2.3, 2.0]
            })

            self.view.display_channel_details(details)
            logger.info(f"Loaded channel details for {project_dir}/{subproject_dir}/{structure_dir}")
            return details

        except Exception as e:
            self.on_operation_failed("get_inter_in_channel_details", e)
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

    def set_intercalation_parameters(self, parameters: dict[str, Any]) -> None:
        """Set intercalation parameters."""
        self.model.set_intercalation_parameters(parameters)

    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings."""
        self.model.set_visualization_settings(settings)

    def on_operation_completed(self, operation_type: str, result: Any) -> None:
        """Handle operation completion."""
        operation_info = {
            "operation": operation_type,
            "result": str(result),
            "timestamp": pd.Timestamp.now().isoformat(),
            "status": "completed"
        }
        self.model.save_operation_history(operation_info)

    def on_operation_failed(self, operation_type: str, error: Exception) -> None:
        """Handle operation failure."""
        error_message = f"{operation_type} failed: {str(error)}"
        self.view.show_operation_error(error_message)
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
                self.view.show_operation_error("No context available. Please reload the window.")
                return
            
            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file
            
            IntercalationAndSorption.plot_inter_in_c_structure(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )
            
            self.on_operation_completed("plot_inter_in_c_structure", "Plot generated successfully")
            
        except Exception as e:
            self.on_operation_failed("plot_inter_in_c_structure", e)

    def _handle_generate_inter_plane_coordinates(self) -> None:
        """Handle generate inter plane coordinates callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return
            
            # Get current MVP params
            params = self.model.get_mvp_params()
            
            output_path = IntercalationAndSorption.generate_inter_plane_coordinates_file(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )
            
            self.on_operation_completed("generate_inter_plane_coordinates", f"File generated: {output_path}")
            
        except Exception as e:
            self.on_operation_failed("generate_inter_plane_coordinates", e)

    def _handle_update_inter_plane_coordinates(self) -> None:
        """Handle update inter plane coordinates callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return
            
            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file
            
            output_path = IntercalationAndSorption.update_inter_plane_coordinates_file(
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
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file
            
            output_path = IntercalationAndSorption.update_inter_channel_coordinates(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )
            
            self.on_operation_completed("update_inter_channel_coordinates", f"Channel coordinates updated: {output_path}")
            
        except Exception as e:
            self.on_operation_failed("update_inter_channel_coordinates", e)

    def _handle_save_inter_in_channel_details(self) -> None:
        """Handle save inter in channel details callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return
            
            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file
            
            output_path = IntercalationAndSorption.save_inter_in_channel_details(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )
            
            self.on_operation_completed("save_inter_in_channel_details", f"Channel details saved: {output_path}")
            
        except Exception as e:
            self.on_operation_failed("save_inter_in_channel_details", e)

    def _handle_get_inter_in_channel_details(self) -> None:
        """Handle get inter in channel details callback."""
        try:
            if not self._current_context:
                self.view.show_operation_error("No context available. Please reload the window.")
                return
            
            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file
            
            details = IntercalationAndSorption.get_inter_in_channel_details(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )
            
            self.view.display_channel_details(details)
            self.on_operation_completed("get_inter_in_channel_details", "Channel details retrieved")
            
        except Exception as e:
            self.on_operation_failed("get_inter_in_channel_details", e)

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
                self.view.show_operation_error("No context available. Please reload the window.")
                return
            
            # Get current MVP params with file selection
            params = self.model.get_mvp_params()
            selected_file = self.view.get_selected_file()
            if selected_file and selected_file != "No files found":
                params.file_name = selected_file
            
            coords_path, details_path = IntercalationAndSorption.translate_inter_to_all_channels_generate_files(
                project_dir=self._current_context["project_dir"],
                subproject_dir=self._current_context["subproject_dir"],
                structure_dir=self._current_context["structure_dir"],
                params=params,
            )
            
            self.on_operation_completed("translate_inter_to_all_channels_generate", f"Files generated: {coords_path}, {details_path}")
            
        except Exception as e:
            self.on_operation_failed("translate_inter_to_all_channels_generate", e)

    def _handle_file_selected(self, file_name: str) -> None:
        """Handle file selection from dropdown."""
        logger.info(f"File selected: {file_name}")
        # TODO: Store selected file name and use it in operations
        # For now, just log the selection

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
            logger.info(f"Loaded {len(files)} files for {project_dir}/{subproject_dir}/{structure_dir}")
        except Exception as e:
            logger.error(f"Failed to load available files: {e}")
            self.view.set_available_files(["No files found"])
