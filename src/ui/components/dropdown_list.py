import customtkinter as ctk
from typing import Callable


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
        kwargs["fg_color"] = "white"
        kwargs["text_color"] = "black"

        super().__init__(master, values=options, command=command, **kwargs)

        if title:
            self.title: ctk.CTkLabel = ctk.CTkLabel(master, text=title)
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
