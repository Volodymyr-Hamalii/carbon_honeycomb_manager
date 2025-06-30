import numpy as np
from numpy.typing import NDArray
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from scipy.spatial.distance import pdist, squareform

from src.interfaces import ILinesBuilder, IVisualizationParams


class LinesBuilder(ILinesBuilder):
    @classmethod
    def add_lines(
        cls,
        coordinates: NDArray[np.float64],
        ax: Axes,
        num_of_min_distances: int,
        visual_params: IVisualizationParams,
        skip_first_distances: int = 0,
    ) -> None:
        """
        Add lines to the axis.

        To get the atoms between which we have to build bonds you can set the following parameters:
        num_of_min_distances: int - number of the distances we use as a target to build the line,
        skip_first_distances: int - set it if have to build the bonds not for all minimal distances.
        """

        lines: list[list[NDArray[np.float64]]] = cls._build_lines(
            coordinates=coordinates,
            num_of_min_distances=num_of_min_distances,
            skip_first_distances=skip_first_distances)

        lc = Line3DCollection(
            lines,
            colors=visual_params.color_bonds,
            linewidths=visual_params.bonds_width,
            alpha=visual_params.transparency_bonds,
        )
        ax.add_collection3d(lc)  # type: ignore

        # To highlight the front plane (uncomment and ajust limits if needed)

        # # Split coordinates into two groups: with x>5 & y<5.5 and the rest
        # x_min_limit: float = 5.0
        # y_max_limit: float = 5.5
        # coordinates_group_1: NDArray[np.float64] = coordinates[
        #     (coordinates[:, 0] > x_min_limit) & (coordinates[:, 1] < y_max_limit)
        # ]

        # if len(coordinates_group_1) > 0:
        #     lines_group_1: list[list[NDArray[np.float64]]] = cls._build_lines(
        #         coordinates=coordinates_group_1,
        #         num_of_min_distances=num_of_min_distances,
        #         skip_first_distances=skip_first_distances)

        #     lc = Line3DCollection(
        #         lines_group_1,
        #         colors=visual_params.color_bonds,
        #         linewidths=1.25,
        #         alpha=visual_params.transparency_bonds,
        #     )
        #     ax.add_collection3d(lc)  # type: ignore
        # else:
        #     logger.warning(
        #         f"No coordinates to build lines for x_min_limit={x_min_limit} and y_max_limit={y_max_limit}"
        #     )

        #########################################################################################
        # # To build additional dotted vertical lines (uncomment and ajust limits if needed)

        # # Get 2 points from coordinates_group_1: first with max X and second with min X
        # # and with max Z coordinate:
        # max_x_mask: NDArray[np.float64] = coordinates_group_1[:, 0] == coordinates_group_1[:, 0].max()
        # max_x_points: NDArray[np.float64] = coordinates_group_1[max_x_mask]
        # point_1: NDArray[np.float64] = max_x_points[max_x_points[:, 2].argmax()]

        # min_x_mask: NDArray[np.float64] = coordinates_group_1[:, 0] == coordinates_group_1[:, 0].min()
        # min_x_points: NDArray[np.float64] = coordinates_group_1[min_x_mask]
        # point_2: NDArray[np.float64] = min_x_points[min_x_points[:, 2].argmax()]

        # z_max: float = 16.
        # line1: list[list[float]] = [[point_1[0], point_1[1], 0], [point_1[0], point_1[1], z_max]]
        # line2: list[list[float]] = [[point_2[0], point_2[1], 0], [point_2[0], point_2[1], z_max]]

        # lc = Line3DCollection(
        #     [line1, line2],
        #     colors=visual_params.color_bonds,
        #     linewidths=1.75,
        #     alpha=visual_params.transparency_bonds,
        #     linestyles='dotted',
        # )
        # ax.add_collection3d(lc)  # type: ignore

    @classmethod
    def _build_lines(
            cls,
            coordinates: NDArray[np.float64],
            num_of_min_distances: int,
            skip_first_distances: int,
    ) -> list[list[NDArray[np.float64]]]:
        """
        Build lines between points (like, bonds between atoms).

        Return lines: list[list[ndarray]]

        To add them to the structure add lines like
            lc = Line3DCollection(lines, colors='black', linewidths=1)
            ax.add_collection3d(lc)  # ax: Axes
        """

        lines: list[list[NDArray[np.float64]]] = []

        # Calculate the distance matrix for all atoms
        distances_matrix: NDArray[np.float64] = squareform(pdist(coordinates))

        # Round all values to 2nd number of decimal place (to avoid duplicates like 1.44000006 and 1.44000053)
        distances_matrix = np.round(distances_matrix, decimals=2)

        # Add a large value to the diagonal to ignore self-distances
        np.fill_diagonal(distances_matrix, np.inf)

        min_distances: NDArray[np.float64] = cls._find_min_unique_values(
            arr=distances_matrix,
            num_of_values=num_of_min_distances,
            skip_first_values=skip_first_distances)

        # Iterate over the distance matrix to find atom pairs with distances in min_distances
        for i in range(len(coordinates)):
            for j in range(i + 1, len(coordinates)):
                if distances_matrix[i, j] in min_distances:
                    # Append the line between atoms i and j
                    lines.append([coordinates[i], coordinates[j]])

        return lines

    @staticmethod
    def _find_min_unique_values(
            arr: NDArray[np.float64],
            num_of_values: int,
            skip_first_values: int,
    ) -> NDArray[np.float64]:
        # Flatten the array to 1D and extract unique values
        unique_values: NDArray[np.float64] = np.unique(arr)

        # Sort the unique values
        sorted_unique_values: NDArray[np.float64] = np.sort(unique_values)

        # Remove 0.0 values
        sorted_unique_values = sorted_unique_values[sorted_unique_values != 0.0]

        # Return the values from specified range
        start: int = skip_first_values
        end: int = skip_first_values + num_of_values
        return sorted_unique_values[start:end]
