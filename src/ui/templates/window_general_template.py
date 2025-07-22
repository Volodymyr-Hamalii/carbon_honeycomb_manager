from typing import Any, Callable, Optional
import customtkinter as ctk
import pandas as pd

from src.services import Logger
from src.ui.components import (
    InputField,
    CheckBox,
    DropdownList,
    Button,
    InputFieldCoordLimits,
    Table,
)
# CoordinateLimitsTemplate will be imported locally to avoid circular import

logger = Logger("WindowGeneralTemplate")


class WindowGeneralTemplate:
    """Template for creating consistent UI layouts across MVP views."""
    
    def __init__(self) -> None:
        self.main_frame: Optional[ctk.CTkScrollableFrame] = None
        self.window: Optional[ctk.CTk | ctk.CTkToplevel] = None

    def create_main_layout(
            self,
            parent: ctk.CTk | ctk.CTkToplevel,
            title: str = "",
            geometry: tuple[int, int] | None = None,
            padx: int = 10,
            pady: int = 10,
    ) -> ctk.CTkScrollableFrame:
        """Create the main scrollable layout for MVP views."""
        self.window = parent
        
        if geometry and hasattr(parent, 'geometry'):
            parent.geometry(f"{geometry[0]}x{geometry[1]}")
        
        if title and hasattr(parent, 'title'):
            parent.title(title)
            
        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(parent)
        self.main_frame.pack(fill="both", expand=True, padx=padx, pady=pady)
        
        return self.main_frame

    def create_section_frame(
            self,
            parent: ctk.CTkFrame | ctk.CTkScrollableFrame,
            title: str,
            pady: tuple[int, int] = (0, 10),
            font_size: int = 16,
            font_weight: str = "bold"
    ) -> ctk.CTkFrame:
        """Create a titled section frame."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=pady)
        
        if title:
            title_label = ctk.CTkLabel(
                section_frame, 
                text=title,
                font=ctk.CTkFont(size=font_size, weight=font_weight)
            )
            title_label.pack(pady=5)
        
        return section_frame

    def create_columns_layout(
            self,
            parent: ctk.CTkFrame,
            column_count: int = 2,
            spacing: int = 5
    ) -> list[ctk.CTkFrame]:
        """Create a multi-column layout within a frame."""
        columns_container = ctk.CTkFrame(parent, fg_color="transparent")
        columns_container.pack(fill="x", padx=10, pady=5)
        
        columns = []
        for i in range(column_count):
            column = ctk.CTkFrame(columns_container)
            
            # Pack columns side by side
            if i == 0:
                column.pack(side="left", fill="both", expand=True, padx=(0, spacing))
            elif i == column_count - 1:
                column.pack(side="right", fill="both", expand=True, padx=(spacing, 0))
            else:
                column.pack(side="left", fill="both", expand=True, padx=spacing)
                
            columns.append(column)
        
        return columns

    def create_coordinate_limits_section(
            self,
            parent: ctk.CTkFrame | ctk.CTkScrollableFrame,
            title: str = "Plot coordinate limits",
            change_callback: Callable[[str, str], None] | None = None,
            pady: tuple[int, int] = (0, 10)
    ) -> Any:
        """Create a coordinate limits section."""
        # Import locally to avoid circular import
        from src.ui.templates.coordinate_limits_template import CoordinateLimitsTemplate
        
        coord_limits = CoordinateLimitsTemplate(
            parent,
            title=title,
            change_callback=change_callback
        )
        coord_limits.pack(fill="x", pady=pady)
        return coord_limits

    def pack_label(
            self,
            parent: Any,
            text: str,
            pady: int | tuple[int, int] = 10,
            padx: int | tuple[int, int] = 10,
            font: Any = None,
    ) -> ctk.CTkLabel:
        """Pack a label with optional custom font."""
        label_config = {"text": text}
        if font:
            label_config["font"] = font
            
        label: ctk.CTkLabel = ctk.CTkLabel(parent, **label_config)
        label.pack(pady=pady, padx=padx)
        return label

    def pack_input_field(
            self,
            parent: Any,
            text: str,
            change_callback: Callable[[str], None] | None = None,
            default_value: Any = "",
            pady: int | tuple[int, int] = 2,
            padx: int | tuple[int, int] = 0,
            fill: str = "x",
    ) -> InputField:
        """Pack an input field with auto-sync support."""
        input_field: InputField = InputField(
            parent,
            text=text,
            change_callback=change_callback,
            default_value=default_value,
        )
        input_field.pack(pady=pady, padx=padx, fill=fill)
        return input_field

    def pack_input_field_coord_limits(
            self,
            parent: Any,
            text: str,
            command: Callable,
            default_min: float,
            default_max: float,
            pady: int | tuple[int, int] = 10,
            padx: int | tuple[int, int] = 10,
    ) -> InputFieldCoordLimits:
        input_field_coord_limits: InputFieldCoordLimits = InputFieldCoordLimits(
            parent,
            text=text,
            command=command,
            default_min=default_min,
            default_max=default_max,
        )
        input_field_coord_limits.pack(pady=pady, padx=padx)
        return input_field_coord_limits

    def pack_check_box(
            self,
            parent: Any,
            text: str,
            command: Callable | None = None,
            default: bool = False,
            pady: int | tuple[int, int] = 1,
            padx: int | tuple[int, int] = 0,
            anchor: str = "w",
    ) -> CheckBox:
        """Pack a checkbox with consistent styling."""
        check_box: CheckBox = CheckBox(
            parent,
            text=text,
            command=command,
            default=default,
        )
        check_box.pack(pady=pady, padx=padx, anchor=anchor)
        return check_box

    def pack_dropdown_list(
            self,
            parent: Any,
            command: Callable,
            options: list[str],
            title: str = "",
            is_disabled: bool = False,
            pady: int | tuple[int, int] = 0,
            padx: int | tuple[int, int] = 0,
            title_pady: int | tuple[int, int] = (10, 0),
    ) -> DropdownList:
        dropdown_list: DropdownList = DropdownList(
            parent,
            title=title,
            command=command,
            options=options,
            is_disabled=is_disabled,
            title_pady=title_pady,
        )

        dropdown_list.pack(
            pady=pady,
            padx=padx,
        )
        return dropdown_list

    def pack_button(
            self,
            parent: Any,
            text: str,
            command: Callable,
            pady: int | tuple[int, int] = 10,
            padx: int | tuple[int, int] = 10,
    ) -> Button:
        button: Button = Button(
            parent,
            text=text,
            command=command,
        )
        button.pack(pady=pady, padx=padx)
        return button

    def pack_table(
            self,
            parent: Any,
            df: pd.DataFrame,
            title: str = "",
            to_show_index: bool = True,
    ) -> Table:
        table: Table = Table(df, master=parent, title=title, to_show_index=to_show_index)
        table.pack(fill="both", expand=True)
        return table
