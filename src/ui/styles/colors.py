"""Color definitions for the application."""

from dataclasses import dataclass
import customtkinter as ctk


class Colors:
    BLACK: str = "#000000"
    GRAY100: str = "#2a2a2a"
    GRAY200: str = "#333333"
    GRAY300: str = "#454545"
    GRAY400: str = "#6a6a6a"
    GRAY500: str = "#919191"
    GRAY600: str = "#afafaf"
    GRAY700: str = "#d4d4d4"
    WHITE: str = "#ffffff"

    BLUE100: str = "#00065f"
    BLUE200: str = "#0500a4"
    BLUE300: str = "#144870"
    BLUE400: str = "#1F6AA5"
    BLUE500: str = "#3B8ED0"

    RED100: str = "#500000"
    RED200: str = "#8b0000"
    RED300: str = "#e00000"
    RED400: str = "#ff4d4d"

    ORANGE: str = "#8b5a00"

    GREEN100: str = "#004309"
    GREEN200: str = "#2d5a27"
    GREEN300: str = "#00d11d"
    GREEN400: str = "#99ff99"


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
class ColorScheme:
    """Application color scheme."""
    light: ThemeColors
    dark: ThemeColors
    status: StatusColors


# Status colors (semantic colors that don't change with theme)
STATUS_COLORS = StatusColors(
    info=Colors.BLUE300,
    success=Colors.GREEN200,
    warning=Colors.ORANGE,
    error=Colors.RED200,
    processing=Colors.GRAY300,
)

# Color definitions
COLOR_SCHEME = ColorScheme(
    light=ThemeColors(
        background=Colors.WHITE,
        surface=Colors.GRAY700,
        header_background=Colors.GRAY600,
        alternate_row=Colors.GRAY700,
        text=Colors.BLACK,
        border=Colors.GRAY700,
        primary=Colors.BLUE500,
        secondary=Colors.GRAY400,
        accent=Colors.BLUE400,
        status=STATUS_COLORS,
    ),
    dark=ThemeColors(
        background=Colors.GRAY200,
        surface=Colors.GRAY100,
        header_background=Colors.GRAY300,
        alternate_row=Colors.GRAY200,
        text=Colors.WHITE,
        border=Colors.GRAY300,
        primary=Colors.BLUE400,
        secondary=Colors.GRAY400,
        accent=Colors.BLUE300,
        status=STATUS_COLORS,
    ),
    status=STATUS_COLORS
)


def get_current_theme_colors() -> ThemeColors:
    """Get colors for the current CustomTkinter theme."""
    current_theme: str = ctk.get_appearance_mode().lower()
    return COLOR_SCHEME.dark if current_theme == "dark" else COLOR_SCHEME.light
