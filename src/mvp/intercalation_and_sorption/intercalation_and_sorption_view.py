"""View for intercalation and sorption functionality."""

import customtkinter as ctk
from typing import Any, Callable
from pathlib import Path
import pandas as pd

from src.interfaces import IIntercalationAndSorptionView
from src.mvp.general import GeneralView
from src.ui.components import Button, CheckBox, InputField, DropdownList, Table
from src.ui.templates import ScrollableToplevel, CoordinateLimitsTemplate
from src.services import Logger

logger = Logger("IntercalationAndSorptionView")


class IntercalationAndSorptionView(GeneralView, IIntercalationAndSorptionView):
    """View for intercalation and sorption functionality."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Intercalation and Sorption")
        self.geometry("700x900")

        # Context variables
        self.project_dir = ""
        self.subproject_dir = ""
        self.structure_dir = ""

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

    def set_context(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Set the context for this view."""
        self.project_dir = project_dir
        self.subproject_dir = subproject_dir
        self.structure_dir = structure_dir
        self.title(f"Intercalation & Sorption - {project_dir}/{subproject_dir}/{structure_dir}")

    def set_ui(self) -> None:
        """Set up the UI components."""
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

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

        # File selection
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(file_frame, text="File Selection",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        ctk.CTkLabel(file_frame, text="Select intercalated structure file:").pack(pady=2)
        self.file_selection_dropdown = DropdownList(file_frame, ["Loading..."], command=self._on_file_selected)
        self.file_selection_dropdown.pack(pady=2)

        # Visualization settings - organized in columns
        viz_frame = ctk.CTkFrame(main_frame)
        viz_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(viz_frame, text="Visualization Settings",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Create two columns for better organization
        columns_frame = ctk.CTkFrame(viz_frame, fg_color="transparent")
        columns_frame.pack(fill="x", padx=10, pady=5)

        # Left column - Structure display
        left_column = ctk.CTkFrame(columns_frame)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(left_column, text="Structure Display", 
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=2)

        self.visualization_checkboxes["to_build_bonds"] = CheckBox(left_column, text="Build bonds")
        self.visualization_checkboxes["to_build_bonds"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_show_coordinates"] = CheckBox(left_column, text="Show coordinates")
        self.visualization_checkboxes["to_show_coordinates"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_show_c_indexes"] = CheckBox(left_column, text="Show carbon atom indexes")
        self.visualization_checkboxes["to_show_c_indexes"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_show_inter_atoms_indexes"] = CheckBox(left_column, text="Show intercalated atom indexes")
        self.visualization_checkboxes["to_show_inter_atoms_indexes"].pack(pady=1, anchor="w")

        # Right column - Channel analysis
        right_column = ctk.CTkFrame(columns_frame)
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(right_column, text="Channel Analysis", 
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=2)

        self.visualization_checkboxes["to_show_dists_to_plane"] = CheckBox(right_column, text="Show distances to plane")
        self.visualization_checkboxes["to_show_dists_to_plane"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_show_dists_to_edges"] = CheckBox(right_column, text="Show distances to edges")
        self.visualization_checkboxes["to_show_dists_to_edges"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_show_channel_angles"] = CheckBox(right_column, text="Show channel angles")
        self.visualization_checkboxes["to_show_channel_angles"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_show_plane_lengths"] = CheckBox(right_column, text="Show plane lengths")
        self.visualization_checkboxes["to_show_plane_lengths"].pack(pady=1, anchor="w")

        # Bonds parameters section
        bonds_frame = ctk.CTkFrame(viz_frame)
        bonds_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(bonds_frame, text="Bond Parameters", 
                     font=ctk.CTkFont(size=12, weight="bold")).pack(pady=2)

        bonds_row = ctk.CTkFrame(bonds_frame, fg_color="transparent")
        bonds_row.pack(fill="x", pady=2)

        self.bonds_num_input = InputField(
            bonds_row, "Number of min distances",
            change_callback=self._on_bonds_num_changed
        )
        self.bonds_num_input.pack(side="left", padx=(0, 5), fill="x", expand=True)

        self.bonds_skip_input = InputField(
            bonds_row, "Skip first distances",
            change_callback=self._on_bonds_skip_changed
        )
        self.bonds_skip_input.pack(side="right", padx=(5, 0), fill="x", expand=True)

        # Coordinate limits using template
        self.coordinate_limits_template = CoordinateLimitsTemplate(
            main_frame,
            title="Plot coordinate limits"
        )
        self.coordinate_limits_template.pack(fill="x", pady=(0, 10))

        # Intercalation parameters
        inter_frame = ctk.CTkFrame(main_frame)
        inter_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(inter_frame, text="Intercalation Parameters",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Organize intercalation params in columns
        inter_columns = ctk.CTkFrame(inter_frame, fg_color="transparent")
        inter_columns.pack(fill="x", padx=10, pady=5)

        # Left column - Basic parameters
        inter_left = ctk.CTkFrame(inter_columns)
        inter_left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.intercalation_params["number_of_planes"] = InputField(
            inter_left, "Number of planes",
            change_callback=self._on_number_of_planes_changed
        )
        self.intercalation_params["number_of_planes"].pack(pady=2, fill="x")

        self.intercalation_params["num_of_inter_atoms_layers"] = InputField(
            inter_left, "Number of inter atom layers",
            change_callback=self._on_num_inter_atoms_layers_changed
        )
        self.intercalation_params["num_of_inter_atoms_layers"].pack(pady=2, fill="x")

        self.intercalation_params["inter_atoms_lattice_type"] = InputField(
            inter_left, "Inter atoms lattice type",
            change_callback=self._on_lattice_type_changed
        )
        self.intercalation_params["inter_atoms_lattice_type"].pack(pady=2, fill="x")

        # Right column - Boolean flags
        inter_right = ctk.CTkFrame(inter_columns)
        inter_right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.visualization_checkboxes["to_translate_inter"] = CheckBox(inter_right, text="Translate intercalated atoms")
        self.visualization_checkboxes["to_translate_inter"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_replace_nearby_atoms"] = CheckBox(inter_right, text="Replace nearby atoms")
        self.visualization_checkboxes["to_replace_nearby_atoms"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_remove_too_close_atoms"] = CheckBox(inter_right, text="Remove too close atoms")
        self.visualization_checkboxes["to_remove_too_close_atoms"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_to_try_to_reflect_inter_atoms"] = CheckBox(inter_right, text="Try to reflect inter atoms")
        self.visualization_checkboxes["to_to_try_to_reflect_inter_atoms"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_equidistant_inter_points"] = CheckBox(inter_right, text="Equidistant inter points")
        self.visualization_checkboxes["to_equidistant_inter_points"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_filter_inter_atoms"] = CheckBox(inter_right, text="Filter inter atoms")
        self.visualization_checkboxes["to_filter_inter_atoms"].pack(pady=1, anchor="w")

        self.visualization_checkboxes["to_remove_inter_atoms_with_min_and_max_x_coordinates"] = CheckBox(inter_right, text="Remove atoms at X boundaries")
        self.visualization_checkboxes["to_remove_inter_atoms_with_min_and_max_x_coordinates"].pack(pady=1, anchor="w")

        # Operation buttons
        operations_frame = ctk.CTkFrame(main_frame)
        operations_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(operations_frame, text="Operations",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Create operation buttons in groups
        plot_frame = ctk.CTkFrame(operations_frame)
        plot_frame.pack(fill="x", pady=5)

        self.operation_buttons["plot_inter_in_c_structure"] = Button(
            plot_frame, text="Plot Intercalated Atoms in C Structure",
            command=self._on_plot_inter_in_c_structure
        )
        self.operation_buttons["plot_inter_in_c_structure"].pack(pady=2)

        coords_frame = ctk.CTkFrame(operations_frame)
        coords_frame.pack(fill="x", pady=5)

        self.operation_buttons["generate_inter_plane_coordinates"] = Button(
            coords_frame, text="Generate Plane Coordinates",
            command=self._on_generate_inter_plane_coordinates
        )
        self.operation_buttons["generate_inter_plane_coordinates"].pack(pady=2)

        self.operation_buttons["update_inter_plane_coordinates"] = Button(
            coords_frame, text="Update Plane Coordinates",
            command=self._on_update_inter_plane_coordinates
        )
        self.operation_buttons["update_inter_plane_coordinates"].pack(pady=2)

        self.operation_buttons["translate_inter_atoms"] = Button(
            coords_frame, text="Translate Atoms to Other Planes",
            command=self._on_translate_inter_atoms
        )
        self.operation_buttons["translate_inter_atoms"].pack(pady=2)

        channel_frame = ctk.CTkFrame(operations_frame)
        channel_frame.pack(fill="x", pady=5)

        self.operation_buttons["update_inter_channel_coordinates"] = Button(
            channel_frame, text="Update Channel Coordinates",
            command=self._on_update_inter_channel_coordinates
        )
        self.operation_buttons["update_inter_channel_coordinates"].pack(pady=2)

        self.operation_buttons["save_inter_in_channel_details"] = Button(
            channel_frame, text="Save Channel Details",
            command=self._on_save_inter_in_channel_details
        )
        self.operation_buttons["save_inter_in_channel_details"].pack(pady=2)

        self.operation_buttons["get_inter_in_channel_details"] = Button(
            channel_frame, text="Get Channel Details",
            command=self._on_get_inter_in_channel_details
        )
        self.operation_buttons["get_inter_in_channel_details"].pack(pady=2)

        all_channels_frame = ctk.CTkFrame(operations_frame)
        all_channels_frame.pack(fill="x", pady=5)

        self.operation_buttons["translate_inter_to_all_channels_plot"] = Button(
            all_channels_frame, text="Plot All Channels",
            command=self._on_translate_inter_to_all_channels_plot
        )
        self.operation_buttons["translate_inter_to_all_channels_plot"].pack(pady=2)

        self.operation_buttons["translate_inter_to_all_channels_generate"] = Button(
            all_channels_frame, text="Generate All Channels Files",
            command=self._on_translate_inter_to_all_channels_generate
        )
        self.operation_buttons["translate_inter_to_all_channels_generate"].pack(pady=2)

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

        width: int = min(len(details.columns) * 50 + 100, 1000)
        height: int = min(len(details) * 20 + 100, 1000)
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
        constants_window.geometry("450x200")

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
        state = "normal" if enabled else "disabled"

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

        # Reset coordinate limits
        for field in self.coordinate_limits.values():
            field.set_min_value("0.0")
            field.set_max_value("100.0")

    # Event handlers for buttons
    def _on_plot_inter_in_c_structure(self) -> None:
        """Handle plot inter in C structure button click."""
        if "plot_inter_in_c_structure" in self.callbacks:
            self.callbacks["plot_inter_in_c_structure"]()

    def _on_generate_inter_plane_coordinates(self) -> None:
        """Handle generate inter plane coordinates button click."""
        if "generate_inter_plane_coordinates" in self.callbacks:
            self.callbacks["generate_inter_plane_coordinates"]()

    def _on_update_inter_plane_coordinates(self) -> None:
        """Handle update inter plane coordinates button click."""
        if "update_inter_plane_coordinates" in self.callbacks:
            self.callbacks["update_inter_plane_coordinates"]()

    def _on_translate_inter_atoms(self) -> None:
        """Handle translate inter atoms button click."""
        if "translate_inter_atoms" in self.callbacks:
            self.callbacks["translate_inter_atoms"]()

    def _on_update_inter_channel_coordinates(self) -> None:
        """Handle update inter channel coordinates button click."""
        if "update_inter_channel_coordinates" in self.callbacks:
            self.callbacks["update_inter_channel_coordinates"]()

    def _on_save_inter_in_channel_details(self) -> None:
        """Handle save inter in channel details button click."""
        if "save_inter_in_channel_details" in self.callbacks:
            self.callbacks["save_inter_in_channel_details"]()

    def _on_get_inter_in_channel_details(self) -> None:
        """Handle get inter in channel details button click."""
        if "get_inter_in_channel_details" in self.callbacks:
            self.callbacks["get_inter_in_channel_details"]()

    def _on_translate_inter_to_all_channels_plot(self) -> None:
        """Handle translate inter to all channels plot button click."""
        if "translate_inter_to_all_channels_plot" in self.callbacks:
            self.callbacks["translate_inter_to_all_channels_plot"]()

    def _on_translate_inter_to_all_channels_generate(self) -> None:
        """Handle translate inter to all channels generate button click."""
        if "translate_inter_to_all_channels_generate" in self.callbacks:
            self.callbacks["translate_inter_to_all_channels_generate"]()

    def _on_file_selected(self, file_name: str) -> None:
        """Handle file selection from dropdown."""
        if "file_selected" in self.callbacks:
            self.callbacks["file_selected"](file_name)

    def set_available_files(self, files: list[str]) -> None:
        """Set available files for selection."""
        if self.file_selection_dropdown:
            self.file_selection_dropdown.configure(values=files)
            if files and files[0] != "Loading...":
                self.file_selection_dropdown.set(files[0])

    def get_selected_file(self) -> str:
        """Get selected file from the dropdown."""
        if self.file_selection_dropdown:
            return self.file_selection_dropdown.get()
        return ""

    def get_operation_settings(self) -> dict[str, Any]:
        """Get operation settings from the UI."""
        settings = {}
        
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
        self._presenter_auto_sync_callback = callback
        # Set callback on coordinate limits template
        if self.coordinate_limits_template:
            self.coordinate_limits_template.set_change_callback(self._on_coordinate_limits_changed)
