import customtkinter as ctk
from typing import Callable, Any

from src.ui.styles import get_component_style, ComponentStyle, get_color_safe, get_dimension_safe


class InputField(ctk.CTkFrame):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            text: str,
            change_callback: Callable[[str], None] | None = None,
            state: str = "normal",
            default_value: str | int | float | None = None,
            auto_sync_interval: int = 200,  # milliseconds
            **kwargs,
    ) -> None:
        # Apply default styles
        style: ComponentStyle = get_component_style("input_field")
        
        # Initialize the CTkEntry within the frame
        frame_config = {
            # "bg_color": get_color_safe("input_field", "bg_color"),
            # "fg_color": get_color_safe("input_field", "fg_color"),
        }
        final_frame_config = {**frame_config, **kwargs}
        
        super().__init__(master, **final_frame_config)

        # Store callback and last known value for change detection
        self.change_callback: Callable[[str], None] | None = change_callback
        self.last_value: str = ""
        self.auto_sync_interval: int = auto_sync_interval
        self.auto_sync_job: str | None = None

        # Create a frame to hold the entry
        self.pack(
            fill="x", 
            padx=style.spacing.get("padx", 10), 
            pady=style.spacing.get("pady", 5)  # Reduced padding since no Apply button
        )

        # Create and pack the label above the frame
        label_style: ComponentStyle = get_component_style("label")
        self.label = ctk.CTkLabel(
            self, 
            text=text,
            text_color=get_color_safe("label", "text_color"),
            font=(label_style.font.get("family", "Arial"), label_style.font.get("size", 10))
        )
        self.label.pack(side="top", fill="x")

        # Initialize the CTkEntry within the frame
        entry_config = {
            # "fg_color": get_color_safe("input_field", "fg_color"),
            # "text_color": get_color_safe("input_field", "text_color"),
            # "border_color": get_color_safe("input_field", "border_color"),
            "height": get_dimension_safe("input_field", "height"),
            "font": (style.font.get("family", "Arial"), style.font.get("size", 10)),
        }
        self.entry = ctk.CTkEntry(self, **entry_config)
        self.entry.configure(state=state)

        if default_value is not None:
            self.entry.insert(0, str(default_value))
            self.last_value = str(default_value)

        self.entry.pack(
            fill="x", 
            expand=True, 
            padx=style.spacing.get("internal_padx", 5)
        )

        # Start auto-sync if callback is provided
        if self.change_callback:
            self._start_auto_sync()

    def set_change_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback function for value changes."""
        self.change_callback = callback
        if callback:
            self._start_auto_sync()
        else:
            self._stop_auto_sync()

    def _start_auto_sync(self) -> None:
        """Start periodic value checking and auto-sync."""
        if self.auto_sync_job:
            self.after_cancel(self.auto_sync_job)
        self._check_for_changes()

    def _stop_auto_sync(self) -> None:
        """Stop auto-sync timer."""
        if self.auto_sync_job:
            self.after_cancel(self.auto_sync_job)
            self.auto_sync_job = None

    def _check_for_changes(self) -> None:
        """Check if value has changed and call callback if it has."""
        try:
            current_value = self.entry.get()
            if current_value != self.last_value:
                self.last_value = current_value
                if self.change_callback:
                    self.change_callback(current_value)
        except Exception:
            # Ignore errors during value checking (e.g., if widget is destroyed)
            pass
        
        # Schedule next check
        if self.change_callback:
            self.auto_sync_job = self.after(self.auto_sync_interval, self._check_for_changes)

    def set_value(self, value: str | int | float) -> None:
        """Set the value of the input field."""
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        self.last_value = str(value)

    def get_value(self) -> str:
        """Get the current value from the input field."""
        return self.entry.get()

    def destroy(self) -> None:
        """Override destroy to clean up auto-sync timer."""
        self._stop_auto_sync()
        super().destroy()
