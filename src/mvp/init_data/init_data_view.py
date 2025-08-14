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
    Table,
)
from src.ui.templates import ScrollableToplevel, CoordinateLimitsTemplate, WindowGeneralTemplate
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

        # UI template
        self.template = WindowGeneralTemplate()

        # UI components
        self.file_names_dropdown: DropdownList | None = None
        self.to_build_bonds_checkbox: CheckBox | None = None
        self.to_show_coordinates_checkbox: CheckBox | None = None
        self.to_show_c_indexes_checkbox: CheckBox | None = None
        self.bonds_num_of_min_distances_input: InputField | None = None
        self.bonds_skip_first_distances_input: InputField | None = None
        self.coordinate_limits_template: CoordinateLimitsTemplate | None = None

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
        # Create main layout using template
        main_frame: ctk.CTkScrollableFrame = self.template.create_main_layout(self)

        # Action buttons section
        button_frame: ctk.CTkFrame = self.template.create_section_frame(main_frame, "Visualizations")

        self.init_structure_btn = self.template.pack_button(
            button_frame, "Show Initial Structure", self._on_show_init_structure
        )
        self.one_channel_structure_btn = self.template.pack_button(
            button_frame, "Show One Channel", self._on_show_one_channel
        )
        self.channel_2d_scheme_btn = self.template.pack_button(
            button_frame, "Show 2D Channel Scheme", self._on_show_2d_scheme
        )
        self.channel_params_btn = self.template.pack_button(
            button_frame, "Get Channel Parameters", self._on_get_channel_params
        )

        # File selection section
        file_frame: ctk.CTkFrame = self.template.create_section_frame(main_frame, "File Selection")
        self.file_names_dropdown = DropdownList(file_frame, ["None"])
        self.file_names_dropdown.pack(pady=5)

        # Visualization settings section (hidden - controls moved to PlotWindow)
        # viz_frame: ctk.CTkFrame = self.template.create_section_frame(main_frame, "Visualization Settings")

        # Create checkboxes using template helper (hidden - moved to PlotWindow)
        # self.to_build_bonds_checkbox = self.template.pack_check_box(
        #     viz_frame, "Build bonds"
        # )
        # self.to_show_coordinates_checkbox = self.template.pack_check_box(
        #     viz_frame, "Show coordinates"
        # )
        # self.to_show_c_indexes_checkbox = self.template.pack_check_box(
        #     viz_frame, "Show C atoms indexes"
        # )

        # Create input fields using template helper (hidden - moved to PlotWindow)
        # self.bonds_num_of_min_distances_input = self.template.pack_input_field(
        #     viz_frame, 
        #     "Number of min distances for bonds",
        #     change_callback=self._on_bonds_num_changed
        # )
        # self.bonds_skip_first_distances_input = self.template.pack_input_field(
        #     viz_frame, 
        #     "Skip first distances for bonds",
        #     change_callback=self._on_bonds_skip_changed
        # )

        # Coordinate limits using template (hidden - moved to PlotWindow)
        # self.coordinate_limits_template = self.template.create_coordinate_limits_section(
        #     main_frame,
        #     change_callback=self._on_coordinate_limits_changed
        # )
        
        # Call parent set_ui to refresh scrolling
        super().set_ui()

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
        # Return empty dict since visualization controls are now in PlotWindow
        settings: dict[str, Any] = {}

        # Controls moved to PlotWindow - return default values
        if self.to_build_bonds_checkbox:
            settings["to_build_bonds"] = self.to_build_bonds_checkbox.get()
        else:
            settings["to_build_bonds"] = True

        if self.to_show_coordinates_checkbox:
            settings["to_show_coordinates"] = self.to_show_coordinates_checkbox.get()
        else:
            settings["to_show_coordinates"] = False

        if self.to_show_c_indexes_checkbox:
            settings["to_show_c_indexes"] = self.to_show_c_indexes_checkbox.get()
        else:
            settings["to_show_c_indexes"] = False

        if self.bonds_num_of_min_distances_input:
            try:
                settings["bonds_num_of_min_distances"] = int(
                    self.bonds_num_of_min_distances_input.get_value()
                )
            except ValueError:
                settings["bonds_num_of_min_distances"] = 5
        else:
            settings["bonds_num_of_min_distances"] = 5

        if self.bonds_skip_first_distances_input:
            try:
                settings["bonds_skip_first_distances"] = int(
                    self.bonds_skip_first_distances_input.get_value()
                )
            except ValueError:
                settings["bonds_skip_first_distances"] = 0
        else:
            settings["bonds_skip_first_distances"] = 0

        return settings

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits in the UI."""
        # Coordinate limits controls moved to PlotWindow
        if self.coordinate_limits_template:
            self.coordinate_limits_template.set_coordinate_limits(limits)

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits from the UI."""
        # Coordinate limits controls moved to PlotWindow - return default values
        if self.coordinate_limits_template:
            return self.coordinate_limits_template.get_coordinate_limits()
        
        # Return default coordinate limits
        return {
            "x_min": -float('inf'),
            "x_max": float('inf'),
            "y_min": -float('inf'),
            "y_max": float('inf'),
            "z_min": -float('inf'),
            "z_max": float('inf'),
        }

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
        # Create a new window with touchpad scrolling support
        param_window = ScrollableToplevel(self)
        param_window.title("Channel Parameters")
        param_window.geometry("800x600")

        # Create and display the table
        table = Table(
            data=parameters,
            master=param_window,
            title="Channel Parameters",
            to_show_index=True
        )
        table.pack(fill="both", expand=True, padx=10, pady=10)

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
        # Visualization controls moved to PlotWindow - only reset file selection
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

    def set_auto_sync_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set the auto-sync callback for parameter updates."""
        self._presenter_auto_sync_callback = callback
        # Set callback on coordinate limits template
        if self.coordinate_limits_template:
            self.coordinate_limits_template.set_change_callback(self._on_coordinate_limits_changed)
