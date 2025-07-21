import customtkinter as ctk
from typing import Callable

from src.ui.styles import get_component_style, ComponentStyle, get_color_safe


class CheckBox(ctk.CTkCheckBox):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            text: str,
            command: Callable | None = None,
            default: bool = False,
            **kwargs,
    ) -> None:
        # Apply default styles
        style: ComponentStyle = get_component_style("label")
        
        # Merge default styles with user-provided kwargs
        default_config = {
            "text_color": get_color_safe("label", "text_color"),
            "font": (style.font.get("family", "Arial"), style.font.get("size", 10)),
        }
        
        # User kwargs override defaults
        final_config = {**default_config, **kwargs}
        
        self.var = ctk.BooleanVar(value=default)
        super().__init__(master, text=text, command=command, variable=self.var, **final_config)

    def set_command(self, command: Callable) -> None:
        """Add listener to the checkbox."""
        self.configure(command=command)

    def set_value(self, value: bool) -> None:
        self.var.set(value)

    def get_value(self) -> bool:
        return self.var.get()
