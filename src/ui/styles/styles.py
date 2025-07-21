"""General styles configuration for UI components."""

from dataclasses import dataclass
from typing import Any

from .colors import ThemeColors
from .colors import get_current_theme_colors
from .spacing import SPACING, PADDING, FONT_SIZES, DIMENSIONS


@dataclass(frozen=True)
class ComponentStyle:
    """Style configuration for a UI component."""
    colors: dict[str, str]
    spacing: dict[str, int]
    font: dict[str, Any]
    dimensions: dict[str, int]


class Styles:
    """Central styles configuration."""

    def __init__(self) -> None:
        self._styles: dict[str, ComponentStyle] = {}
        self._init_default_styles()

    def _init_default_styles(self) -> None:
        """Initialize default styles for components."""
        colors: ThemeColors = get_current_theme_colors()

        # Button styles
        self._styles["button"] = ComponentStyle(
            colors={
                "fg_color": colors.primary,
                "text_color": colors.text,
                "hover_color": colors.accent,
            },
            spacing={
                "padx": PADDING.md,
                "pady": PADDING.sm,
            },
            font={
                "family": "Arial",
                "size": FONT_SIZES.normal,
            },
            dimensions={
                "height": DIMENSIONS.button_height,
            }
        )

        # Input field styles
        self._styles["input_field"] = ComponentStyle(
            colors={
                "bg_color": colors.background,
                "fg_color": colors.surface,
                "text_color": colors.text,
                "border_color": colors.border,
            },
            spacing={
                "padx": PADDING.md,
                "pady": PADDING.md,
                "internal_padx": PADDING.sm,
            },
            font={
                "family": "Arial",
                "size": FONT_SIZES.normal,
            },
            dimensions={
                "height": DIMENSIONS.input_height,
            }
        )

        # Table styles
        self._styles["table"] = ComponentStyle(
            colors={
                "bg_color": colors.background,
                "header_bg_color": colors.header_background,
                "text_color": colors.text,
                "alt_row_color": colors.alternate_row,
                "border_color": colors.border,
            },
            spacing={
                "padx": SPACING.xs,
                "pady": SPACING.xs,
                "cell_padding": SPACING.sm,
            },
            font={
                "family": "Arial",
                "size": FONT_SIZES.small,
                "header_size": FONT_SIZES.normal,
            },
            dimensions={
                "row_height": DIMENSIONS.table_row_height,
                "header_height": DIMENSIONS.header_height,
            }
        )

        # Frame styles
        self._styles["frame"] = ComponentStyle(
            colors={
                "bg_color": colors.background,
                "fg_color": colors.surface,
                "border_color": colors.border,
            },
            spacing={
                "padx": PADDING.md,
                "pady": PADDING.md,
            },
            font={},
            dimensions={}
        )

        # Label styles
        self._styles["label"] = ComponentStyle(
            colors={
                "bg_color": colors.background,
                "text_color": colors.text,
            },
            spacing={
                "padx": PADDING.sm,
                "pady": PADDING.sm,
            },
            font={
                "family": "Arial",
                "size": FONT_SIZES.normal,
            },
            dimensions={}
        )

    def get_style(self, component_name: str) -> ComponentStyle:
        """Get style configuration for a component."""
        return self._styles.get(component_name, self._styles["frame"])
    
    def get_color_with_fallback(self, component_name: str, color_key: str) -> str:
        """Get a color value with theme-appropriate fallback."""
        style: ComponentStyle = self.get_style(component_name)
        colors: ThemeColors = get_current_theme_colors()
        
        # Define theme-appropriate fallbacks for different color types
        fallback_map = {
            "fg_color": colors.primary,
            "bg_color": colors.background,
            "text_color": colors.text,
            "hover_color": colors.accent,
            "border_color": colors.border,
            "header_bg_color": colors.header_background,
            "alt_row_color": colors.alternate_row,
        }
        
        fallback = fallback_map.get(color_key, colors.text)
        return style.colors.get(color_key, fallback)
    
    def get_dimension_with_fallback(self, component_name: str, dimension_key: str) -> int:
        """Get a dimension value with appropriate fallback."""
        style: ComponentStyle = self.get_style(component_name)
        
        # Define appropriate fallbacks for different dimension types
        fallback_map = {
            "height": DIMENSIONS.button_height,
            "width": 100,
            "row_height": DIMENSIONS.table_row_height,
            "header_height": DIMENSIONS.header_height,
        }
        
        fallback = fallback_map.get(dimension_key, DIMENSIONS.button_height)
        return style.dimensions.get(dimension_key, fallback)

    def update_component_style(self, component_name: str, style_updates: dict[str, Any]) -> None:
        """Update style configuration for a component."""
        if component_name not in self._styles:
            self._styles[component_name] = ComponentStyle({}, {}, {}, {})

        style: ComponentStyle = self._styles[component_name]

        if "colors" in style_updates:
            style.colors.update(style_updates["colors"])
        if "spacing" in style_updates:
            style.spacing.update(style_updates["spacing"])
        if "font" in style_updates:
            style.font.update(style_updates["font"])
        if "dimensions" in style_updates:
            style.dimensions.update(style_updates["dimensions"])


# Global styles instance
STYLES = Styles()


def get_component_style(component_name: str) -> ComponentStyle:
    """Get style configuration for a component."""
    return STYLES.get_style(component_name)


def get_color_safe(component_name: str, color_key: str) -> str:
    """Get a color value with guaranteed non-None result."""
    return STYLES.get_color_with_fallback(component_name, color_key)


def get_dimension_safe(component_name: str, dimension_key: str) -> int:
    """Get a dimension value with guaranteed non-None result."""
    return STYLES.get_dimension_with_fallback(component_name, dimension_key)
