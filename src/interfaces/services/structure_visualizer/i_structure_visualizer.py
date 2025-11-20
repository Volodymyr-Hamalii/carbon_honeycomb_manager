import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection

from src.interfaces.entities.params import PCoordinateLimits
from .i_visualization_params import IVisualizationParams


class IStructureVisualizer(ABC):
    @classmethod
    @abstractmethod
    def show_structure(
            cls,
            coordinates: NDArray[np.float64],
            to_build_bonds: bool,
            to_set_equal_scale: bool | None,
            to_show_coordinates: bool | None,
            to_show_indexes: bool | None,
            visual_params: IVisualizationParams,
            num_of_min_distances: int,
            skip_first_distances: int,
            title: str | None,
            is_interactive_mode: bool,
            coordinate_limits: PCoordinateLimits | None,
    ) -> None:
        ...

    @classmethod
    @abstractmethod
    def show_structures(
            cls,
            coordinates_list: list[NDArray[np.float64]],
            visual_params_list: list[IVisualizationParams],
            to_build_bonds_list: list[bool],
            to_show_indexes_list: list[bool] | None,
            title: str | None,
            to_show_coordinates: bool | None,
            num_of_min_distances: int,
            skip_first_distances: int,
            is_interactive_mode: bool,
            custom_indices_list: list[list[int] | None] | None,
            coordinate_limits_list: list[PCoordinateLimits] | None,
    ) -> None:
        ...

    @staticmethod
    @abstractmethod
    def get_2d_plot(
            coordinates: NDArray[np.float64],
            title: str | None,
            visual_params: IVisualizationParams,
            to_show_coordinates: bool | None,
            to_show_indexes: bool | None,
    ) -> Axes:
        ...

    @classmethod
    @abstractmethod
    def show_2d_graph(
            cls,
            coordinates: NDArray[np.float64],
            title: str | None,
            visual_params: IVisualizationParams,
            to_show_coordinates: bool | None,
            to_show_indexes: bool | None,
    ) -> None:
        ...

    @classmethod
    @abstractmethod
    def _plot_atoms_3d(
            cls,
            fig: Figure,
            ax: Axes,
            coordinates: NDArray[np.float64],
            visual_params: IVisualizationParams,
            to_set_equal_scale: bool | None,
            to_build_bonds: bool,
            num_of_min_distances: int,
            skip_first_distances: int,
            to_show_coordinates: bool | None,
            to_show_indexes: bool | None,
            is_interactive_mode: bool,
            custom_indexes: list[int],
            coordinate_limits: PCoordinateLimits | None,
            plot_as_polygon_balls: bool | None = None,
    ) -> PathCollection | None:
        ...

    @staticmethod
    @abstractmethod
    def _set_equal_scale(
            ax: Axes,
            x_coor: NDArray[np.float64],
            y_coor: NDArray[np.float64],
            z_coor: NDArray[np.float64],
    ) -> None:
        ...
