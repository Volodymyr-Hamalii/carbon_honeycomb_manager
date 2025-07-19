"""View for init data functionality."""
import customtkinter as ctk
from typing import Any, Callable
import pandas as pd

from src.interfaces import IShowInitDataView
from src.mvp.general import GeneralView
from src.ui.components import (
    Button,
    CheckBox,
    DropdownList,
    InputField,
    InputFieldCoordLimits,
)
from src.services import Logger


logger = Logger("InitDataView")


class InitDataView(GeneralView, IShowInitDataView):
    """View for init data functionality."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Carbon Honeycomb Init Data Viewer")
        self.geometry("600x800")
        
        # Context variables
        self.project_dir = ""
        self.subproject_dir = ""
        self.structure_dir = ""
        
        # UI components
        self.file_names_dropdown: DropdownList | None = None
        self.to_build_bonds_checkbox: CheckBox | None = None
        self.to_show_coordinates_checkbox: CheckBox | None = None
        self.to_show_c_indexes_checkbox: CheckBox | None = None
        self.bonds_num_of_min_distances_input: InputField | None = None
        self.bonds_skip_first_distances_input: InputField | None = None
        self.coord_x_limits_input: InputFieldCoordLimits | None = None
        self.coord_y_limits_input: InputFieldCoordLimits | None = None
        self.coord_z_limits_input: InputFieldCoordLimits | None = None
        
        # Buttons
        self.init_structure_btn: Button | None = None
        self.one_channel_structure_btn: Button | None = None
        self.channel_2d_scheme_btn: Button | None = None
        self.channel_params_btn: Button | None = None
        
        # Callbacks
        self.callbacks: dict[str, Callable] = {}

    def set_context(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Set the context for this view."""
        self.project_dir: str = project_dir
        self.subproject_dir: str = subproject_dir
        self.structure_dir: str = structure_dir
        self.title(f"Init Data Viewer - {project_dir}/{subproject_dir}/{structure_dir}")

    def set_ui(self) -> None:
        """Set up the UI components."""
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File selection
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(file_frame, text="File Selection").pack(pady=5)
        self.file_names_dropdown = DropdownList(file_frame, ["None"])
        self.file_names_dropdown.pack(pady=5)
        
        # Visualization settings
        viz_frame = ctk.CTkFrame(main_frame)
        viz_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(viz_frame, text="Visualization Settings").pack(pady=5)
        
        self.to_build_bonds_checkbox = CheckBox(viz_frame, text="Build bonds")
        self.to_build_bonds_checkbox.pack(pady=2)
        
        self.to_show_coordinates_checkbox = CheckBox(viz_frame, text="Show coordinates")
        self.to_show_coordinates_checkbox.pack(pady=2)
        
        self.to_show_c_indexes_checkbox = CheckBox(viz_frame, text="Show C atoms indexes")
        self.to_show_c_indexes_checkbox.pack(pady=2)
        
        self.bonds_num_of_min_distances_input = InputField(
            viz_frame, "Number of min distances for bonds"
        )
        self.bonds_num_of_min_distances_input.pack(pady=2)
        
        self.bonds_skip_first_distances_input = InputField(
            viz_frame, "Skip first distances for bonds"
        )
        self.bonds_skip_first_distances_input.pack(pady=2)
        
        # Coordinate limits
        coord_frame = ctk.CTkFrame(main_frame)
        coord_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(coord_frame, text="Coordinate Limits").pack(pady=5)
        
        self.coord_x_limits_input = InputFieldCoordLimits(coord_frame, "X limits")
        self.coord_x_limits_input.pack(pady=2)
        
        self.coord_y_limits_input = InputFieldCoordLimits(coord_frame, "Y limits")
        self.coord_y_limits_input.pack(pady=2)
        
        self.coord_z_limits_input = InputFieldCoordLimits(coord_frame, "Z limits")
        self.coord_z_limits_input.pack(pady=2)
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(button_frame, text="Visualizations").pack(pady=5)
        
        self.init_structure_btn = Button(
            button_frame, text="Show Initial Structure", 
            command=self._on_show_init_structure,
        )
        self.init_structure_btn.pack(pady=5)
        
        self.one_channel_structure_btn = Button(
            button_frame, text="Show One Channel", 
            command=self._on_show_one_channel,
        )
        self.one_channel_structure_btn.pack(pady=5)
        
        self.channel_2d_scheme_btn = Button(
            button_frame, text="Show 2D Channel Scheme", 
            command=self._on_show_2d_scheme,
        )
        self.channel_2d_scheme_btn.pack(pady=5)
        
        self.channel_params_btn = Button(
            button_frame, text="Get Channel Parameters", 
            command=self._on_get_channel_params,
        )
        self.channel_params_btn.pack(pady=5)

    def set_visualization_settings(self, settings: dict[str, Any]) -> None:
        """Set visualization settings in the UI."""
        if self.to_build_bonds_checkbox and "to_build_bonds" in settings:
            self.to_build_bonds_checkbox.set_value(settings["to_build_bonds"])
        
        if self.to_show_coordinates_checkbox and "to_show_coordinates" in settings:
            self.to_show_coordinates_checkbox.set_value(settings["to_show_coordinates"])
        
        if self.to_show_c_indexes_checkbox and "to_show_c_indexes" in settings:
            self.to_show_c_indexes_checkbox.set_value(settings["to_show_c_indexes"])
        
        if self.bonds_num_of_min_distances_input and "bonds_num_of_min_distances" in settings:
            self.bonds_num_of_min_distances_input.set_value(str(settings["bonds_num_of_min_distances"]))
        
        if self.bonds_skip_first_distances_input and "bonds_skip_first_distances" in settings:
            self.bonds_skip_first_distances_input.set_value(str(settings["bonds_skip_first_distances"]))

    def get_visualization_settings(self) -> dict[str, Any]:
        """Get visualization settings from the UI."""
        settings: dict[str, Any] = {}
        
        if self.to_build_bonds_checkbox:
            settings["to_build_bonds"] = self.to_build_bonds_checkbox.get()
        
        if self.to_show_coordinates_checkbox:
            settings["to_show_coordinates"] = self.to_show_coordinates_checkbox.get()
        
        if self.to_show_c_indexes_checkbox:
            settings["to_show_c_indexes"] = self.to_show_c_indexes_checkbox.get()
        
        if self.bonds_num_of_min_distances_input:
            try:
                settings["bonds_num_of_min_distances"] = int(
                    self.bonds_num_of_min_distances_input.get_value()
                )
            except ValueError:
                settings["bonds_num_of_min_distances"] = 5
        
        if self.bonds_skip_first_distances_input:
            try:
                settings["bonds_skip_first_distances"] = int(
                    self.bonds_skip_first_distances_input.get_value()
                )
            except ValueError:
                settings["bonds_skip_first_distances"] = 0
        
        return settings

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits in the UI."""
        if self.coord_x_limits_input:
            self.coord_x_limits_input.set_min_value(str(limits.get("x_min", -float("inf"))))
            self.coord_x_limits_input.set_max_value(str(limits.get("x_max", float("inf"))))
        
        if self.coord_y_limits_input:
            self.coord_y_limits_input.set_min_value(str(limits.get("y_min", -float("inf"))))
            self.coord_y_limits_input.set_max_value(str(limits.get("y_max", float("inf"))))
        
        if self.coord_z_limits_input:
            self.coord_z_limits_input.set_min_value(str(limits.get("z_min", -float("inf"))))
            self.coord_z_limits_input.set_max_value(str(limits.get("z_max", float("inf"))))

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits from the UI."""
        limits: dict[str, float] = {}
        
        if self.coord_x_limits_input:
            try:
                limits["x_min"] = float(self.coord_x_limits_input.get_min_value())
                limits["x_max"] = float(self.coord_x_limits_input.get_max_value())
            except ValueError:
                limits["x_min"] = -float("inf")
                limits["x_max"] = float("inf")
        
        if self.coord_y_limits_input:
            try:
                limits["y_min"] = float(self.coord_y_limits_input.get_min_value())
                limits["y_max"] = float(self.coord_y_limits_input.get_max_value())
            except ValueError:
                limits["y_min"] = -float("inf")
                limits["y_max"] = float("inf")
        
        if self.coord_z_limits_input:
            try:
                limits["z_min"] = float(self.coord_z_limits_input.get_min_value())
                limits["z_max"] = float(self.coord_z_limits_input.get_max_value())
            except ValueError:
                limits["z_min"] = -float("inf")
                limits["z_max"] = float("inf")
        
        return limits

    def set_channel_display_settings(self, settings: dict[str, Any]) -> None:
        """Set channel display settings in the UI."""
        # These would be additional checkboxes for channel-specific display options
        pass

    def get_channel_display_settings(self) -> dict[str, Any]:
        """Get channel display settings from the UI."""
        # These would be additional checkboxes for channel-specific display options
        return {}

    def show_visualization_progress(self, message: str) -> None:
        """Show visualization progress to user."""
        self.show_status_message(f"Processing: {message}")

    def show_visualization_success(self, message: str) -> None:
        """Show successful visualization result."""
        self.show_success_message(message)

    def show_visualization_error(self, error_message: str) -> None:
        """Show visualization error to user."""
        self.show_error_message(error_message)

    def display_channel_parameters(self, parameters: pd.DataFrame) -> None:
        """Display channel parameters in the UI."""
        # Create a new window to display the DataFrame
        param_window = ctk.CTkToplevel(self)
        param_window.title("Channel Parameters")
        param_window.geometry("400x300")
        
        # Create a text widget to display the parameters
        text_widget = ctk.CTkTextbox(param_window)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insert the DataFrame as text
        text_widget.insert("0.0", parameters.to_string(index=False))

    def set_visualization_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for visualization buttons."""
        self.callbacks = callbacks

    def enable_controls(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        state = "normal" if enabled else "disabled"
        
        controls: list[Button | None] = [
            self.init_structure_btn,
            self.one_channel_structure_btn,
            self.channel_2d_scheme_btn,
            self.channel_params_btn,
        ]
        
        for control in controls:
            if control:
                control.configure(state=state)

    def reset_form(self) -> None:
        """Reset the form to default values."""
        if self.to_build_bonds_checkbox:
            self.to_build_bonds_checkbox.set_value(True)
        
        if self.to_show_coordinates_checkbox:
            self.to_show_coordinates_checkbox.set_value(False)
        
        if self.to_show_c_indexes_checkbox:
            self.to_show_c_indexes_checkbox.set_value(False)
        
        if self.bonds_num_of_min_distances_input:
            self.bonds_num_of_min_distances_input.set_value("5")
        
        if self.bonds_skip_first_distances_input:
            self.bonds_skip_first_distances_input.set_value("0")

    def _on_show_init_structure(self) -> None:
        """Handle show init structure button click."""
        if "show_init_structure" in self.callbacks:
            self.callbacks["show_init_structure"]()

    def _on_show_one_channel(self) -> None:
        """Handle show one channel button click."""
        if "show_one_channel_structure" in self.callbacks:
            self.callbacks["show_one_channel_structure"]()

    def _on_show_2d_scheme(self) -> None:
        """Handle show 2D scheme button click."""
        if "show_2d_channel_scheme" in self.callbacks:
            self.callbacks["show_2d_channel_scheme"]()

    def _on_get_channel_params(self) -> None:
        """Handle get channel parameters button click."""
        if "get_channel_params" in self.callbacks:
            self.callbacks["get_channel_params"]()

    def set_available_files(self, files: list[str]) -> None:
        """Set available files in dropdown."""
        if self.file_names_dropdown:
            self.file_names_dropdown.configure(values=files)
            if files:
                self.file_names_dropdown.set(files[0])

    def get_selected_file(self) -> str:
        """Get currently selected file."""
        if self.file_names_dropdown:
            return self.file_names_dropdown.get()
        return "None"