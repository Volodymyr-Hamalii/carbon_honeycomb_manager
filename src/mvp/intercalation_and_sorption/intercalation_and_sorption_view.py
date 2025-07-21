"""View for intercalation and sorption functionality."""

import customtkinter as ctk
from typing import Any, Callable
from pathlib import Path
import pandas as pd

from src.interfaces import IIntercalationAndSorptionView
from src.mvp.general import GeneralView
from src.ui.components import Button, CheckBox, InputField, InputFieldCoordLimits, DropdownList, Table
from src.ui.templates import ScrollableToplevel
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
        # self.intercalation_params: dict[str, InputField] = {}
        self.visualization_checkboxes: dict[str, CheckBox] = {}
        self.coordinate_limits: dict[str, InputFieldCoordLimits] = {}
        self.operation_buttons: dict[str, Button] = {}
        self.file_selection_dropdown: DropdownList | None = None

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

        # Visualization settings
        viz_frame = ctk.CTkFrame(main_frame)
        viz_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(viz_frame, text="Visualization Settings",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.visualization_checkboxes["show_carbon"] = CheckBox(viz_frame, text="Show carbon structure")
        self.visualization_checkboxes["show_carbon"].pack(pady=2)

        self.visualization_checkboxes["show_intercalated"] = CheckBox(viz_frame, text="Show intercalated atoms")
        self.visualization_checkboxes["show_intercalated"].pack(pady=2)

        self.visualization_checkboxes["show_bonds"] = CheckBox(viz_frame, text="Show bonds")
        self.visualization_checkboxes["show_bonds"].pack(pady=2)

        self.visualization_checkboxes["show_channels"] = CheckBox(viz_frame, text="Show channels")
        self.visualization_checkboxes["show_channels"].pack(pady=2)

        # Coordinate limits
        coord_frame = ctk.CTkFrame(main_frame)
        coord_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(coord_frame, text="Coordinate Limits",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        self.coordinate_limits["x"] = InputFieldCoordLimits(coord_frame, "X limits")
        self.coordinate_limits["x"].pack(pady=2)

        self.coordinate_limits["y"] = InputFieldCoordLimits(coord_frame, "Y limits")
        self.coordinate_limits["y"].pack(pady=2)

        self.coordinate_limits["z"] = InputFieldCoordLimits(coord_frame, "Z limits")
        self.coordinate_limits["z"].pack(pady=2)

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

    def get_visualization_settings(self) -> dict[str, Any]:
        """Get visualization settings from the UI."""
        settings = {}
        for key, checkbox in self.visualization_checkboxes.items():
            settings[key] = checkbox.get()
        return settings

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits in the UI."""
        for axis in ["x", "y", "z"]:
            if axis in self.coordinate_limits:
                min_key = f"{axis}_min"
                max_key = f"{axis}_max"
                if min_key in limits:
                    self.coordinate_limits[axis].set_min_value(str(limits[min_key]))
                if max_key in limits:
                    self.coordinate_limits[axis].set_max_value(str(limits[max_key]))

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits from the UI."""
        limits = {}
        for axis, field in self.coordinate_limits.items():
            try:
                limits[f"{axis}_min"] = float(field.get_min_value())
                limits[f"{axis}_max"] = float(field.get_max_value())
            except ValueError:
                limits[f"{axis}_min"] = 0.0
                limits[f"{axis}_max"] = 100.0
        return limits

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
        # settings.update(self.get_intercalation_parameters())
        settings.update(self.get_visualization_settings())
        settings.update(self.get_coordinate_limits())
        
        return settings
