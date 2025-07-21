import customtkinter as ctk
from typing import Callable

from src.ui.styles import get_component_style, ComponentStyle, get_color_safe, get_dimension_safe


class Button(ctk.CTkButton):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            text: str,
            command: Callable | None = None,
            state: str = "active",
            **kwargs,
    ) -> None:
        # Apply default styles
        style: ComponentStyle = get_component_style("button")

        # Merge default styles with user-provided kwargs
        default_config = {
            # "fg_color": get_color_safe("button", "fg_color"),
            "text_color": get_color_safe("button", "text_color"),
            # "hover_color": get_color_safe("button", "hover_color"),
            "height": get_dimension_safe("button", "height"),
            "font": (style.font.get("family", "Arial"), style.font.get("size", 10)),
        }

        # User kwargs override defaults
        final_config = {**default_config, **kwargs}

        super().__init__(master, text=text, command=command, **final_config)
        self.configure(state=state)

    def set_command(self, command: Callable) -> None:
        """Add listener to the button."""
        self.configure(command=command)
