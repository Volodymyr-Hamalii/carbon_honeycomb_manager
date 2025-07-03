import customtkinter as ctk
from typing import Callable


class Button(ctk.CTkButton):
    def __init__(
            self,
            master: ctk.CTkFrame | ctk.CTk,
            text: str,
            command: Callable | None = None,
            state: str = "active",
            **kwargs,
    ) -> None:
        super().__init__(master, text=text, command=command, **kwargs)
        self.configure(state=state)

    def set_command(self, command: Callable) -> None:
        """Add listener to the button."""
        self.configure(command=command)
