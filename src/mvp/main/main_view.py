from typing import Any, Callable
import customtkinter as ctk
from tkinter import messagebox

from src.interfaces import IMainView
# from src.ui.components.dropdown_list import DropdownList
# from old_gui_logic.windows.windows_template import WindowsTemplate
from src.services import Constants, Logger

logger = Logger("MainView")


class MainView(ctk.CTk, IMainView):
    """Main application view."""

    def __init__(self):
        super().__init__()
        self.title("Carbon Honeycomb Manager")
        self.pack_propagate(True)
        self.grid_propagate(True)
        
        # Initialize UI components
        self._projects_dropdown = None
        self._subprojects_dropdown = None
        self._structures_dropdown = None
        
        # Callbacks
        self._selection_callbacks = {}
        self._action_callbacks = {}
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Project selection
        ctk.CTkLabel(self, text="Select project:").pack(pady=5)
        self._projects_dropdown = ctk.CTkOptionMenu(
            self,
            values=[],
            command=self._on_project_selected,
        )
        self._projects_dropdown.pack(pady=5)
        
        # Subproject selection
        ctk.CTkLabel(self, text="Select subproject:").pack(pady=5)
        self._subprojects_dropdown = ctk.CTkOptionMenu(
            self,
            values=[],
            command=self._on_subproject_selected,
        )
        self._subprojects_dropdown.pack(pady=5)
        
        # Structure selection
        ctk.CTkLabel(self, text="Select structure:").pack(pady=5)
        self._structures_dropdown = ctk.CTkOptionMenu(
            self,
            values=[],
            command=self._on_structure_selected,
        )
        self._structures_dropdown.pack(pady=5)
        
        # Action buttons
        self._create_action_buttons()
        
        # Status bar
        self._status_label = ctk.CTkLabel(self, text="Ready")
        self._status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def _create_action_buttons(self) -> None:
        """Create action buttons."""
        # Button frame
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Data converter button
        self._data_converter_btn = ctk.CTkButton(
            button_frame,
            text="Data Converter",
            command=self._on_data_converter_clicked,
            state="disabled"
        )
        self._data_converter_btn.pack(side="left", padx=5)
        
        # Intercalation and sorption button
        self._intercalation_btn = ctk.CTkButton(
            button_frame,
            text="Intercalation & Sorption",
            command=self._on_intercalation_clicked,
            state="disabled"
        )
        self._intercalation_btn.pack(side="left", padx=5)
        
        # Show init data button
        self._show_init_data_btn = ctk.CTkButton(
            button_frame,
            text="Show Init Data",
            command=self._on_show_init_data_clicked,
            state="disabled"
        )
        self._show_init_data_btn.pack(side="left", padx=5)

    def set_projects(self, projects: list[str]) -> None:
        """Set projects list in the UI."""
        if self._projects_dropdown:
            values = projects if projects else ["No projects"]
            self._projects_dropdown.configure(values=values)
            if projects:
                self._projects_dropdown.set(projects[0])

    def set_subprojects(self, subprojects: list[str]) -> None:
        """Set subprojects list in the UI."""
        if self._subprojects_dropdown:
            values = subprojects if subprojects else ["No subprojects"]
            self._subprojects_dropdown.configure(values=values)
            if subprojects:
                self._subprojects_dropdown.set(subprojects[0])

    def set_structures(self, structures: list[str]) -> None:
        """Set structures list in the UI."""
        if self._structures_dropdown:
            values = structures if structures else ["No structures"]
            self._structures_dropdown.configure(values=values)
            if structures:
                self._structures_dropdown.set(structures[0])

    def get_selected_project(self) -> str:
        """Get selected project from the UI."""
        if self._projects_dropdown:
            return self._projects_dropdown.get()
        return ""

    def get_selected_subproject(self) -> str:
        """Get selected subproject from the UI."""
        if self._subprojects_dropdown:
            return self._subprojects_dropdown.get()
        return ""

    def get_selected_structure(self) -> str:
        """Get selected structure from the UI."""
        if self._structures_dropdown:
            return self._structures_dropdown.get()
        return ""

    def set_selection_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for selection changes."""
        self._selection_callbacks = callbacks

    def set_action_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for action buttons."""
        self._action_callbacks = callbacks

    def show_status_message(self, message: str) -> None:
        """Show status message to user."""
        if hasattr(self, '_status_label'):
            self._status_label.configure(text=message)

    def show_error_message(self, message: str) -> None:
        """Show error message to user."""
        messagebox.showerror("Error", message)

    def enable_actions(self, enabled: bool) -> None:
        """Enable or disable action buttons."""
        state = "normal" if enabled else "disabled"
        
        if hasattr(self, '_data_converter_btn'):
            self._data_converter_btn.configure(state=state)
        if hasattr(self, '_intercalation_btn'):
            self._intercalation_btn.configure(state=state)
        if hasattr(self, '_show_init_data_btn'):
            self._show_init_data_btn.configure(state=state)

    def set_application_settings(self, settings: dict[str, Any]) -> None:
        """Set application settings in the UI."""
        # TODO: Implement application settings UI
        pass

    def show_about_dialog(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Carbon Honeycomb Manager\nVersion 3.0\nA tool for building honeycomb carbon models"
        )

    def set_ui(self) -> None:
        """Set up the UI (required by IGeneralView)."""
        self._setup_ui()

    # Event handlers
    def _on_project_selected(self, project: str) -> None:
        """Handle project selection."""
        if "project" in self._selection_callbacks:
            self._selection_callbacks["project"](project)

    def _on_subproject_selected(self, subproject: str) -> None:
        """Handle subproject selection."""
        if "subproject" in self._selection_callbacks:
            self._selection_callbacks["subproject"](subproject)

    def _on_structure_selected(self, structure: str) -> None:
        """Handle structure selection."""
        if "structure" in self._selection_callbacks:
            self._selection_callbacks["structure"](structure)

    def _on_data_converter_clicked(self) -> None:
        """Handle data converter button click."""
        if "data_converter" in self._action_callbacks:
            self._action_callbacks["data_converter"]()

    def _on_intercalation_clicked(self) -> None:
        """Handle intercalation button click."""
        if "intercalation_and_sorption" in self._action_callbacks:
            self._action_callbacks["intercalation_and_sorption"]()

    def _on_show_init_data_clicked(self) -> None:
        """Handle show init data button click."""
        if "show_init_data" in self._action_callbacks:
            self._action_callbacks["show_init_data"]()