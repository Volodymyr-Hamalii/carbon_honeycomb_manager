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

        # Create callback to sync changes back to MVP params
        def on_plot_params_changed(updated_plot_params: PlotParams) -> None:
            # logger.info(f"Syncing plot params back to MVP: x_min={updated_plot_params.x_min}, "
            #            f"x_max={updated_plot_params.x_max}, bonds_min_dist={updated_plot_params.num_of_min_distances}")
            cls.sync_plot_params_to_mvp(updated_plot_params, mvp_params)
            # logger.info(f"MVP params after sync: x_min={mvp_params.x_min}, x_max={mvp_params.x_max}, "
            #            f"bonds_min_dist={mvp_params.bonds_num_of_min_distances}")

        plot_window: PlotWindow = PlotWindow(
            master=master,
            title=title,
            plot_params=plot_params,
            on_params_changed_callback=on_plot_params_changed,
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
        # Check if there are any saved plot params in the MVP params
        plot_params = PlotParams(
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
            to_set_equal_scale=getattr(mvp_params, 'to_set_equal_scale', True),
            is_interactive_mode=getattr(mvp_params, 'is_interactive_mode', False),
            to_build_edge_vertical_lines=getattr(mvp_params, 'to_build_edge_vertical_lines', False),
            to_show_grid=getattr(mvp_params, 'to_show_grid', True),
            to_show_legend=getattr(mvp_params, 'to_show_legend', True),
            num_of_inter_atoms_layers=getattr(mvp_params, 'num_of_inter_atoms_layers', 2),
        )
        return plot_params

    @staticmethod
    def sync_plot_params_to_mvp(plot_params: PlotParams, mvp_params: PMvpParams) -> PMvpParams:
        """Sync plot parameters back to MVP parameters for state persistence."""
        # Update MVP params with current plot settings
        mvp_params.to_build_bonds = plot_params.to_build_bonds
        mvp_params.to_show_coordinates = plot_params.to_show_coordinates
        mvp_params.to_show_c_indexes = plot_params.to_show_indexes
        mvp_params.bonds_num_of_min_distances = plot_params.num_of_min_distances
        mvp_params.bonds_skip_first_distances = plot_params.skip_first_distances
        mvp_params.x_min = plot_params.x_min
        mvp_params.x_max = plot_params.x_max
        mvp_params.y_min = plot_params.y_min
        mvp_params.y_max = plot_params.y_max
        mvp_params.z_min = plot_params.z_min
        mvp_params.z_max = plot_params.z_max

        # Update additional plot-specific settings if they exist in MVP params
        if hasattr(mvp_params, 'to_set_equal_scale'):
            mvp_params.to_set_equal_scale = plot_params.to_set_equal_scale
        if hasattr(mvp_params, 'is_interactive_mode'):
            mvp_params.is_interactive_mode = plot_params.is_interactive_mode
        if hasattr(mvp_params, 'to_build_edge_vertical_lines'):
            mvp_params.to_build_edge_vertical_lines = plot_params.to_build_edge_vertical_lines
        if hasattr(mvp_params, 'to_show_grid'):
            mvp_params.to_show_grid = plot_params.to_show_grid
        if hasattr(mvp_params, 'to_show_legend'):
            mvp_params.to_show_legend = plot_params.to_show_legend
        if hasattr(mvp_params, 'num_of_inter_atoms_layers'):
            mvp_params.num_of_inter_atoms_layers = plot_params.num_of_inter_atoms_layers

        return mvp_params

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
        plot_params.num_of_inter_atoms_layers = getattr(mvp_params, 'num_of_inter_atoms_layers', 2)

        return plot_params
