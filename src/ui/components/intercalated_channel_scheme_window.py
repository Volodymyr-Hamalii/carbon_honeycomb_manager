"""Tk window for the two-panel intercalated-channel scheme."""

from typing import Any

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # type: ignore
from matplotlib.figure import Figure

from src.entities import IntercalatedChannelSchemeData
from src.services.structure_visualizer import IntercalatedChannelSchemeRenderer
from src.ui.styles import SPACING


class IntercalatedChannelSchemeWindow(ctk.CTkToplevel):
    """Display an intercalated-channel scheme with the standard toolbar."""

    def __init__(
        self,
        master: Any,
        data: IntercalatedChannelSchemeData,
        title: str = "2D Intercalated Channel Scheme",
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.geometry("1600x900")
        self.figure: Figure = IntercalatedChannelSchemeRenderer().render(data)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Embed the rendered figure and Matplotlib navigation toolbar."""
        main_frame: ctk.CTkFrame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=SPACING.sm, pady=SPACING.sm)
        toolbar_frame: ctk.CTkFrame = ctk.CTkFrame(main_frame)
        toolbar_frame.pack(fill="x", pady=(0, SPACING.sm))
        self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(self.figure, main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar: NavigationToolbar2Tk = NavigationToolbar2Tk(
            self.canvas, toolbar_frame
        )
        self.toolbar.update()
        self.canvas.draw()
