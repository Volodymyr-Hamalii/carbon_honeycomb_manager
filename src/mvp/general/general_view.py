import customtkinter as ctk
from tkinter import messagebox

from src.interfaces import IGeneralView, IGeneralPresenter
from src.services import Logger


class GeneralView(ctk.CTk, IGeneralView):
    """General view with default logic."""
    
    def __init__(self) -> None:
        super().__init__()
        self.presenter: IGeneralPresenter | None = None
        self.logger = Logger(self.__class__.__name__)
        
        # Common UI elements
        self._status_label: ctk.CTkLabel | None = None
        self._setup_common_ui()
    
    def _setup_common_ui(self) -> None:
        """Set up common UI elements."""
        # Status bar at bottom
        self._status_label = ctk.CTkLabel(self, text="Ready")
        self._status_label.pack(side="bottom", fill="x", padx=10, pady=5)
    
    def set_presenter(self, presenter: IGeneralPresenter) -> None:
        """Set the presenter for this view."""
        self.presenter = presenter
    
    def show_status_message(self, message: str) -> None:
        """Show status message to user."""
        if self._status_label:
            self._status_label.configure(text=message)
        self.logger.info(f"Status: {message}")
    
    def show_error_message(self, message: str) -> None:
        """Show error message to user."""
        messagebox.showerror("Error", message)
        self.logger.error(message)
    
    def show_success_message(self, message: str) -> None:
        """Show success message to user."""
        messagebox.showinfo("Success", message)
        self.logger.info(message)
    
    def show_warning_message(self, message: str) -> None:
        """Show warning message to user."""
        messagebox.showwarning("Warning", message)
        self.logger.warning(message)
    
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
