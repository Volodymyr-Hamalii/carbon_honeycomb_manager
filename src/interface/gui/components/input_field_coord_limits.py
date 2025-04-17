import customtkinter as ctk
from typing import Callable


class InputFieldCoordLimits(ctk.CTkFrame):
    def __init__(
            self,
            master,
            text: str,
            command: Callable,
            state: str = "normal",
            default_min: str | int | float | None = None,
            default_max: str | int | float | None = None,
            **kwargs,
    ) -> None:
        # Initialize the parent class
        super().__init__(master, **kwargs)

        # Store the command for later use
        self.command = command

        # Create a frame to hold the entries and button
        self.pack(fill="x", padx=10, pady=10)

        # Create and pack the label above the frame
        self.label = ctk.CTkLabel(self, text=f"{text}:")
        self.label.pack(side="top", fill="x")

        # Initialize the CTkEntry for min value within the frame
        self.min_entry = ctk.CTkEntry(self, **kwargs)
        self.min_entry.configure(state=state)
        if default_min is not None and default_min != -float("inf"):
            self.min_entry.insert(0, default_min)
        self.min_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Initialize the CTkEntry for max value within the frame
        self.max_entry = ctk.CTkEntry(self, **kwargs)
        self.max_entry.configure(state=state)
        if default_max is not None and default_max != float("inf"):
            self.max_entry.insert(0, default_max)
        self.max_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Create and pack a single "Apply" button to the right of the entries
        self.apply_button = ctk.CTkButton(self, text="Apply", command=self.command)
        self.apply_button.pack(side="left", padx=10, pady=5)
