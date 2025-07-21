import customtkinter as ctk
from typing import Callable

from src.ui.styles import get_component_style, ComponentStyle, get_color_safe, get_dimension_safe


class InputFieldCoordLimits(ctk.CTkFrame):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            text: str,
            change_callback: Callable[[str, str], None] | None = None,
            state: str = "normal",
            default_min: str | int | float | None = None,
            default_max: str | int | float | None = None,
            auto_sync_interval: int = 200,  # milliseconds
            **kwargs,
    ) -> None:
        # Apply default styles
        style: ComponentStyle = get_component_style("input_field")

        # Initialize the parent class
        frame_config = {
            "bg_color": get_color_safe("input_field", "bg_color"),
            "fg_color": get_color_safe("input_field", "fg_color"),
        }
        final_frame_config = {**frame_config, **kwargs}

        super().__init__(master, **final_frame_config)

        # Store callback and last known values for change detection
        self.change_callback: Callable[[str, str], None] | None = change_callback
        self.last_min_value: str = ""
        self.last_max_value: str = ""
        self.auto_sync_interval: int = auto_sync_interval
        self.auto_sync_job: str | None = None

        # Create a frame to hold the entries
        # Don't pack here - let parent handle packing to control width
        # self.pack(
        #     fill="x",
        #     padx=style.spacing.get("padx", 10),
        #     pady=style.spacing.get("pady", 5)  # Reduced padding since no Apply button
        # )

        # Create and pack the label above the frame
        label_style: ComponentStyle = get_component_style("label")
        self.label = ctk.CTkLabel(
            self,
            text=text,
            text_color=get_color_safe("label", "text_color"),
            font=(label_style.font.get("family", "Arial"), label_style.font.get("size", 10))
        )
        self.label.pack(side="top", fill="x")

        # Create a sub-frame for the min/max entries
        entries_frame = ctk.CTkFrame(self, fg_color="transparent")
        entries_frame.pack(fill="x", padx=style.spacing.get("internal_padx", 5))

        # Initialize the CTkEntry for min value
        entry_config = {
            "fg_color": get_color_safe("input_field", "fg_color"),
            "text_color": get_color_safe("input_field", "text_color"),
            "border_color": get_color_safe("input_field", "border_color"),
            "height": get_dimension_safe("input_field", "height"),
            "font": (style.font.get("family", "Arial"), style.font.get("size", 10)),
            "placeholder_text": "Min",
            "placeholder_text_color": "#999999"  # Grey placeholder
        }
        
        # Add width if specified in kwargs
        if "width" in kwargs:
            entry_width = kwargs["width"] // 2  # Divide by 2 since we have min and max entries
            entry_config["width"] = entry_width
        self.min_entry = ctk.CTkEntry(entries_frame, **entry_config)
        self.min_entry.configure(state=state)
        if default_min is not None and not self._is_infinity(default_min):
            self.min_entry.insert(0, str(default_min))
            self.last_min_value = str(default_min)
        elif default_min is not None:
            # Store infinity but don't display it
            self.last_min_value = ""
        self.min_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )

        # Initialize the CTkEntry for max value
        max_entry_config = entry_config.copy()
        max_entry_config["placeholder_text"] = "Max"
        max_entry_config["placeholder_text_color"] = "#999999"  # Grey placeholder
        self.max_entry = ctk.CTkEntry(entries_frame, **max_entry_config)
        self.max_entry.configure(state=state)
        if default_max is not None and not self._is_infinity(default_max):
            self.max_entry.insert(0, str(default_max))
            self.last_max_value = str(default_max)
        elif default_max is not None:
            # Store infinity but don't display it
            self.last_max_value = ""
        self.max_entry.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(5, 0)
        )

        # Start auto-sync if callback is provided
        if self.change_callback:
            self._start_auto_sync()

    def set_change_callback(self, callback: Callable[[str, str], None]) -> None:
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
        """Check if values have changed and call callback if they have."""
        try:
            current_min: str = self.min_entry.get()
            current_max: str = self.max_entry.get()
            
            if current_min != self.last_min_value or current_max != self.last_max_value:
                self.last_min_value = current_min
                self.last_max_value = current_max
                if self.change_callback:
                    self.change_callback(current_min, current_max)
        except Exception:
            # Ignore errors during value checking (e.g., if widget is destroyed)
            pass
        
        # Schedule next check
        if self.change_callback:
            self.auto_sync_job = self.after(self.auto_sync_interval, self._check_for_changes)

    def _is_infinity(self, value: str | int | float) -> bool:
        """Check if a value represents infinity."""
        if isinstance(value, (int, float)):
            return value == float('inf') or value == -float('inf')
        if isinstance(value, str):
            return value.lower() in ['inf', '-inf'] or str(value) in ['inf', '-inf']
        return False

    def set_min_value(self, value: str | int | float) -> None:
        """Set the minimum value."""
        self.min_entry.delete(0, "end")
        if not self._is_infinity(value):
            self.min_entry.insert(0, str(value))
            self.last_min_value = str(value)
        else:
            # Don't display infinity values, keep field empty
            self.last_min_value = ""

    def set_max_value(self, value: str | int | float) -> None:
        """Set the maximum value."""
        self.max_entry.delete(0, "end")
        if not self._is_infinity(value):
            self.max_entry.insert(0, str(value))
            self.last_max_value = str(value)
        else:
            # Don't display infinity values, keep field empty
            self.last_max_value = ""

    def get_min_value(self) -> str:
        """Get the current minimum value."""
        return self.min_entry.get()

    def get_max_value(self) -> str:
        """Get the current maximum value."""
        return self.max_entry.get()

    def destroy(self) -> None:
        """Override destroy to clean up auto-sync timer."""
        self._stop_auto_sync()
        super().destroy()
