import customtkinter as ctk
from typing import Callable

from src.interfaces.ui.templates import ICoordinateLimitsTemplate
from src.ui.components import InputFieldCoordLimits
from src.ui.styles import get_component_style, ComponentStyle, get_color_safe


class CoordinateLimitsTemplate(ctk.CTkFrame, ICoordinateLimitsTemplate):
    """Template for coordinate limits with horizontal layout."""

    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            title: str = "Plot coordinate limits",
            change_callback: Callable[[str, str], None] | None = None,
            **kwargs,
    ) -> None:
        # Apply default styles
        style: ComponentStyle = get_component_style("input_field")
        
        # Initialize the frame
        frame_config = {
            "fg_color": "transparent",
        }
        final_frame_config = {**frame_config, **kwargs}
        
        super().__init__(master, **final_frame_config)

        self.change_callback: Callable[[str, str], None] | None = change_callback
        self.coordinate_limits: dict[str, InputFieldCoordLimits] = {}

        # Create title
        title_style: ComponentStyle = get_component_style("label")
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            text_color=get_color_safe("label", "text_color"),
            font=(title_style.font.get("family", "Arial"), title_style.font.get("size", 14), "bold")
        )
        self.title_label.pack(pady=(0, 5))

        # Create horizontal container for coordinate limits
        coords_container = ctk.CTkFrame(self, fg_color="transparent")
        coords_container.pack(fill="x", pady=(0, 5))

        # Create X, Y, Z coordinate inputs in horizontal layout
        axes: list[str] = ["x", "y", "z"]
        for i, axis in enumerate(axes):
            # Create frame for this axis
            axis_frame = ctk.CTkFrame(coords_container, fg_color="transparent")
            axis_frame.pack(side="left", expand=True, padx=(0 if i == 0 else 2, 2 if i < len(axes)-1 else 0))

            # Create axis label
            axis_label = ctk.CTkLabel(
                axis_frame,
                text=f"{axis.upper()}:",
                text_color=get_color_safe("label", "text_color"),
                font=(style.font.get("family", "Arial"), style.font.get("size", 10), "bold"),
                width=20
            )
            axis_label.pack(side="left", padx=(0, 2))

            # Create coordinate limit input with reduced width
            coord_input = InputFieldCoordLimits(
                axis_frame,
                text="",  # No text since we have the axis label
                change_callback=self._on_coordinate_change if change_callback else None,
                width=120  # Make input field width twice shorter
            )
            
            # Remove the internal label from the coord_input (we have our own axis label)
            if hasattr(coord_input, 'label'):
                coord_input.label.destroy()
            
            coord_input.pack(side="right", padx=2, pady=2)
            self.coordinate_limits[axis] = coord_input

    def _on_coordinate_change(self, min_val: str, max_val: str) -> None:
        """Handle coordinate change from any axis input."""
        if self.change_callback:
            # We need to identify which axis changed and call callback appropriately
            # This will be handled by the individual axis callbacks set by parent
            pass

    def set_coordinate_limits(self, limits: dict[str, float]) -> None:
        """Set coordinate limits in the UI."""
        for axis in ["x", "y", "z"]:
            if axis in self.coordinate_limits:
                min_key = f"{axis}_min"
                max_key = f"{axis}_max"
                if min_key in limits:
                    self.coordinate_limits[axis].set_min_value(limits[min_key])
                if max_key in limits:
                    self.coordinate_limits[axis].set_max_value(limits[max_key])

    def get_coordinate_limits(self) -> dict[str, float]:
        """Get coordinate limits from the UI."""
        limits = {}
        for axis, field in self.coordinate_limits.items():
            # Handle min value
            min_val: str = field.get_min_value().strip()
            if min_val == "":
                limits[f"{axis}_min"] = -float("inf")
            else:
                try:
                    limits[f"{axis}_min"] = float(min_val)
                except ValueError:
                    limits[f"{axis}_min"] = -float("inf")
            
            # Handle max value
            max_val: str = field.get_max_value().strip()
            if max_val == "":
                limits[f"{axis}_max"] = float("inf")
            else:
                try:
                    limits[f"{axis}_max"] = float(max_val)
                except ValueError:
                    limits[f"{axis}_max"] = float("inf")
        return limits

    def set_change_callback(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for coordinate limit changes."""
        self.change_callback = callback
        
        # Set individual callbacks for each axis
        for axis, field in self.coordinate_limits.items():
            def create_axis_callback(axis_name: str):
                def axis_callback(min_val: str, max_val: str) -> None:
                    if self.change_callback:
                        # Call callback for min and max separately
                        self.change_callback(f"{axis_name}_min", min_val)
                        self.change_callback(f"{axis_name}_max", max_val)
                return axis_callback
            
            field.set_change_callback(create_axis_callback(axis))

    def destroy(self) -> None:
        """Destroy the coordinate limits template."""
        # Clean up individual input fields
        for field in self.coordinate_limits.values():
            field.destroy()
        super().destroy()