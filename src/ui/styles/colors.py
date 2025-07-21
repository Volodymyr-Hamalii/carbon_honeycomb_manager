"""Color definitions for the application."""

from dataclasses import dataclass
import customtkinter as ctk


@dataclass(frozen=True)
class StatusColors:
    """Status message colors."""
    info: str
    success: str
    warning: str
    error: str
    processing: str


@dataclass(frozen=True)
class ThemeColors:
    """Colors for a specific theme."""
    background: str
    surface: str
    header_background: str
    alternate_row: str
    text: str
    border: str
    primary: str
    secondary: str
    accent: str
    status: StatusColors


@dataclass(frozen=True)
class Colors:
    """Application color scheme."""
    light: ThemeColors
    dark: ThemeColors
    status: StatusColors


# Status colors (semantic colors that don't change with theme)
STATUS_COLORS = StatusColors(
    info="#1f538d",      # Blue
    success="#2d5a27",   # Green
    warning="#8b5a00",   # Orange
    error="#8b0000",     # Red
    processing="#4a4a4a" # Gray
)

# Color definitions
COLORS = Colors(
    light=ThemeColors(
        background="white",
        surface="#f8f9fa",
        header_background="lightgray",
        alternate_row="#f0f0f0",
        text="black",
        border="#e0e0e0",
        primary="#3B8ED0",  # CTkButton default blue
        secondary="#6c757d",
        accent="#36719F",   # CTkButton default hover blue
        status=STATUS_COLORS,
    ),
    dark=ThemeColors(
        background="#333333",
        surface="#2a2a2a",
        header_background="#444444",
        alternate_row="#3a3a3a",
        text="white",
        border="#555555",
        primary="#1F6AA5",  # CTkButton default blue (dark)
        secondary="#6c757d",
        accent="#144870",   # CTkButton default hover blue (dark)
        status=STATUS_COLORS,
    ),
    status=STATUS_COLORS
)


def get_current_theme_colors() -> ThemeColors:
    """Get colors for the current CustomTkinter theme."""
    current_theme: str = ctk.get_appearance_mode().lower()
    return COLORS.dark if current_theme == "dark" else COLORS.light
