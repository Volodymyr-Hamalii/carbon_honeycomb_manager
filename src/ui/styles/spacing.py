"""Spacing and sizing definitions for the application."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Spacing:
    """Standard spacing values."""
    xs: int = 2
    sm: int = 5
    md: int = 10
    lg: int = 15
    xl: int = 20
    xxl: int = 30


@dataclass(frozen=True)
class Padding:
    """Standard padding values."""
    xs: int = 2
    sm: int = 5
    md: int = 10
    lg: int = 15
    xl: int = 20


@dataclass(frozen=True)
class FontSizes:
    """Standard font sizes."""
    small: int = 10
    normal: int = 12
    medium: int = 14
    large: int = 16
    title: int = 18


@dataclass(frozen=True)
class Dimensions:
    """Standard dimensions for UI elements."""
    button_height: int = 32
    input_height: int = 32
    table_row_height: int = 25
    header_height: int = 40


# Global instances
SPACING = Spacing()
PADDING = Padding()
FONT_SIZES = FontSizes()
DIMENSIONS = Dimensions()
