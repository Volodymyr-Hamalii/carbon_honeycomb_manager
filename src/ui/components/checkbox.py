import customtkinter as ctk
from typing import Callable


class CheckBox(ctk.CTkCheckBox):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            text: str,
            command: Callable | None = None,
            default: bool = False,
            **kwargs,
    ) -> None:
        self.var = ctk.BooleanVar(value=default)
        super().__init__(master, text=text, command=command, variable=self.var, **kwargs)

    def set_command(self, command: Callable) -> None:
        """Add listener to the checkbox."""
        self.configure(command=command)
