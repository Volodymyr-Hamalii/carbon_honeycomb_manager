from typing import Any, Callable
import customtkinter as ctk
import pandas as pd

from src.utils import Logger
from ..components import (
    InputField,
    CheckBox,
    DropdownList,
    Button,
    InputFieldCoordLimits,
    Table,
)

logger = Logger("WindowsTemplate")


class WindowsTemplate:
    window: ctk.CTkToplevel

    def create_window(
            self,
            title: str,
            description: str = "",
            geometry: tuple[int, int] | None = None,
    ) -> None:
        self.window = ctk.CTkToplevel()
        self.window.pack_propagate(True)
        self.window.grid_propagate(True)

        if geometry:
            self.window.geometry(f"{geometry[0]}x{geometry[1]}")

        self.window.title(title)

        if description:
            description_label: ctk.CTkLabel = ctk.CTkLabel(
                self.window, text=description, wraplength=500
            )
            description_label.pack(pady=10, padx=10)

    def pack_label(
            self,
            parent: Any,
            text: str,
            pady: int | tuple[int, int] = 10,
            padx: int | tuple[int, int] = 10,
    ) -> ctk.CTkLabel:
        label: ctk.CTkLabel = ctk.CTkLabel(
            parent,
            text=text,
        )
        label.pack(pady=pady, padx=padx)
        return label

    def pack_input_field(
            self,
            parent: Any,
            text: str,
            command: Callable,
            default_value: Any,
            pady: int | tuple[int, int] = 10,
            padx: int | tuple[int, int] = 10,
    ) -> InputField:
        input_field: InputField = InputField(
            parent,
            text=text,
            command=command,
            default_value=default_value,
        )
        input_field.pack(pady=pady, padx=padx)
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
            command: Callable,
            default: bool,
            pady: int | tuple[int, int] = 10,
            padx: int | tuple[int, int] = 10,
    ) -> CheckBox:
        check_box: CheckBox = CheckBox(
            parent,
            text=text,
            command=command,
            default=default,
        )
        check_box.pack(pady=pady, padx=padx)
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
