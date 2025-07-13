import customtkinter as ctk
from typing import Callable


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
        # Initialize the CTkEntry within the frame
        super().__init__(master, **kwargs)

        # Create a frame to hold the entries and button
        self.pack(fill="x", padx=10, pady=10)

        # Create and pack the label above the frame
        self.label = ctk.CTkLabel(self, text=text)
        self.label.pack(side="top", fill="x")

        # Initialize the CTkEntry for min value within the frame
        self.entry = ctk.CTkEntry(self, **kwargs)
        self.entry.configure(state=state)

        if default_value is not None:
            self.entry.insert(0, default_value)

        self.entry.pack(side="left", fill="x", expand=True, padx=5)

        # Create and pack a single "Apply" button to the right of the entries
        self.apply_button = ctk.CTkButton(self, text="Apply")
        self.apply_button.pack(side="right", padx=10, pady=5)

        if command:
            self.set_command(command)

    def set_command(self, command: Callable) -> None:
        """Add listener to the input field."""
        self.apply_button.configure(command=command)

    def set_value(self, value: str | int | float) -> None:
        self.entry.insert(0, value)

    def get_value(self) -> str | int | float:
        return self.entry.get()
