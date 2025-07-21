import customtkinter as ctk
from typing import Callable

from src.ui.styles import get_component_style, ComponentStyle, get_color_safe, get_dimension_safe


class InputField(ctk.CTkFrame):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            text: str,
            command: Callable | None = None,
            state: str = "normal",
            default_value: str | int | float | None = None,
            **kwargs,
    ) -> None:
        # Apply default styles
        style: ComponentStyle = get_component_style("input_field")
        
        # Initialize the CTkEntry within the frame
        frame_config = {
            "bg_color": get_color_safe("input_field", "bg_color"),
            "fg_color": get_color_safe("input_field", "fg_color"),
        }
        final_frame_config = {**frame_config, **kwargs}
        
        super().__init__(master, **final_frame_config)

        # Create a frame to hold the entries and button
        self.pack(
            fill="x", 
            padx=style.spacing.get("padx", 10), 
            pady=style.spacing.get("pady", 10)
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

        # Initialize the CTkEntry for min value within the frame
        entry_config = {
            "fg_color": get_color_safe("input_field", "fg_color"),
            "text_color": get_color_safe("input_field", "text_color"),
            "border_color": get_color_safe("input_field", "border_color"),
            "height": get_dimension_safe("input_field", "height"),
            "font": (style.font.get("family", "Arial"), style.font.get("size", 10)),
        }
        self.entry = ctk.CTkEntry(self, **entry_config)
        self.entry.configure(state=state)

        if default_value is not None:
            self.entry.insert(0, default_value)

        self.entry.pack(
            side="left", 
            fill="x", 
            expand=True, 
            padx=style.spacing.get("internal_padx", 5)
        )

        # Create and pack a single "Apply" button to the right of the entries
        button_style: ComponentStyle = get_component_style("button")
        self.apply_button = ctk.CTkButton(
            self, 
            text="Apply",
            fg_color=get_color_safe("button", "fg_color"),
            text_color=get_color_safe("button", "text_color"),
            hover_color=get_color_safe("button", "hover_color"),
            height=button_style.dimensions.get("height") or 0,
            font=(button_style.font.get("family", "Arial"), button_style.font.get("size", 10))
        )
        self.apply_button.pack(
            side="right", 
            padx=style.spacing.get("padx", 10), 
            pady=style.spacing.get("pady", 5)
        )

        if command:
            self.set_command(command)

    def set_command(self, command: Callable) -> None:
        """Add listener to the input field."""
        self.apply_button.configure(command=command)

    def set_value(self, value: str | int | float) -> None:
        self.entry.insert(0, value)

    def get_value(self) -> str | int | float:
        return self.entry.get()
