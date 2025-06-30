import numpy as np
from numpy.typing import NDArray

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import FigureManagerBase
from matplotlib.collections import PathCollection

# from src.coordinate_operations import DistanceMeasure
from src.interfaces import IVisualizationParams, PCoordinateLimits, IStructureVisualizer
from .lines_builder import LinesBuilder
from .visualization_params import VisualizationParams, StructureVisualParams
from ..utils import Logger


logger = Logger("StructureVisualizer")


class StructureVisualizer(IStructureVisualizer):
    @classmethod
    def show_structure(
            cls,
            coordinates: NDArray[np.float64],
            visual_params: IVisualizationParams,
            to_build_bonds: bool = True,
            to_set_equal_scale: bool | None = None,
            to_show_coordinates: bool | None = None,
            to_show_indexes: bool | None = None,
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
            title: str | None = None,
            is_interactive_mode: bool = False,
            coordinate_limits: PCoordinateLimits | None = None,
    ) -> None:
        """ Show 3D plot with 1 structure. """

        # Prepare to visualize
        fig: Figure = plt.figure()
        ax: Axes = fig.add_subplot(111, projection='3d')

        cls._plot_atoms_3d(
            fig=fig,
            ax=ax,
            coordinates=coordinates,
            visual_params=visual_params,
            to_build_bonds=to_build_bonds,
            to_set_equal_scale=to_set_equal_scale,
            to_show_coordinates=to_show_coordinates,
            to_show_indexes=to_show_indexes,
            num_of_min_distances=num_of_min_distances,
            skip_first_distances=skip_first_distances,
            is_interactive_mode=is_interactive_mode,
            coordinate_limits=coordinate_limits,
        )

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')  # type: ignore

        if title is not None:
            ax.set_title(title)

            # Set the plot window name
            current_fig_manager: FigureManagerBase | None = plt.get_current_fig_manager()
            if current_fig_manager:
                current_fig_manager.set_window_title(title)

        plt.show()

    @classmethod
    def show_two_structures(
            cls,
            coordinates_first: NDArray[np.float64],
            coordinates_second: NDArray[np.float64],
            visual_params_first: IVisualizationParams,
            visual_params_second: IVisualizationParams,
            coordinate_limits_first: PCoordinateLimits | None = None,
            coordinate_limits_second: PCoordinateLimits | None = None,
            to_show_indexes_first: bool | None = None,
            to_show_indexes_second: bool | None = None,
            to_build_bonds: bool = False,
            to_show_coordinates: bool | None = None,
            title: str | None = None,
            is_interactive_mode: bool = False,
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
    ) -> None:
        """ Show 3D plot with 2 structures (by default there are carbon and aluminium) """

        # Prepare to visualize
        fig: Figure = plt.figure()
        ax: Axes = fig.add_subplot(111, projection='3d')

        # Plot first structure atoms (not interactive)
        cls._plot_atoms_3d(
            fig=fig,
            ax=ax,
            coordinates=coordinates_first,
            visual_params=visual_params_first,
            to_build_bonds=to_build_bonds,
            num_of_min_distances=num_of_min_distances,
            skip_first_distances=skip_first_distances,
            to_show_coordinates=to_show_coordinates,
            to_show_indexes=to_show_indexes_first,
            is_interactive_mode=False,
            coordinate_limits=coordinate_limits_first,
        )

        # Plot second structure atoms (interactive if enabled)
        cls._plot_atoms_3d(
            fig=fig,
            ax=ax,
            coordinates=coordinates_second,
            visual_params=visual_params_second,
            to_build_bonds=False,
            num_of_min_distances=1,
            skip_first_distances=0,
            to_show_coordinates=to_show_coordinates,
            to_show_indexes=to_show_indexes_second,
            is_interactive_mode=is_interactive_mode,
            coordinate_limits=coordinate_limits_second,
        )

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')  # type: ignore
        ax.legend(
            # fontsize=16,
            labelspacing=1.1,
        )

        if title is not None:
            ax.set_title(title)

            # Set the plot window name
            current_fig_manager: FigureManagerBase | None = plt.get_current_fig_manager()
            if current_fig_manager:
                current_fig_manager.set_window_title(title)

        plt.show()

    @classmethod
    def show_structures(
            cls,
            coordinates_list: list[NDArray[np.float64]],
            visual_params_list: list[IVisualizationParams],
            to_build_bonds_list: list[bool],
            to_show_indexes_list: list[bool] | None = None,
            title: str | None = None,
            to_show_coordinates: bool | None = None,
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
            is_interactive_mode: bool = False,
            custom_indices_list: list[list[int] | None] | None = None,
            coordinate_limits_list: list[PCoordinateLimits] | None = None,
    ) -> None:
        """ Show 3D plot with multiple structures """

        if len(coordinates_list) != len(visual_params_list) != len(to_build_bonds_list):
            raise ValueError("len(coordinates_list) != len(visual_params_list) != len(to_build_bonds_list)")

        if custom_indices_list and len(custom_indices_list) != len(coordinates_list):
            raise ValueError("len(custom_indices_list) != len(coordinates_list)")

        if coordinate_limits_list and len(coordinate_limits_list) != len(coordinates_list):
            raise ValueError("len(coordinate_limits_list) != len(coordinates_list)")

        # Prepare to visualize
        fig: Figure = plt.figure()
        ax: Axes = fig.add_subplot(111, projection='3d')

        all_params = zip(
            coordinates_list,
            visual_params_list,
            to_build_bonds_list,
        )

        for i, (coordinates, visual_params, to_build_bonds) in enumerate(all_params):
            custom_indices = custom_indices_list[i] if custom_indices_list else []

            if coordinate_limits_list:
                coordinate_limits: PCoordinateLimits | None = coordinate_limits_list[i]
            else:
                coordinate_limits = None

            # if i == 1:
            #     num_of_min_distances=3
            # elif i == 2:
            #     num_of_min_distances=3

            cls._plot_atoms_3d(
                fig=fig,
                ax=ax,
                coordinates=coordinates,
                visual_params=visual_params,
                to_build_bonds=to_build_bonds,
                num_of_min_distances=num_of_min_distances,
                skip_first_distances=skip_first_distances,
                to_show_coordinates=to_show_coordinates,
                to_show_indexes=to_show_indexes_list[i] if to_show_indexes_list else None,
                is_interactive_mode=is_interactive_mode if visual_params.label != "Carbon" else False,
                custom_indexes=custom_indices if custom_indices else [],
                coordinate_limits=coordinate_limits,
            )

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')  # type: ignore
        ax.legend(
            # fontsize=12,
            labelspacing=1.1
        )

        if title is not None:
            ax.set_title(title)

            # Set the plot window name
            current_fig_manager: FigureManagerBase | None = plt.get_current_fig_manager()
            if current_fig_manager:
                current_fig_manager.set_window_title(title)

        plt.show()

    @staticmethod
    def get_2d_plot(
        coordinates: NDArray[np.float64],
        visual_params: IVisualizationParams,
        title: str | None = None,
        to_show_coordinates: bool | None = None,
        to_show_indexes: bool | None = None,
    ) -> Axes:
        # Prepare to visualize in 2D
        fig: Figure = plt.figure()
        ax: Axes = fig.add_subplot(111)  # No 3D projection here, just 2D

        # Plot points
        x: np.ndarray = coordinates[:, 0]
        y: np.ndarray = coordinates[:, 1]
        ax.scatter(
            x, y,
            color=visual_params.color_atoms,
            label='Points',
            alpha=visual_params.transparency,
        )

        if to_show_coordinates:
            # Show coordinates near each point
            for xx, yy in zip(x, y):
                ax.annotate(
                    f"({xx:.2f}, {yy:.2f})",
                    (xx, yy),
                    textcoords="offset points",
                    xytext=(5, 5),  # Offset from the point
                    fontsize=6,
                )

        if to_show_indexes:
            # Show coordinates near each point
            for xx, yy, i in zip(x, y, range(len(coordinates))):
                ax.annotate(
                    str(i),
                    (xx, yy),
                    textcoords="offset points",
                    xytext=(5, 5),  # Offset from the point
                    fontsize=6,
                )

        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        if title is not None:
            ax.set_title(title)

            # Set the plot window name
            current_fig_manager: FigureManagerBase | None = plt.get_current_fig_manager()
            if current_fig_manager:
                current_fig_manager.set_window_title(title)

        # ax.legend()
        plt.grid(True)

        return ax

    @classmethod
    def show_2d_graph(
        cls,
        coordinates: NDArray[np.float64],
        visual_params: IVisualizationParams,
        title: str | None = None,
        to_show_coordinates: bool | None = None,
        to_show_indexes: bool | None = None,
    ) -> None:
        cls.get_2d_plot(
            coordinates=coordinates,
            visual_params=visual_params,
            title=title,
            to_show_coordinates=to_show_coordinates,
            to_show_indexes=to_show_indexes,
        )
        plt.show()

    @classmethod
    def _plot_atoms_3d(
            cls,
            fig: Figure,
            ax: Axes,
            coordinates: NDArray[np.float64],
            visual_params: IVisualizationParams,
            to_set_equal_scale: bool | None = None,
            to_build_bonds: bool = True,
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
            to_show_coordinates: bool | None = None,
            to_show_indexes: bool | None = None,
            is_interactive_mode: bool = False,
            custom_indexes: list[int] = [],
            coordinate_limits: PCoordinateLimits | None = None,
    ) -> PathCollection | None:
        if coordinates.size == 0:
            logger.warning(f"No points to plot for {visual_params.label}.")
            return

        if coordinate_limits:
            # Remove points outside the coordinate limits
            coordinates = coordinates[
                (coordinates[:, 0] >= coordinate_limits.x_min) &
                (coordinates[:, 0] <= coordinate_limits.x_max) &
                (coordinates[:, 1] >= coordinate_limits.y_min) &
                (coordinates[:, 1] <= coordinate_limits.y_max) &
                (coordinates[:, 2] >= coordinate_limits.z_min) &
                (coordinates[:, 2] <= coordinate_limits.z_max)
            ]

        x: NDArray[np.float64] = coordinates[:, 0]
        y: NDArray[np.float64] = coordinates[:, 1]
        z: NDArray[np.float64] = coordinates[:, 2]

        # if coordinate_limits:
        #     x = np.clip(x, coordinate_limits.x_min, coordinate_limits.x_max)
        #     y = np.clip(y, coordinate_limits.y_min, coordinate_limits.y_max)
        #     z = np.clip(z, coordinate_limits.z_min, coordinate_limits.z_max)

        scatter: PathCollection = ax.scatter(
            x, y, z,
            c=visual_params.color_atoms,
            label=visual_params.label,
            s=visual_params.size,  # type: ignore
            alpha=visual_params.transparency,
            picker=True if is_interactive_mode else False,
        )

        if to_set_equal_scale is None:
            to_set_equal_scale = visual_params.to_set_equal_scale

        if to_set_equal_scale:
            cls._set_equal_scale(ax, x, y, z)

        if to_show_coordinates is True or (to_show_coordinates is None and visual_params.to_show_coordinates):
            # Show coordinates near each point
            for xx, yy, zz in zip(x, y, z):
                ax.text(
                    xx, yy, zz,
                    f"({xx:.2f}, {yy:.2f}, {zz:.2f})",  # type: ignore
                    fontsize=6,
                    color="black",
                    ha="center",
                    va="center",
                )

        if to_show_indexes or (to_show_indexes is None and visual_params.to_show_indexes):
            # Show coordinates near each point
            if len(custom_indexes) > 0:
                for i, (xx, yy, zz) in enumerate(coordinates):
                    ax.text(
                        xx, yy, zz,
                        str(custom_indexes[i]),  # type: ignore
                        fontsize=10,
                        color="black",
                        ha="center",
                        va="center",
                    )
            else:
                for i, (xx, yy, zz) in enumerate(coordinates):
                    ax.text(
                        xx, yy, zz,
                        str(i),  # type: ignore
                        fontsize=10,
                        color="black",
                        ha="center",
                        va="center",
                    )

        if to_build_bonds:
            # Carbon
            LinesBuilder.add_lines(
                coordinates=coordinates, ax=ax,
                visual_params=visual_params,
                num_of_min_distances=num_of_min_distances,
                skip_first_distances=skip_first_distances)

        if is_interactive_mode:
            def on_pick(event) -> None:
                try:
                    ind: int = event.ind[0]
                except Exception:
                    return

                while True:
                    try:
                        result: str = input(
                            f"Update coordinates for point with coordinates={coordinates[ind]}? (y/n): ")
                        if result == "y":
                            break
                        else:
                            return
                    except Exception:
                        return

                new_x = float(input(f"Enter new X ({coordinates[ind][0]:.2f}): ") or coordinates[ind][0])
                new_y = float(input(f"Enter new Y ({coordinates[ind][1]:.2f}): ") or coordinates[ind][1])
                new_z = float(input(f"Enter new Z ({coordinates[ind][2]:.2f}): ") or coordinates[ind][2])

                upd_point: list[float] = [new_x, new_y, new_z]

                coordinates[ind] = upd_point
                scatter._offsets3d = (coordinates[:, 0], coordinates[:, 1], coordinates[:, 2])  # type: ignore
                plt.draw()

                logger.info(f"Updated point coordinates: {coordinates[ind]}")

                # min_dists: np.ndarray = DistanceMeasure.calculate_min_distances(coordinates, np.array([upd_point]))
                # min_dist: float = np.min(min_dists[min_dists > 0])
                # logger.info(f"Distance to the nearest atom: {min_dist}")

            fig.canvas.mpl_connect('pick_event', on_pick)

        return scatter

    @staticmethod
    def _set_equal_scale(
            ax: Axes,
            x_coor: NDArray[np.float64],
            y_coor: NDArray[np.float64],
            z_coor: NDArray[np.float64],
    ) -> None:
        """Set equal scaling for all axis."""

        x_min, x_max = x_coor.min(), x_coor.max()
        y_min, y_max = y_coor.min(), y_coor.max()
        z_min, z_max = z_coor.min(), z_coor.max()

        min_lim = np.min([x_min, y_min, z_min])
        max_lim = np.max([x_max, y_max, z_max])

        delta = (max_lim - min_lim) / 2
        delta_minus = delta * 0.8

        x_mid = (x_max + x_min) / 2
        y_mid = (y_max + y_min) / 2
        z_mid = (z_max + z_min) / 2

        ax.set_xlim(x_mid - delta, x_mid + delta)
        ax.set_ylim(y_mid - delta, y_mid + delta)

        try:
            ax.set_zlim(z_mid - delta_minus, z_mid + delta_minus)  # type: ignore
        except Exception:
            pass
