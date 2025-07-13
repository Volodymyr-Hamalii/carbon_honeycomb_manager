"""Carbon honeycomb modeling and analysis functionality."""

import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import pandas as pd

from src.services.utils import Constants, Logger, FileReader
from src.services import (
    DistanceMeasurer,
    LinesOperations,
    StructureVisualizer,
    VisualizationParams,
)
from src.interfaces import (
    ICarbonHoneycombChannel,
    ICarbonHoneycombPlane,
    ICarbonHoneycombHexagon,
)
from src.entities import Points, CoordinateLimits, MvpParams

from .carbon_honeycomb_actions import CarbonHoneycombActions


logger = Logger("CarbonHoneycombModeller")


class CarbonHoneycombModeller:
    """Carbon honeycomb modeling and analysis functionality."""

    @staticmethod
    def show_init_structure(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: MvpParams,
    ) -> None:
        """
        Show 3D model of init_data/{structure_dir}/file_name.

        Args:
            project_dir: Project directory name
            subproject_dir: Subproject directory name
            structure_dir: Structure directory name
            params: MVP parameters containing visualization settings
        """
        file_name: str | None = params.file_name
        if file_name is None:
            raise ValueError("File name is required")

        carbon_points: NDArray[np.float64] = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        coordinate_limits: CoordinateLimits = CoordinateLimits(
            x_min=params.x_min,
            x_max=params.x_max,
            y_min=params.y_min,
            y_max=params.y_max,
            z_min=params.z_min,
            z_max=params.z_max,
        )

        StructureVisualizer.show_structure(
            carbon_points,
            to_build_bonds=params.to_build_bonds,
            to_show_coordinates=params.to_show_coordinates,
            to_show_indexes=params.to_show_c_indexes,
            title=structure_dir,
            to_set_equal_scale=True,
            num_of_min_distances=params.bonds_num_of_min_distances,
            skip_first_distances=params.bonds_skip_first_distances,
            coordinate_limits=coordinate_limits,
            visual_params=VisualizationParams.carbon,
        )

    @staticmethod
    def show_one_channel_structure(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: MvpParams,
    ) -> None:
        """
        Build one channel model from init_data/{structure_dir}/file_name atoms
        based on structure settings channel limits.

        Args:
            project_dir: Project directory name
            subproject_dir: Subproject directory name
            structure_dir: Structure directory name
            params: MVP parameters containing visualization settings
        """
        file_name: str | None = params.file_name
        if file_name is None:
            raise ValueError("File name is required")

        carbon_points: NDArray[np.float64] = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        carbon_channels: list[ICarbonHoneycombChannel] = CarbonHoneycombActions.split_init_structure_into_separate_channels(
            coordinates_carbon=Points(points=carbon_points))

        carbon_channel: ICarbonHoneycombChannel = carbon_channels[0]

        coordinate_limits: CoordinateLimits = CoordinateLimits(
            x_min=params.x_min,
            x_max=params.x_max,
            y_min=params.y_min,
            y_max=params.y_max,
            z_min=params.z_min,
            z_max=params.z_max,
        )

        StructureVisualizer.show_structure(
            coordinates=carbon_channel.points,
            to_build_bonds=params.to_build_bonds,
            title=structure_dir,
            to_show_coordinates=params.to_show_coordinates,
            to_show_indexes=params.to_show_c_indexes,
            num_of_min_distances=params.bonds_num_of_min_distances,
            skip_first_distances=params.bonds_skip_first_distances,
            coordinate_limits=coordinate_limits,
            visual_params=VisualizationParams.carbon,
        )

    @classmethod
    def show_2d_channel_scheme(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: MvpParams,
    ) -> None:
        """
        Get details of the channel from structure settings:
        - distance from the channel center to the planes and to the connection edges,
        - angles between the planes on the connection edges.

        Shows the details in the console and on the 2D graph.

        Args:
            project_dir: Project directory name
            subproject_dir: Subproject directory name
            structure_dir: Structure directory name
            params: MVP parameters containing visualization settings
        """
        fontsize: int = 8

        carbon_channel: ICarbonHoneycombChannel = cls.build_carbon_channel(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
        )

        center_2d: NDArray[np.float64] = carbon_channel.center[:2]
        planes: list[ICarbonHoneycombPlane] = carbon_channel.planes

        # Convert planes to 2D points (take only unique x and y coordinates)
        planes_points_2d: list[NDArray[np.float64]] = [
            np.unique(plane.points[:, :2], axis=0) for plane in planes
        ]

        ax: Axes = StructureVisualizer.get_2d_plot(
            np.concatenate(planes_points_2d),
            title=structure_dir,
            visual_params=VisualizationParams.carbon,
        )

        # Add center point to the plot
        ax.scatter(
            center_2d[0],
            center_2d[1],
            color=VisualizationParams.al_1.color_atoms,
            alpha=0.5,
            label='Center',
        )

        # Add center coordinates text
        ax.text(
            center_2d[0], center_2d[1],
            f"({center_2d[0]:.2f}, {center_2d[1]:.2f})",
            fontsize=fontsize,
            ha="center",
            va="bottom",
        )

        processed_points: list[NDArray[np.float64]] = []

        for i, plane_points_2d in enumerate(planes_points_2d):
            # Build lines for the plane
            ax.plot(
                plane_points_2d[:, 0],
                plane_points_2d[:, 1],
                color=VisualizationParams.carbon.color_bonds,
                alpha=0.5,
                label='Plane',
            )

            # Get points with the min and max x coordinate
            min_point = plane_points_2d[np.argmin(plane_points_2d[:, 0])]
            max_point = plane_points_2d[np.argmax(plane_points_2d[:, 0])]

            line_equation: tuple[float, float, float, float] = LinesOperations.get_line_equation(
                min_point, max_point
            )

            distance_from_center_to_plane: float = DistanceMeasurer.calculate_distance_from_plane(
                np.array([center_2d]), line_equation
            )

            # Center of the plane
            plane_center = np.mean(plane_points_2d, axis=0)

            if params.to_show_dists_to_plane:
                # Show the distance from the center to the plane
                ax.text(
                    plane_center[0], plane_center[1],
                    f"To plane: {distance_from_center_to_plane:.2f}",
                    fontsize=fontsize,
                    ha="center",
                    va="top" if plane_center[1] < center_2d[1] else "bottom",
                )

            if params.to_show_channel_angles:
                # Calculate the angle between the plane and the next plane
                if i < len(planes_points_2d) - 1:
                    next_plane_points: NDArray[np.float64] = planes_points_2d[i + 1]
                else:
                    next_plane_points: NDArray[np.float64] = planes_points_2d[0]

                next_plane_line_equation: tuple[float, float, float, float] = LinesOperations.get_line_equation(
                    next_plane_points[0], next_plane_points[1]
                )

                # Calculate vectors along the lines
                current_vector: NDArray[np.float64] = (
                    np.array([1.0, line_equation[1] / line_equation[0]])
                    if line_equation[0] != 0
                    else np.array([0.0, 1.0])
                )
                next_vector: NDArray[np.float64] = (
                    np.array([1.0, next_plane_line_equation[1] / next_plane_line_equation[0]])
                    if next_plane_line_equation[0] != 0
                    else np.array([0.0, 1.0])
                )

                # Normalize vectors
                current_vector = current_vector / np.linalg.norm(current_vector)
                next_vector = next_vector / np.linalg.norm(next_vector)

                # Calculate angle using dot product and handle the direction
                dot_product: float = np.clip(np.dot(current_vector, next_vector), -1.0, 1.0)
                angle: float = np.degrees(np.arccos(dot_product))

                # Ensure we get the smaller angle (should be ~120° not ~240°)
                if angle > 180:
                    angle = 360 - angle
                if angle < 90:
                    angle = 180 - angle

                # Get the point that is general for plane_points_2d and next_plane_points
                general_planes_point: NDArray[np.float64] = next(
                    point for point in plane_points_2d
                    if any(np.array_equal(point, p) for p in next_plane_points)
                )

                ax.text(
                    general_planes_point[0], general_planes_point[1],
                    f"{round(angle, 1)}°",
                    fontsize=fontsize,
                    ha="left" if general_planes_point[0] < center_2d[0] else "right",
                    va="top" if general_planes_point[1] > center_2d[1] else "bottom",
                )

            if params.to_show_dists_to_edges:
                for point in (min_point, max_point):
                    if not any(np.array_equal(point, p) for p in processed_points):
                        processed_points.append(point)

                        distance_from_center_to_point: np.floating = np.linalg.norm(center_2d - point)

                        # Show the distance from the center to the point
                        ax.text(
                            point[0], point[1],
                            f"To edge: {distance_from_center_to_point:.2f}",
                            fontsize=fontsize,
                            ha="center",
                            va="bottom" if point[1] > center_2d[1] else "top",
                        )

        if params.to_show_coordinates:
            # Show coordinates near each point
            for xx, yy in zip(carbon_channel.points[:, 0], carbon_channel.points[:, 1]):
                ax.annotate(
                    f"({xx:.2f}, {yy:.2f})",
                    (xx, yy),
                    textcoords="offset points",
                    xytext=(5, 5),  # Offset from the point
                    fontsize=6,
                )

        if params.to_show_plane_lengths:
            for plane in carbon_channel.planes:
                # Get the points with max and min x coordinate
                point_1: NDArray[np.float64] = plane.points[np.argmax(plane.points[:, 0])]
                point_2: NDArray[np.float64] = plane.points[np.argmin(plane.points[:, 0])]

                # If the points have the same x coordinate, use the y coordinate
                if point_1[0] == point_2[0]:
                    point_1 = plane.points[np.argmax(plane.points[:, 1])]
                    point_2 = plane.points[np.argmin(plane.points[:, 1])]

                # Convert the points to 2D
                point_1 = point_1[:2]
                point_2 = point_2[:2]

                # Get the distance between the points
                distance: float = DistanceMeasurer.calculate_distance_between_2_points(point_1, point_2)

                # Show the distance
                ax.text(
                    plane.center[0], plane.center[1],
                    f"Length: {distance:.2f}",
                    fontsize=fontsize,
                    ha="center",
                    va="bottom" if plane.center[1] > center_2d[1] else "top",
                )

        # Set equal scale for the plot
        x_min, x_max = carbon_channel.points[:, 0].min(), carbon_channel.points[:, 0].max()
        y_min, y_max = carbon_channel.points[:, 1].min(), carbon_channel.points[:, 1].max()

        min_lim = np.abs(np.min([x_min, y_min]))
        max_lim = np.abs(np.max([x_max, y_max]))

        delta = (max_lim + min_lim) / 2 * 1.2

        x_mid = (x_max + x_min) / 2
        y_mid = (y_max + y_min) / 2

        ax.set_xlim(x_mid - delta, x_mid + delta)
        ax.set_ylim(y_mid - delta, y_mid + delta)

        plt.show()

    @classmethod
    def get_channel_params(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: MvpParams,
    ) -> pd.DataFrame:
        """
        Get parameters of the channel from structure settings:
        - distance between atoms,
        - distance between hexagon layers.

        Args:
            project_dir: Project directory name
            subproject_dir: Subproject directory name
            structure_dir: Structure directory name
            params: MVP parameters containing file settings

        Returns:
            DataFrame with channel parameters
        """
        file_name: str = params.file_name or Constants.file_names.INIT_DAT_FILE

        carbon_channel: ICarbonHoneycombChannel = cls.build_carbon_channel(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        min_dist_between_atoms: np.floating = np.mean(
            DistanceMeasurer.calculate_min_distances_between_points(carbon_channel.points)
        )

        hexagons: list[ICarbonHoneycombHexagon] = [
            hexagon for plane in carbon_channel.planes
            for hexagon in plane.hexagons
        ]
        hexagon_centers: NDArray[np.float64] = np.array([hexagon.center for hexagon in hexagons])
        hexagon_centers_z_coords: NDArray[np.float64] = np.sort(
            np.round(np.unique(hexagon_centers[:, 2]), 3)
        )
        logger.info(f"Hexagon centers Z coordinates ({structure_dir}): {hexagon_centers_z_coords}")

        # Get all possible distances between hexagon center Z coordinates
        dists_between_hexagon_center_layers: NDArray[np.float64] = np.abs(
            hexagon_centers_z_coords[:, None] - hexagon_centers_z_coords[None, :]
        )
        min_dists_between_hexagon_layers: np.floating = np.min(
            dists_between_hexagon_center_layers[dists_between_hexagon_center_layers > 0.01]
        )

        carbon_channel_constants: dict[str, float] = {
            "Average distance between atoms (Å)": round(float(min_dist_between_atoms), 4),
            "Min distance between hexagon layers (Å)": round(float(min_dists_between_hexagon_layers), 4),
        }

        # Convert the dictionary to a DataFrame
        carbon_channel_constants_df: pd.DataFrame = pd.DataFrame.from_dict(
            carbon_channel_constants, orient='index', columns=['Value']
        ).reset_index().rename(columns={'index': 'Name'})

        return carbon_channel_constants_df

    @staticmethod
    def build_carbon_coordinates(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str | None = None,
    ) -> Points:
        if file_name is None:
            file_name = Constants.file_names.INIT_DAT_FILE

        carbon_points: np.ndarray = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        if len(carbon_points) == 0:
            raise ValueError(f"No carbon atoms found in {file_name} file.")

        carbon_points = np.round(carbon_points, 3)

        return Points(points=carbon_points)

    @classmethod
    def build_carbon_channel(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str | None = None,
    ) -> ICarbonHoneycombChannel:
        coordinates_carbon: Points = cls.build_carbon_coordinates(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        carbon_channels: list[ICarbonHoneycombChannel] = CarbonHoneycombActions.split_init_structure_into_separate_channels(
            coordinates_carbon=coordinates_carbon)
        return carbon_channels[0]
