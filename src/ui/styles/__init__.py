"""UI styles package."""

from .colors import COLORS, get_current_theme_colors, STATUS_COLORS
from .spacing import SPACING, PADDING, FONT_SIZES, DIMENSIONS
from .styles import STYLES, get_component_style, ComponentStyle, get_color_safe, get_dimension_safe

__all__: list[str] = [
    "COLORS",
    "STATUS_COLORS",
    "SPACING",
    "PADDING",
    "FONT_SIZES",
    "DIMENSIONS",
    "STYLES",
    "ComponentStyle",
    "get_current_theme_colors",
    "get_component_style",
    "get_color_safe",
    "get_dimension_safe",
]
