"""View for data converter functionality."""
import customtkinter as ctk
from typing import Any, Callable
from pathlib import Path

from src.interfaces import IDataConverterView
from src.mvp.general import GeneralView
from src.ui.components import Button, DropdownList, InputField
from src.services import Logger


logger = Logger("DataConverterView")


class DataConverterView(GeneralView, IDataConverterView):
    """View for data converter functionality."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Data Converter")
        self.geometry("500x400")

        # Context variables
        self.project_dir = ""
        self.subproject_dir = ""
        self.structure_dir = ""

        # UI components
        self.source_file_dropdown: DropdownList | None = None
        self.target_format_dropdown: DropdownList | None = None
        self.convert_btn: Button | None = None

        # Callbacks
        self.callbacks: dict[str, Callable] = {}

    def set_context(self, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        """Set the context for this view."""
        self.project_dir: str = project_dir
        self.subproject_dir: str = subproject_dir
        self.structure_dir: str = structure_dir
        self.title(f"Data Converter - {project_dir}/{subproject_dir}/{structure_dir}")

    def set_ui(self) -> None:
        """Set up the UI components."""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame, text="File Format Converter",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(0, 20))

        # Source file selection
        source_frame = ctk.CTkFrame(main_frame)
        source_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(source_frame, text="Source File:").pack(pady=5)
        self.source_file_dropdown = DropdownList(source_frame, ["Loading..."])
        self.source_file_dropdown.pack(pady=5)

        # Target format selection
        target_frame = ctk.CTkFrame(main_frame)
        target_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(target_frame, text="Target Format:").pack(pady=5)
        self.target_format_dropdown = DropdownList(target_frame, ["xlsx", "dat", "pdb"])
        self.target_format_dropdown.pack(pady=5)

        # Convert button
        self.convert_btn = Button(
            main_frame,
            text="Convert File",
            command=self._on_convert_file,
        )
        self.convert_btn.pack(pady=20)

        # Status frame
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="x", pady=(10, 0))

        self.status_label = ctk.CTkLabel(status_frame, text="Ready to convert")
        self.status_label.pack(pady=10)

    def set_available_files(self, files: list[str]) -> None:
        """Set available files for conversion."""
        if self.source_file_dropdown:
            self.source_file_dropdown.configure(values=files)
            if files:
                self.source_file_dropdown.set(files[0])

    def get_selected_file(self) -> str:
        """Get selected source file."""
        if self.source_file_dropdown:
            return self.source_file_dropdown.get()
        return ""

    def get_target_format(self) -> str:
        """Get selected target format."""
        if self.target_format_dropdown:
            return self.target_format_dropdown.get()
        return ""

    def set_conversion_callbacks(self, callbacks: dict[str, Callable]) -> None:
        """Set callbacks for conversion operations."""
        self.callbacks = callbacks

    def set_conversion_callback(self, callback: Callable) -> None:
        """Set callback for conversion button."""
        self.callbacks["convert_file"] = callback

    def set_available_formats(self, formats: list[str]) -> None:
        """Set available formats in the UI."""
        if self.target_format_dropdown:
            self.target_format_dropdown.configure(values=formats)

    def get_conversion_parameters(self) -> dict[str, str]:
        """Get conversion parameters from UI."""
        return {
            "source_file": self.get_selected_file(),
            "target_format": self.get_target_format(),
            "project_dir": self.project_dir,
            "subproject_dir": self.subproject_dir,
            "structure_dir": self.structure_dir,
        }

    def show_conversion_progress(self, message: str) -> None:
        """Show conversion progress."""
        self.show_status_message(f"Converting: {message}")

    def show_conversion_success(self, output_path: Path) -> None:
        """Show conversion success."""
        self.show_success_message(f"File converted successfully: {output_path.name}")

    def show_conversion_error(self, error_message: str) -> None:
        """Show conversion error."""
        self.show_error_message(error_message)

    def enable_controls(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        state = "normal" if enabled else "disabled"
        if self.convert_btn:
            self.convert_btn.configure(state=state)

    def reset_form(self) -> None:
        """Reset the form to default values."""
        if self.target_format_dropdown:
            self.target_format_dropdown.set("xlsx")

    def _on_convert_file(self) -> None:
        """Handle convert file button click."""
        if "convert_file" in self.callbacks:
            self.callbacks["convert_file"]()

    def update_status(self, message: str) -> None:
        """Update status message."""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
