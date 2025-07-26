"""View for intercalation and sorption functionality."""

import customtkinter as ctk
from typing import Any, Callable, Literal
from pathlib import Path
import pandas as pd

from src.interfaces import IIntercalationAndSorptionView
from src.mvp.general import GeneralView
from src.ui.components import Button, CheckBox, InputField, DropdownList, Table
from src.ui.templates import ScrollableToplevel, CoordinateLimitsTemplate, WindowGeneralTemplate
from src.services import Logger

logger = Logger("IntercalationAndSorptionView")


class IntercalationAndSorptionView(GeneralView, IIntercalationAndSorptionView):
    """View for intercalation and sorption functionality."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Intercalation and Sorption")
        self.geometry("800x900")

        # Context variables
        self.project_dir: str = ""
        self.subproject_dir: str = ""
        self.structure_dir: str = ""

        # UI template
        self.template = WindowGeneralTemplate()

        # UI components
        self.visualization_checkboxes: dict[str, CheckBox] = {}
        self.operation_buttons: dict[str, Button] = {}
        self.intercalation_params: dict[str, InputField] = {}
        self.file_selection_dropdown: DropdownList | None = None
        self.bonds_num_input: InputField | None = None
        self.bonds_skip_input: InputField | None = None
        self.coordinate_limits_template: CoordinateLimitsTemplate | None = None

        # Callbacks
        self.callbacks: dict[str, Callable] = {}

        # File refresh management
        self._refresh_job_id: str | None = None
        self._last_files_list: list[str] = []

    def set_context(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Set the context for this view."""
        self.project_dir = project_dir
        self.subproject_dir = subproject_dir
        self.structure_dir = structure_dir
        self.title(f"Intercalation & Sorption - {project_dir}/{subproject_dir}/{structure_dir}")

    def set_ui(self) -> None:
        """Set up the UI components."""
        # Create main layout using template
        main_frame: ctk.CTkScrollableFrame = self.template.create_main_layout(self)

        # # Intercalation parameters
        # params_frame = ctk.CTkFrame(main_frame)
        # params_frame.pack(fill="x", pady=(0, 10))

        # ctk.CTkLabel(params_frame, text="Intercalation Parameters",
        #              font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # self.intercalation_params["atom_type"] = InputField(params_frame, "Atom Type")
        # self.intercalation_params["atom_type"].pack(pady=2)

        # self.intercalation_params["concentration"] = InputField(params_frame, "Concentration")
        # self.intercalation_params["concentration"].pack(pady=2)

        # self.intercalation_params["temperature"] = InputField(params_frame, "Temperature (K)")
        # self.intercalation_params["temperature"].pack(pady=2)

        # Operation buttons section
        operations_frame: ctk.CTkFrame = self.template.create_section_frame(main_frame, "Operations")

        # Create three columns for operation buttons
        op_col1, op_col2, op_col3 = self.template.create_columns_layout(operations_frame, 3)

        ##### FIRST COLUMN #####
        self.operation_buttons["generate_inter_plane_coordinates"] = self.template.pack_button(
            op_col1, "Generate Plane Coordinates",
            self._on_generate_inter_plane_coordinates
        )
        self.operation_buttons["update_inter_plane_coordinates"] = self.template.pack_button(
            op_col1, "Update Plane Coordinates",
            self._on_update_inter_plane_coordinates
        )
        self.operation_buttons["get_inter_chc_constants"] = self.template.pack_button(
            op_col1, "Get intercalation constants",
            self._on_get_inter_chc_constants
        )

        ##### SECOND COLUMN #####
        self.operation_buttons["plot_inter_in_c_structure"] = self.template.pack_button(
            op_col2, "Plot Intercalated Atoms in C Structure",
            self._on_plot_inter_in_c_structure
        )
        self.operation_buttons["get_inter_in_channel_details"] = self.template.pack_button(
            op_col2, "Get Channel Details",
            self._on_get_inter_in_channel_details
        )
        self.operation_buttons["save_inter_in_channel_details"] = self.template.pack_button(
            op_col2, "Save Channel Details",
            self._on_save_inter_in_channel_details
        )
        self.operation_buttons["translate_inter_atoms"] = self.template.pack_button(
            op_col2, "Translate Atoms to Other Planes",
            self._on_translate_inter_atoms
        )

        ##### THIRD COLUMN #####
        self.operation_buttons["update_inter_channel_coordinates"] = self.template.pack_button(
            op_col3, "Update Channel Coordinates",
            self._on_update_inter_channel_coordinates
        )
        self.operation_buttons["translate_inter_to_all_channels_generate"] = self.template.pack_button(
            op_col3, "Generate All Channels Files",
            self._on_translate_inter_to_all_channels_generate
        )
        self.operation_buttons["translate_inter_to_all_channels_plot"] = self.template.pack_button(
            op_col3, "Plot All Channels",
            self._on_translate_inter_to_all_channels_plot
        )

        # File selection section
        file_frame: ctk.CTkFrame = self.template.create_section_frame(main_frame, "File Selection")
        self.template.pack_label(file_frame, "Select intercalated structure file:", pady=2)
        self.file_selection_dropdown = DropdownList(file_frame, ["Loading..."], command=self._on_file_selected)
        self.file_selection_dropdown.pack(pady=2)

        # Visualization settings section with columns
        viz_frame: ctk.CTkFrame = self.template.create_section_frame(main_frame, "Visualization Settings")

        # Create two columns using template
        left_column, right_column = self.template.create_columns_layout(viz_frame, 2)

        # Left column - Structure display
        self.template.pack_label(left_column, "Structure Display", pady=2,
                                 font=ctk.CTkFont(size=12, weight="bold"))

        self.visualization_checkboxes["to_build_bonds"] = self.template.pack_check_box(
            left_column, "Build bonds"
        )
        self.visualization_checkboxes["to_show_coordinates"] = self.template.pack_check_box(
            left_column, "Show coordinates"
        )
        self.visualization_checkboxes["to_show_c_indexes"] = self.template.pack_check_box(
            left_column, "Show carbon atom indexes"
        )
        self.visualization_checkboxes["to_show_inter_atoms_indexes"] = self.template.pack_check_box(
            left_column, "Show intercalated atom indexes"
        )

        # Right column - Channel analysis
        self.template.pack_label(right_column, "Channel Analysis", pady=2,
                                 font=ctk.CTkFont(size=12, weight="bold"))

        self.visualization_checkboxes["to_show_dists_to_plane"] = self.template.pack_check_box(
            right_column, "Show distances to plane"
        )
        self.visualization_checkboxes["to_show_dists_to_edges"] = self.template.pack_check_box(
            right_column, "Show distances to edges"
        )
        self.visualization_checkboxes["to_show_channel_angles"] = self.template.pack_check_box(
            right_column, "Show channel angles"
        )
        self.visualization_checkboxes["to_show_plane_lengths"] = self.template.pack_check_box(
            right_column, "Show plane lengths"
        )

        # Bonds parameters section
        bonds_frame = ctk.CTkFrame(viz_frame)
        bonds_frame.pack(fill="x", padx=10, pady=5)

        self.template.pack_label(bonds_frame, "Bond Parameters", pady=2,
                                 font=ctk.CTkFont(size=12, weight="bold"))

        # Create horizontal layout for bond inputs
        bonds_left, bonds_right = self.template.create_columns_layout(bonds_frame, 2)

        self.bonds_num_input = self.template.pack_input_field(
            bonds_left, "Number of min distances",
            change_callback=self._on_bonds_num_changed
        )
        self.bonds_skip_input = self.template.pack_input_field(
            bonds_right, "Skip first distances",
            change_callback=self._on_bonds_skip_changed
        )

        # Coordinate limits using template
        self.coordinate_limits_template = self.template.create_coordinate_limits_section(
            main_frame,
            change_callback=self._on_coordinate_limits_changed
        )

        # Intercalation parameters section
        inter_frame: ctk.CTkFrame = self.template.create_section_frame(main_frame, "Intercalation Parameters")

        # Create columns for intercalation parameters
        inter_left, inter_right = self.template.create_columns_layout(inter_frame, 2)

        # Left column - Basic parameters
        self.intercalation_params["number_of_planes"] = self.template.pack_input_field(
            inter_left, "Number of planes",
            change_callback=self._on_number_of_planes_changed
        )
        self.intercalation_params["num_of_inter_atoms_layers"] = self.template.pack_input_field(
            inter_left, "Number of inter atom layers",
            change_callback=self._on_num_inter_atoms_layers_changed
        )
        self.intercalation_params["inter_atoms_lattice_type"] = self.template.pack_input_field(
            inter_left, "Inter atoms lattice type",
            change_callback=self._on_lattice_type_changed
        )

        # Right column - Boolean flags
        self.visualization_checkboxes["to_translate_inter"] = self.template.pack_check_box(
            inter_right, "Translate intercalated atoms"
        )
        self.visualization_checkboxes["to_replace_nearby_atoms"] = self.template.pack_check_box(
            inter_right, "Replace nearby atoms"
        )
        self.visualization_checkboxes["to_remove_too_close_atoms"] = self.template.pack_check_box(
            inter_right, "Remove too close atoms"
        )
        self.visualization_checkboxes["to_to_try_to_reflect_inter_atoms"] = self.template.pack_check_box(
            inter_right, "Try to reflect inter atoms"
        )
        self.visualization_checkboxes["to_equidistant_inter_points"] = self.template.pack_check_box(
            inter_right, "Equidistant inter points"
        )
        self.visualization_checkboxes["to_filter_inter_atoms"] = self.template.pack_check_box(
            inter_right, "Filter inter atoms"
        )
        self.visualization_checkboxes["to_remove_inter_atoms_with_min_and_max_x_coordinates"] = self.template.pack_check_box(
            inter_right, "Remove atoms at X boundaries")

        # Call parent set_ui to refresh scrolling
        super().set_ui()

    # def set_intercalation_parameters(self, parameters: dict[str, Any]) -> None:
    #     """Set intercalation parameters in the UI."""
    #     for key, value in parameters.items():
    #         if key in self.intercalation_params:
    #             self.intercalation_params[key].set_value(str(value))

    # def get_intercalation_parameters(self) -> dict[str, Any]:
    #     """Get intercalation parameters from the UI."""
    #     parameters = {}
    #     for key, field in self.intercalation_params.items():
    #         parameters[key] = field.get_value()
    #     return parameters

    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings in the UI."""
        for key, value in settings.items():
            if key in self.visualization_checkboxes:
                self.visualization_checkboxes[key].set_value(bool(value))

        # Handle bond parameters
        if "bonds_num_of_min_distances" in settings and self.bonds_num_input:
            self.bonds_num_input.set_value(str(settings["bonds_num_of_min_distances"]))

        if "bonds_skip_first_distances" in settings and self.bonds_skip_input:
            self.bonds_skip_input.set_value(str(settings["bonds_skip_first_distances"]))

    def get_visualization_settings(self) -> dict[str, Any]:
        """Get visualization settings from the UI."""
        settings = {}
        for key, checkbox in self.visualization_checkboxes.items():
            settings[key] = checkbox.get()

        # Add bond parameters
        if self.bonds_num_input:
            try:
                settings["bonds_num_of_min_distances"] = int(self.bonds_num_input.get_value())
            except ValueError:
                settings["bonds_num_of_min_distances"] = 2

        if self.bonds_skip_input:
            try:
                settings["bonds_skip_first_distances"] = int(self.bonds_skip_input.get_value())
            except ValueError:
                settings["bonds_skip_first_distances"] = 0

        return settings

    def set_intercalation_parameters(self, params: dict[str, Any]) -> None:
        """Set intercalation parameters in the UI."""
        for key, value in params.items():
            if key in self.intercalation_params:
                self.intercalation_params[key].set_value(str(value))

    def get_intercalation_parameters(self) -> dict[str, Any]:
        """Get intercalation parameters from the UI."""
        params = {}
        for key, field in self.intercalation_params.items():
            value = field.get_value()
            if key in ["number_of_planes", "num_of_inter_atoms_layers"]:
                try:
                    params[key] = int(value) if value else 6 if key == "number_of_planes" else 2
                except ValueError:
                    params[key] = 6 if key == "number_of_planes" else 2
            else:
                params[key] = value if value else ("FCC" if key == "inter_atoms_lattice_type" else "")

        return params

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits in the UI."""
        if self.coordinate_limits_template:
            self.coordinate_limits_template.set_coordinate_limits(limits)

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits from the UI."""
        if self.coordinate_limits_template:
            return self.coordinate_limits_template.get_coordinate_limits()
        return {}

    def show_operation_progress(self, message: str) -> None:
        """Show operation progress to user."""
        self.show_status_message(f"Processing: {message}")

    def show_operation_success(self, message: str, result_path: Path | None = None) -> None:
        """Show successful operation result."""
        if result_path:
            self.show_success_message(f"{message}\nOutput: {result_path}")
        else:
            self.show_success_message(message)

    def show_operation_error(self, error_message: str) -> None:
        """Show operation error to user."""
        self.show_error_message(error_message)

    def display_channel_details(self, details: pd.DataFrame) -> None:
        """Display channel details in the UI."""
        # Create a new window with touchpad scrolling support
        details_window = ScrollableToplevel(self)
        details_window.title("Channel Details")

        width: int = min(len(details.columns) * 60 + 120, 1000)
        height: int = min(len(details) * 25 + 110, 1000)
        details_window.geometry(f"{width}x{height}")

        # Create and display the table
        table = Table(
            data=details,
            master=details_window,
            title="Channel Details",
            to_show_index=True
        )
        table.pack(fill="both", expand=True, padx=10, pady=10)

    def display_channel_constants(self, constants: pd.DataFrame) -> None:
        """Display channel constants in the UI."""
        # Create a new window with touchpad scrolling support
        constants_window = ScrollableToplevel(self)
        constants_window.title("Channel Constants")
        constants_window.geometry("500x250")

        # Create and display the table
        table = Table(
            data=constants,
            master=constants_window,
            title="Channel Constants",
            to_show_index=True
        )
        table.pack(fill="both", expand=True, padx=10, pady=10)

    def set_operation_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for operation buttons."""
        self.callbacks = callbacks

    def enable_controls(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        state: Literal["normal", "disabled"] = "normal" if enabled else "disabled"

        for button in self.operation_buttons.values():
            button.configure(state=state)

    def reset_form(self) -> None:
        """Reset the form to default values."""
        # Reset intercalation parameters
        # for field in self.intercalation_params.values():
        #     field.set_value("")

        # Reset visualization settings
        for checkbox in self.visualization_checkboxes.values():
            checkbox.set_value(False)

    # Event handlers for buttons
    def _on_plot_inter_in_c_structure(self) -> None:
        """Handle plot inter in C structure button click."""
        if "plot_inter_in_c_structure" in self.callbacks:
            self.callbacks["plot_inter_in_c_structure"]()
            self.refresh_files_after_action()

    def _on_generate_inter_plane_coordinates(self) -> None:
        """Handle generate inter plane coordinates button click."""
        if "generate_inter_plane_coordinates" in self.callbacks:
            self.callbacks["generate_inter_plane_coordinates"]()
            self.refresh_files_after_action()

    def _on_update_inter_plane_coordinates(self) -> None:
        """Handle update inter plane coordinates button click."""
        if "update_inter_plane_coordinates" in self.callbacks:
            self.callbacks["update_inter_plane_coordinates"]()
            self.refresh_files_after_action()

    def _on_translate_inter_atoms(self) -> None:
        """Handle translate inter atoms button click."""
        if "translate_inter_atoms" in self.callbacks:
            self.callbacks["translate_inter_atoms"]()
            self.refresh_files_after_action()

    def _on_update_inter_channel_coordinates(self) -> None:
        """Handle update inter channel coordinates button click."""
        if "update_inter_channel_coordinates" in self.callbacks:
            self.callbacks["update_inter_channel_coordinates"]()
            self.refresh_files_after_action()

    def _on_save_inter_in_channel_details(self) -> None:
        """Handle save inter in channel details button click."""
        if "save_inter_in_channel_details" in self.callbacks:
            self.callbacks["save_inter_in_channel_details"]()
            self.refresh_files_after_action()

    def _on_get_inter_in_channel_details(self) -> None:
        """Handle get inter in channel details button click."""
        if "get_inter_in_channel_details" in self.callbacks:
            self.callbacks["get_inter_in_channel_details"]()
            self.refresh_files_after_action()

    def _on_get_inter_chc_constants(self) -> None:
        """Handle get intercalation constants button click."""
        if "get_inter_chc_constants" in self.callbacks:
            self.callbacks["get_inter_chc_constants"]()
            self.refresh_files_after_action()

    def _on_translate_inter_to_all_channels_plot(self) -> None:
        """Handle translate inter to all channels plot button click."""
        if "translate_inter_to_all_channels_plot" in self.callbacks:
            self.callbacks["translate_inter_to_all_channels_plot"]()
            self.refresh_files_after_action()

    def _on_translate_inter_to_all_channels_generate(self) -> None:
        """Handle translate inter to all channels generate button click."""
        if "translate_inter_to_all_channels_generate" in self.callbacks:
            self.callbacks["translate_inter_to_all_channels_generate"]()
            self.refresh_files_after_action()

    def _on_file_selected(self, file_name: str) -> None:
        """Handle file selection from dropdown."""
        if "file_selected" in self.callbacks:
            self.callbacks["file_selected"](file_name)

    def get_selected_file(self) -> str:
        """Get selected file from the dropdown."""
        if self.file_selection_dropdown:
            return self.file_selection_dropdown.get()
        return ""

    def get_operation_settings(self) -> dict[str, Any]:
        """Get operation settings from the UI."""
        settings: dict[str, Any] = {}

        # Combine all settings from different UI components
        settings.update(self.get_intercalation_parameters())
        settings.update(self.get_visualization_settings())
        settings.update(self.get_coordinate_limits())

        return settings

    # Auto-sync callback methods
    def _on_bonds_num_changed(self, value: str) -> None:
        """Handle bonds number input change."""
        if hasattr(self, '_presenter_auto_sync_callback'):
            self._presenter_auto_sync_callback('bonds_num_of_min_distances', value)

    def _on_bonds_skip_changed(self, value: str) -> None:
        """Handle bonds skip input change."""
        if hasattr(self, '_presenter_auto_sync_callback'):
            self._presenter_auto_sync_callback('bonds_skip_first_distances', value)

    def _on_coordinate_limits_changed(self, param_name: str, value: str) -> None:
        """Handle coordinate limits change from template."""
        if hasattr(self, '_presenter_auto_sync_callback'):
            self._presenter_auto_sync_callback(param_name, value)

    def _on_number_of_planes_changed(self, value: str) -> None:
        """Handle number of planes input change."""
        if hasattr(self, '_presenter_auto_sync_callback'):
            self._presenter_auto_sync_callback('number_of_planes', value)

    def _on_num_inter_atoms_layers_changed(self, value: str) -> None:
        """Handle number of inter atoms layers input change."""
        if hasattr(self, '_presenter_auto_sync_callback'):
            self._presenter_auto_sync_callback('num_of_inter_atoms_layers', value)

    def _on_lattice_type_changed(self, value: str) -> None:
        """Handle lattice type input change."""
        if hasattr(self, '_presenter_auto_sync_callback'):
            self._presenter_auto_sync_callback('inter_atoms_lattice_type', value)

    def set_auto_sync_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set the auto-sync callback for parameter updates."""
        self._presenter_auto_sync_callback: Callable[[str, str], None] = callback
        # Set callback on coordinate limits template
        if self.coordinate_limits_template:
            self.coordinate_limits_template.set_change_callback(self._on_coordinate_limits_changed)

    def start_file_list_refresh(self) -> None:
        """Start periodic refresh of file list every 1 second."""
        self._schedule_file_refresh()

    def stop_file_list_refresh(self) -> None:
        """Stop periodic refresh of file list."""
        if self._refresh_job_id:
            self.after_cancel(self._refresh_job_id)
            self._refresh_job_id = None

    def _schedule_file_refresh(self) -> None:
        """Schedule the next file refresh."""
        if self._refresh_job_id:
            self.after_cancel(self._refresh_job_id)
        self._refresh_job_id = self.after(1000, self._refresh_file_list)

    def _refresh_file_list(self) -> None:
        """Refresh the file list by calling the presenter to update available files."""
        if "refresh_files" in self.callbacks:
            self.callbacks["refresh_files"]()
        # Schedule next refresh
        self._schedule_file_refresh()

    def refresh_files_after_action(self) -> None:
        """Refresh file list immediately after any action is performed."""
        if "refresh_files" in self.callbacks:
            self.callbacks["refresh_files"]()

    def set_available_files(self, files: list[str]) -> None:
        """Set available files for selection with auto-selection logic."""
        if not self.file_selection_dropdown:
            return

        # Store current selection
        current_selection = self.file_selection_dropdown.get()

        # Check if files list has changed
        if files == self._last_files_list:
            return

        self._last_files_list = files.copy()

        # Handle different file list scenarios
        if not files or files == ["No files found"]:
            # No files available
            self.file_selection_dropdown.configure(values=["None"])
            self.file_selection_dropdown.set("None")
        else:
            # Files are available
            self.file_selection_dropdown.configure(values=files)

            # Auto-selection logic
            if current_selection in files:
                # Keep current selection if it's still valid
                self.file_selection_dropdown.set(current_selection)
            else:
                # Select first file if current selection is invalid or doesn't exist
                self.file_selection_dropdown.set(files[0])
                # Notify presenter about the file change
                if "file_selected" in self.callbacks:
                    self.callbacks["file_selected"](files[0])
