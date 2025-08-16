import numpy as np
from numpy.typing import NDArray

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import FigureManagerBase
from matplotlib.collections import PathCollection

from src.interfaces import (
    PCoordinateLimits,
    IStructureVisualizer,
    IStructureVisualParams,
)
from .lines_builder import LinesBuilder
from ..utils import Logger


logger = Logger("StructureVisualizer")


class StructureVisualizer(IStructureVisualizer):
    @classmethod
    def show_structure(
            cls,
            coordinates: NDArray[np.float64],
            structure_visual_params: IStructureVisualParams,
            label: str | None = None,
            to_build_bonds: bool = True,
            to_set_equal_scale: bool | None = None,
            to_show_coordinates: bool | None = None,
            to_show_indexes: bool | None = None,
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
            title: str | None = None,
            is_interactive_mode: bool = False,
            coordinate_limits: PCoordinateLimits | None = None,
            bonds_to_highlight: PCoordinateLimits | None = None,
            to_build_edge_vertical_lines: bool = False,
    ) -> None:
        """ Show 3D plot with 1 structure. """

        # Prepare to visualize
        fig: Figure = plt.figure()
        ax: Axes = fig.add_subplot(111, projection='3d')

        cls._plot_atoms_3d(
            fig=fig,
            ax=ax,
            coordinates=coordinates,
            structure_visual_params=structure_visual_params,
            label=label,
            to_build_bonds=to_build_bonds,
            to_set_equal_scale=to_set_equal_scale,
            to_show_coordinates=to_show_coordinates,
            to_show_indexes=to_show_indexes,
            num_of_min_distances=num_of_min_distances,
            skip_first_distances=skip_first_distances,
            is_interactive_mode=is_interactive_mode,
            coordinate_limits=coordinate_limits,
            bonds_to_highlight=bonds_to_highlight,
            to_build_edge_vertical_lines=to_build_edge_vertical_lines,
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
            structure_visual_params_first: IStructureVisualParams,
            structure_visual_params_second: IStructureVisualParams,
            coordinate_limits_first: PCoordinateLimits | None = None,
            coordinate_limits_second: PCoordinateLimits | None = None,
            label_first: str | None = None,
            label_second: str | None = None,
            to_show_indexes_first: bool | None = None,
            to_show_indexes_second: bool | None = None,
            to_build_bonds: bool = False,
            to_show_coordinates: bool | None = None,
            title: str | None = None,
            is_interactive_mode: bool = False,
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
            bonds_to_highlight: PCoordinateLimits | None = None,
            to_build_edge_vertical_lines: bool = False,
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
            structure_visual_params=structure_visual_params_first,
            label=label_first,
            to_build_bonds=to_build_bonds,
            num_of_min_distances=num_of_min_distances,
            skip_first_distances=skip_first_distances,
            to_show_coordinates=to_show_coordinates,
            to_show_indexes=to_show_indexes_first,
            is_interactive_mode=False,
            coordinate_limits=coordinate_limits_first,
            bonds_to_highlight=bonds_to_highlight,
            to_build_edge_vertical_lines=to_build_edge_vertical_lines,
        )

        # Plot second structure atoms (interactive if enabled)
        cls._plot_atoms_3d(
            fig=fig,
            ax=ax,
            coordinates=coordinates_second,
            structure_visual_params=structure_visual_params_second,
            label=label_second,
            to_build_bonds=False,
            num_of_min_distances=1,
            skip_first_distances=0,
            to_show_coordinates=to_show_coordinates,
            to_show_indexes=to_show_indexes_second,
            is_interactive_mode=is_interactive_mode,
            coordinate_limits=coordinate_limits_second,
            bonds_to_highlight=bonds_to_highlight,
            to_build_edge_vertical_lines=to_build_edge_vertical_lines,
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
            structure_visual_params_list: list[IStructureVisualParams],
            labels_list: list[str | None],
            to_build_bonds_list: list[bool],
            to_show_indexes_list: list[bool] | None = None,
            title: str | None = None,
            to_show_coordinates: bool | None = None,
            to_show_grid: bool | None = None,  # TODO
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
            is_interactive_mode: bool = False,
            custom_indices_list: list[list[int] | None] | None = None,
            coordinate_limits_list: list[PCoordinateLimits] | None = None,
            bonds_to_highlight: PCoordinateLimits | None = None,
            to_build_edge_vertical_lines: bool = False,
    ) -> None:
        """ Show 3D plot with multiple structures """

        if len(coordinates_list) != len(structure_visual_params_list) != len(
                to_build_bonds_list) != len(labels_list):
            raise ValueError("len(coordinates_list) != len(structure_visual_params_list) \
                             != len(to_build_bonds_list) != len(labels_list)")

        if custom_indices_list and len(custom_indices_list) != len(coordinates_list):
            raise ValueError("len(custom_indices_list) != len(coordinates_list)")

        if coordinate_limits_list and len(coordinate_limits_list) != len(coordinates_list):
            raise ValueError("len(coordinate_limits_list) != len(coordinates_list)")

        # Prepare to visualize
        fig: Figure = plt.figure()
        ax: Axes = fig.add_subplot(111, projection='3d')

        all_params = zip(
            coordinates_list,
            structure_visual_params_list,
            to_build_bonds_list,
            labels_list,
        )

        for i, (coordinates, structure_visual_params, to_build_bonds, label) in enumerate(all_params):
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
                structure_visual_params=structure_visual_params,
                label=label,
                to_build_bonds=to_build_bonds,
                num_of_min_distances=num_of_min_distances,
                skip_first_distances=skip_first_distances,
                to_show_coordinates=to_show_coordinates,
                to_show_indexes=to_show_indexes_list[i] if to_show_indexes_list else None,
                is_interactive_mode=is_interactive_mode if label != "Carbon" else False,
                custom_indexes=custom_indices if custom_indices else [],
                coordinate_limits=coordinate_limits,
                bonds_to_highlight=bonds_to_highlight,
                to_build_edge_vertical_lines=to_build_edge_vertical_lines,
                to_show_grid=to_show_grid,
            )

        if to_show_grid is not False:
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
        structure_visual_params: IStructureVisualParams,
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
            color=structure_visual_params.color_atoms,
            label='Points',
            alpha=structure_visual_params.transparency,
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
        structure_visual_params: IStructureVisualParams,
        title: str | None = None,
        to_show_coordinates: bool | None = None,
        to_show_indexes: bool | None = None,
    ) -> None:
        cls.get_2d_plot(
            coordinates=coordinates,
            structure_visual_params=structure_visual_params,
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
            structure_visual_params: IStructureVisualParams,
            label: str | None,
            to_set_equal_scale: bool | None = None,
            to_build_bonds: bool = True,
            num_of_min_distances: int = 2,
            skip_first_distances: int = 0,
            to_show_coordinates: bool | None = None,
            to_show_indexes: bool | None = None,
            to_show_grid: bool | None = None,  # TODO
            is_interactive_mode: bool = False,
            custom_indexes: list[int] = [],
            coordinate_limits: PCoordinateLimits | None = None,
            bonds_to_highlight: PCoordinateLimits | None = None,
            to_build_edge_vertical_lines: bool = False,
            to_show_dists_to_plane: bool = False,
            to_show_dists_to_edges: bool = False,
            to_show_channel_angles: bool = False,
            to_show_plane_lengths: bool = False,
    ) -> PathCollection | None:
        if coordinates.size == 0:
            logger.warning(f"No points to plot for label={label}.")
            return

        if coordinate_limits:
            logger.info(f"Filtering coordinates with limits: "
                        f"x=[{coordinate_limits.x_min}, {coordinate_limits.x_max}], "
                        f"y=[{coordinate_limits.y_min}, {coordinate_limits.y_max}], "
                        f"z=[{coordinate_limits.z_min}, {coordinate_limits.z_max}]")

            original_count = len(coordinates)

            # Check for finite limits only
            has_finite_limits = (
                not (coordinate_limits.x_min == -float('inf') and coordinate_limits.x_max == float('inf')) or
                not (coordinate_limits.y_min == -float('inf') and coordinate_limits.y_max == float('inf')) or
                not (coordinate_limits.z_min == -float('inf') and coordinate_limits.z_max == float('inf'))
            )

            if has_finite_limits:
                # Remove points outside the coordinate limits
                coordinates = coordinates[
                    (coordinates[:, 0] >= coordinate_limits.x_min) &
                    (coordinates[:, 0] <= coordinate_limits.x_max) &
                    (coordinates[:, 1] >= coordinate_limits.y_min) &
                    (coordinates[:, 1] <= coordinate_limits.y_max) &
                    (coordinates[:, 2] >= coordinate_limits.z_min) &
                    (coordinates[:, 2] <= coordinate_limits.z_max)
                ]

                filtered_count = len(coordinates)
                logger.info(f"Coordinate filtering: {original_count} -> {filtered_count} atoms")
            else:
                logger.info("All coordinate limits are infinite, skipping filtering")

        x: NDArray[np.float64] = coordinates[:, 0]
        y: NDArray[np.float64] = coordinates[:, 1]
        z: NDArray[np.float64] = coordinates[:, 2]

        # if coordinate_limits:
        #     x = np.clip(x, coordinate_limits.x_min, coordinate_limits.x_max)
        #     y = np.clip(y, coordinate_limits.y_min, coordinate_limits.y_max)
        #     z = np.clip(z, coordinate_limits.z_min, coordinate_limits.z_max)

        scatter: PathCollection = ax.scatter(
            x, y, z,
            c=structure_visual_params.color_atoms,
            label=label if label else None,
            s=structure_visual_params.size,  # type: ignore
            alpha=structure_visual_params.transparency,
            picker=True if is_interactive_mode else False,
        )

        if to_set_equal_scale is None:
            to_set_equal_scale = structure_visual_params.to_set_equal_scale

        if to_set_equal_scale:
            cls._set_equal_scale(ax, x, y, z)

        # Handle grid display
        if to_show_grid is True:
            ax.grid(True)
        elif to_show_grid is False:
            ax.grid(False)
            # Hide axes, ticks, labels, panes, and background so only atoms/bonds remain
            try:
                ax.set_axis_off()
            except Exception:
                pass
            try:
                ax.set_xticks([])
                ax.set_yticks([])
                zticks_setter = getattr(ax, 'set_zticks', None)
                if callable(zticks_setter):
                    zticks_setter([])
            except Exception:
                pass
            try:
                ax.set_xlabel('')
                ax.set_ylabel('')
                ax.set_zlabel('')  # type: ignore
            except Exception:
                pass
            try:
                # Make axis and figure backgrounds transparent
                ax.set_facecolor('none')
                fig.patch.set_alpha(0.0)
            except Exception:
                pass
            try:
                # Hide 3D panes and their edges if available
                ax.xaxis.pane.fill = False  # type: ignore[attr-defined]
                ax.yaxis.pane.fill = False  # type: ignore[attr-defined]
                z_axis_obj = getattr(ax, 'zaxis', None)
                if z_axis_obj is not None:
                    z_axis_obj.pane.fill = False  # type: ignore[attr-defined]
                ax.xaxis.pane.set_edgecolor('none')  # type: ignore[attr-defined]
                ax.yaxis.pane.set_edgecolor('none')  # type: ignore[attr-defined]
                if z_axis_obj is not None:
                    z_axis_obj.pane.set_edgecolor('none')  # type: ignore[attr-defined]
            except Exception:
                pass
            try:
                # Best-effort removal of axis lines and grids (may rely on private attrs)
                axes_seq = [ax.xaxis, ax.yaxis]
                z_axis_obj = getattr(ax, 'zaxis', None)
                if z_axis_obj is not None:
                    axes_seq.append(z_axis_obj)
                for axis in axes_seq:
                    try:
                        axis._axinfo["grid"]["linewidth"] = 0  # type: ignore[attr-defined]
                    except Exception:
                        pass
                try:
                    ax.w_xaxis.line.set_lw(0.)  # type: ignore[attr-defined]
                    ax.w_yaxis.line.set_lw(0.)  # type: ignore[attr-defined]
                    ax.w_zaxis.line.set_lw(0.)  # type: ignore[attr-defined]
                except Exception:
                    pass
            except Exception:
                pass

        if to_show_coordinates is True or (
                to_show_coordinates is None and structure_visual_params.to_show_coordinates):
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

        if to_show_indexes or (
                to_show_indexes is None and structure_visual_params.to_show_indexes):
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
                structure_visual_params=structure_visual_params,
                num_of_min_distances=num_of_min_distances,
                skip_first_distances=skip_first_distances,
                bonds_to_highlight=bonds_to_highlight,
                to_build_edge_vertical_lines=to_build_edge_vertical_lines,
            )

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
