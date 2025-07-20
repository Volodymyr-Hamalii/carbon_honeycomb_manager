import customtkinter as ctk
from tkinter import messagebox

from src.interfaces import IGeneralView, IGeneralPresenter
from src.services import Logger
from src.ui.components import StatusLabel, StatusType


class GeneralView(ctk.CTk, IGeneralView):
    """General view with default logic."""
    
    def __init__(self) -> None:
        super().__init__()
        self.presenter: IGeneralPresenter | None = None
        self.logger = Logger(self.__class__.__name__)
        
        # Common UI elements
        self.status_label: StatusLabel | None = None
        self._setup_common_ui()
    
    def _setup_common_ui(self) -> None:
        """Set up common UI elements."""
        # Status bar at bottom
        self.status_label = StatusLabel(self)
        self.status_label.pack(side="bottom", fill="x")
    
    def set_presenter(self, presenter: IGeneralPresenter) -> None:
        """Set the presenter for this view."""
        self.presenter = presenter
    
    def show_status_message(self, message: str) -> None:
        """Show status message to user."""
        if self.status_label:
            self.status_label.set_info(message)
        self.logger.info(f"Status: {message}")
    
    def show_error_message(self, message: str) -> None:
        """Show error message to user."""
        if self.status_label:
            self.status_label.set_error(message)
        messagebox.showerror("Error", message)
        self.logger.error(message)
    
    def show_success_message(self, message: str) -> None:
        """Show success message to user."""
        if self.status_label:
            self.status_label.set_success(message)
        messagebox.showinfo("Success", message)
        self.logger.info(message)
    
    def show_warning_message(self, message: str) -> None:
        """Show warning message to user."""
        if self.status_label:
            self.status_label.set_warning(message)
        messagebox.showwarning("Warning", message)
        self.logger.warning(message)
    
    def show_processing_message(self, message: str) -> None:
        """Show processing message to user."""
        if self.status_label:
            self.status_label.set_processing(message)
        self.logger.info(f"Processing: {message}")
    
    def confirm_action(self, message: str, title: str = "Confirm") -> bool:
        """Show confirmation dialog."""
        return messagebox.askyesno(title, message)
    
    def enable_controls(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        # Override in subclasses to implement specific control logic
        pass
    
    def reset_form(self) -> None:
        """Reset the form to default values."""
        # Override in subclasses to implement specific reset logic
        pass
    
    def set_ui(self) -> None:
        """Set up the UI (required by IGeneralView)."""
        # Override in subclasses to implement specific UI setup
        pass
