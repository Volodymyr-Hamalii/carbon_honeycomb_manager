import customtkinter as ctk
from typing import Callable

from src.ui.styles import get_component_style, ComponentStyle, get_color_safe


class DropdownList(ctk.CTkOptionMenu):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            options: list[str],
            command: Callable | None = None,
            title: str = "",
            is_disabled: bool = False,
            title_pady: int | tuple[int, int] = 0,
            **kwargs,
    ) -> None:
        # Apply default styles
        style: ComponentStyle = get_component_style("input_field")

        # Merge default styles with user-provided kwargs
        default_config = {
            "fg_color": style.colors.get("fg_color", "white"),
            "text_color": style.colors.get("text_color", "black"),
            "font": (style.font.get("family", "Arial"), style.font.get("size", 10)),
        }

        # User kwargs override defaults
        final_config = {**default_config, **kwargs}

        super().__init__(master, values=options, command=command, **final_config)

        if title:
            label_style: ComponentStyle = get_component_style("label")
            self.title: ctk.CTkLabel = ctk.CTkLabel(
                master,
                text=title,
                text_color=get_color_safe("label", "text_color"),
                font=(label_style.font.get("family", "Arial"), label_style.font.get("size", 10))
            )
            self.title.pack(pady=title_pady, padx=10)

        if is_disabled:
            self.configure(state=ctk.DISABLED)

    def set_options(self, options: list[str], default_value: str | None = None) -> None:
        self.configure(values=options)
        if default_value:
            self.set(default_value)

    def set_command(self, command: Callable) -> None:
        """Add listener to the dropdown list."""
        self.configure(command=command)
