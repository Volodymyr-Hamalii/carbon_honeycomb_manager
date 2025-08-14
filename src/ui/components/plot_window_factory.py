"""Factory for creating plot windows from MVP parameters."""

import customtkinter as ctk
import numpy as np
from numpy.typing import NDArray

from src.interfaces import (
    PMvpParams,
    IStructureVisualParams,
    IShowInitDataView,
    IIntercalationAndSorptionView,
)
from src.entities.params.plot_params import PlotParams
from .plot import PlotWindow
from src.services.utils.logger import Logger


logger = Logger("PlotWindowFactory")


class PlotWindowFactory:
    """Factory for creating plot windows with MVP parameter integration."""

    @classmethod
    def create_plot_window_from_mvp_params(
        cls,
        master: ctk.CTk | ctk.CTkToplevel | IShowInitDataView | IIntercalationAndSorptionView,
        mvp_params: PMvpParams,
        title: str = "Structure Plot",
        **kwargs
    ) -> PlotWindow:
        """Create a plot window with parameters converted from MVP params."""
        plot_params: PlotParams = cls._convert_mvp_to_plot_params(mvp_params, title)

        plot_window = PlotWindow(
            master=master,
            title=title,
            plot_params=plot_params,
            **kwargs
        )

        return plot_window

    @classmethod
    def show_structure_in_new_window(
        cls,
        master: ctk.CTk | ctk.CTkToplevel | IShowInitDataView | IIntercalationAndSorptionView,
        coordinates: NDArray[np.float64],
        structure_visual_params: IStructureVisualParams,
        mvp_params: PMvpParams,
        title: str = "Structure Visualization",
        label: str | None = None,
    ) -> PlotWindow:
        """Show a single structure in a new plot window."""
        plot_window: PlotWindow = cls.create_plot_window_from_mvp_params(
            master=master,
            mvp_params=mvp_params,
            title=title,
        )

        plot_window.show_structure(
            coordinates=coordinates,
            structure_visual_params=structure_visual_params,
            label=label,
        )

        return plot_window

    @classmethod
    def show_two_structures_in_new_window(
        cls,
        master: ctk.CTk | ctk.CTkToplevel | IShowInitDataView | IIntercalationAndSorptionView,
        coordinates_first: NDArray[np.float64],
        coordinates_second: NDArray[np.float64],
        structure_visual_params_first: IStructureVisualParams,
        structure_visual_params_second: IStructureVisualParams,
        mvp_params: PMvpParams,
        title: str = "Structure Comparison",
        label_first: str | None = None,
        label_second: str | None = None,
    ) -> PlotWindow:
        """Show two structures in a new plot window."""
        plot_window: PlotWindow = cls.create_plot_window_from_mvp_params(
            master=master,
            mvp_params=mvp_params,
            title=title,
        )

        plot_window.show_two_structures(
            coordinates_first=coordinates_first,
            coordinates_second=coordinates_second,
            structure_visual_params_first=structure_visual_params_first,
            structure_visual_params_second=structure_visual_params_second,
            label_first=label_first,
            label_second=label_second,
        )

        return plot_window

    @classmethod
    def show_structures_in_new_window(
        cls,
        master: ctk.CTk | ctk.CTkToplevel | IShowInitDataView | IIntercalationAndSorptionView,
        coordinates_list: list[NDArray[np.float64]],
        structure_visual_params_list: list[IStructureVisualParams],
        labels_list: list[str | None],
        mvp_params: PMvpParams,
        title: str = "Multiple Structures",
    ) -> PlotWindow:
        """Show multiple structures in a new plot window."""
        plot_window: PlotWindow = cls.create_plot_window_from_mvp_params(
            master=master,
            mvp_params=mvp_params,
            title=title,
        )

        plot_window.show_structures(
            coordinates_list=coordinates_list,
            structure_visual_params_list=structure_visual_params_list,
            labels_list=labels_list,
        )

        return plot_window

    @staticmethod
    def _convert_mvp_to_plot_params(mvp_params: PMvpParams, title: str) -> PlotParams:
        """Convert MVP parameters to plot parameters."""
        return PlotParams(
            to_build_bonds=mvp_params.to_build_bonds,
            to_show_coordinates=mvp_params.to_show_coordinates,
            to_show_indexes=mvp_params.to_show_c_indexes,  # Use carbon indexes as default
            num_of_min_distances=mvp_params.bonds_num_of_min_distances,
            skip_first_distances=mvp_params.bonds_skip_first_distances,
            x_min=mvp_params.x_min,
            x_max=mvp_params.x_max,
            y_min=mvp_params.y_min,
            y_max=mvp_params.y_max,
            z_min=mvp_params.z_min,
            z_max=mvp_params.z_max,
            title=title,
            to_set_equal_scale=True,  # Default to true for structure visualization
            is_interactive_mode=False,  # Default to false for safety
            to_build_edge_vertical_lines=False,  # Default to false
        )

    @staticmethod
    def update_plot_params_from_mvp(plot_params: PlotParams, mvp_params: PMvpParams) -> PlotParams:
        """Update existing plot parameters with values from MVP parameters."""
        plot_params.to_build_bonds = mvp_params.to_build_bonds
        plot_params.to_show_coordinates = mvp_params.to_show_coordinates
        plot_params.to_show_indexes = mvp_params.to_show_c_indexes
        plot_params.num_of_min_distances = mvp_params.bonds_num_of_min_distances
        plot_params.skip_first_distances = mvp_params.bonds_skip_first_distances
        plot_params.x_min = mvp_params.x_min
        plot_params.x_max = mvp_params.x_max
        plot_params.y_min = mvp_params.y_min
        plot_params.y_max = mvp_params.y_max
        plot_params.z_min = mvp_params.z_min
        plot_params.z_max = mvp_params.z_max

        return plot_params
