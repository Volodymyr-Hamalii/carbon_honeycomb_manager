from abc import ABC, abstractmethod
from typing import Any, Callable
import customtkinter as ctk
import pandas as pd

from src.interfaces.ui.components import (
    IInputField,
    IInputFieldCoordLimits,
    ICheckBox,
    IDropdownList,
    IButton,
    ITable,
)


class IWindowGeneralTemplate(ABC):
    window: ctk.CTkToplevel

    @abstractmethod
    def create_window(
            self,
            title: str,
            description: str,
            geometry: tuple[int, int] | None,
    ) -> None:
        ...

    @abstractmethod
    def pack_input_field(
            self,
            parent: Any,
            text: str,
            command: Callable,
            default_value: Any,
            pady: int | tuple[int, int],
            padx: int | tuple[int, int],
    ) -> IInputField:
        ...

    @abstractmethod
    def pack_input_field_coord_limits(
            self,
            parent: Any,
            text: str,
            command: Callable,
            default_min: float,
            default_max: float,
            pady: int | tuple[int, int],
            padx: int | tuple[int, int],
    ) -> IInputFieldCoordLimits:
        ...

    @abstractmethod
    def pack_check_box(
            self,
            parent: Any,
            text: str,
            command: Callable,
            default: bool,
            pady: int | tuple[int, int],
            padx: int | tuple[int, int],
    ) -> ICheckBox:
        ...

    @abstractmethod
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
    ) -> IDropdownList:
        ...

    @abstractmethod
    def pack_button(
            self,
            parent: Any,
            text: str,
            command: Callable,
            pady: int | tuple[int, int],
            padx: int | tuple[int, int],
    ) -> IButton:
        ...

    @abstractmethod
    def pack_table(
            self,
            parent: Any,
            df: pd.DataFrame,
            title: str = "",
            to_show_index: bool = True,
    ) -> ITable:
        ...
