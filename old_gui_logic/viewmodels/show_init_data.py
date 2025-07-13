import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import pandas as pd

from src.utils import Constants, Logger, FileReader
from src.coordinate_operations import DistanceMeasure, LinesOperations
from src.base_structure_classes import Points, CoordinateLimits
from src.structure_visualizer import StructureVisualizer, VisualizationParams
from src.projects import (
    CarbonHoneycombActions,
    CarbonHoneycombChannel,
    InterAtomsParser,
    CarbonHoneycombPlane,
    CarbonHoneycombHexagon,
)
from .view_model_params_setter import VMParamsSetter


logger = Logger("Actions")


class VMShowInitData(VMParamsSetter):
    def show_init_structure(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        """
        Show 3D model of result_data/{structure_dir}/ljout-from-init-dat.pdb

        Use params:
        structure_dir: str
        to_build_bonds: bool
        to_show_coordinates: bool
        to_show_indexes: bool
        """

        carbon_points: np.ndarray = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=self.file_name,
        )

        coordinate_limits: CoordinateLimits = CoordinateLimits(
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max,
            z_min=self.z_min,
            z_max=self.z_max,
        )

        StructureVisualizer.show_structure(
            carbon_points,
            to_build_bonds=self.to_build_bonds,
            to_show_coordinates=self.to_show_coordinates,
            to_show_indexes=self.to_show_c_indexes,
            title=structure_dir,
            to_set_equal_scale=True,
            num_of_min_distances=self.bonds_num_of_min_distances,
            skip_first_distances=self.bonds_skip_first_distances,
            coordinate_limits=coordinate_limits,
        )

    def show_one_channel_structure(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        """
        Build one channel model from result_data/{structure_dir}/ljout-from-init-dat.pdb atoms
        based on result_data/{structure_dir}/structure_settings.json channel limits.

        Write result to result_data/{structure_dir}/ljout-result-one-channel.pdb if it didn't exist.

        Use params:
        structure_dir: str
        to_build_bonds: bool
        to_show_coordinates: bool
        to_show_indexes: bool
        """

        carbon_points: np.ndarray = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=self.file_name,
        )

        carbon_channels: list[CarbonHoneycombChannel] = CarbonHoneycombActions.split_init_structure_into_separate_channels(
            coordinates_carbon=Points(points=carbon_points))

        carbon_channel: CarbonHoneycombChannel = carbon_channels[0]

        coordinate_limits: CoordinateLimits = CoordinateLimits(
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max,
            z_min=self.z_min,
            z_max=self.z_max,
        )

        # print(coordinate_limits)

        StructureVisualizer.show_structure(
            coordinates=carbon_channel.points,
            # coordinates=carbon_channel.planes[0].points,
            to_build_bonds=self.to_build_bonds,
            title=structure_dir,
            to_show_coordinates=self.to_show_coordinates,
            to_show_indexes=self.to_show_c_indexes,
            num_of_min_distances=self.bonds_num_of_min_distances,
            skip_first_distances=self.bonds_skip_first_distances,
            coordinate_limits=coordinate_limits,
        )

    def show_2d_channel_scheme(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        """
        Get details of the channel from result_data/{structure_dir}/structure_settings.json:
        - distance from the channel centet to the planes and to the connection edges,
        - angles between the planes on the connection edges.

        And shows the details in the console and on the 2D graph.

        Use params:
        structure_dir: str
        to_show_coordinates: bool
        """

        fontsize: int = 8

        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
        )

        center_2d: np.ndarray = carbon_channel.center[:2]
        planes: list[CarbonHoneycombPlane] = carbon_channel.planes

        # Convert planes to 2D points (take only unique x and y coordinates)
        # Here we have the point groups for each plane (6 groups of points laying on the lines for each of the hexagon sides)
        planes_points_2d: list[np.ndarray] = [np.unique(plane.points[:, :2], axis=0) for plane in planes]

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

        processed_points: list[np.ndarray] = []

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

            line_equation: tuple[float, float, float, float] = LinesOperations.get_line_equation(min_point, max_point)

            distance_from_center_to_plane: float = DistanceMeasure.calculate_distance_from_plane(
                np.array([center_2d]), line_equation)

            # Center of the plane
            plane_center = np.mean(plane_points_2d, axis=0)

            if self.to_show_dists_to_plane:
                # Show the distance from the center to the plane
                ax.text(
                    plane_center[0], plane_center[1],
                    f"To plane: {distance_from_center_to_plane:.2f}",
                    # color="black",
                    fontsize=fontsize,
                    ha="center",
                    va="top" if plane_center[1] < center_2d[1] else "bottom",
                )

            if self.to_show_channel_angles:
                # Calculate the angle between the plane and the next plane
                if i < len(planes_points_2d) - 1:
                    next_plane_points: np.ndarray = planes_points_2d[i + 1]
                else:
                    next_plane_points: np.ndarray = planes_points_2d[0]

                next_plane_line_equation: tuple[float, float, float, float] = LinesOperations.get_line_equation(
                    next_plane_points[0], next_plane_points[1])

                # Calculate vectors along the lines
                current_vector: np.ndarray = np.array(
                    [1.0, line_equation[1] / line_equation[0]]) if line_equation[0] != 0 else np.array([0.0, 1.0])
                next_vector: np.ndarray = np.array(
                    [1.0, next_plane_line_equation[1] / next_plane_line_equation[0]]) if next_plane_line_equation[0] != 0 else np.array([0.0, 1.0])

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
                general_planes_point: np.ndarray = next(
                    point for point in plane_points_2d
                    if any(np.array_equal(point, p) for p in next_plane_points)
                )

                ax.text(
                    general_planes_point[0], general_planes_point[1],
                    f"{round(angle, 1)}°",
                    # color="black",
                    fontsize=fontsize,
                    ha="left" if general_planes_point[0] < center_2d[0] else "right",
                    va="top" if general_planes_point[1] > center_2d[1] else "bottom",
                )

            if self.to_show_dists_to_edges:
                for point in (min_point, max_point):
                    if not any(np.array_equal(point, p) for p in processed_points):
                        processed_points.append(point)

                        distance_from_center_to_point: np.floating = np.linalg.norm(center_2d - point)
                        # distances_from_center_to_edges.append(distance_from_center_to_point)

                        # Show the distance from the center to the point
                        ax.text(
                            point[0], point[1],
                            f"To edge: {distance_from_center_to_point:.2f}",
                            # color="black",
                            fontsize=fontsize,
                            # ha="left" if point[0] > center_2d[0] else "right",
                            ha="center",
                            va="bottom" if point[1] > center_2d[1] else "top",
                        )

        if self.to_show_coordinates:
            # Show coordinates near each point
            for xx, yy in zip(carbon_channel.points[:, 0], carbon_channel.points[:, 1]):
                ax.annotate(
                    f"({xx:.2f}, {yy:.2f})",
                    (xx, yy),
                    textcoords="offset points",
                    xytext=(5, 5),  # Offset from the point
                    fontsize=6,
                )

        if self.to_show_plane_lengths:
            for plane in carbon_channel.planes:
                # Get the points with max and min x coordinate
                point_1: np.ndarray = plane.points[np.argmax(plane.points[:, 0])]
                point_2: np.ndarray = plane.points[np.argmin(plane.points[:, 0])]

                # If the points have the same x coordinate, use the y coordinate
                if point_1[0] == point_2[0]:
                    point_1 = plane.points[np.argmax(plane.points[:, 1])]
                    point_2 = plane.points[np.argmin(plane.points[:, 1])]

                # Convert the points to 2D
                point_1 = point_1[:2]
                point_2 = point_2[:2]

                # Get the distance between the points
                distance: float = DistanceMeasure.calculate_distance_between_2_points(point_1, point_2)

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

    def get_channel_params(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> pd.DataFrame:
        """
        Get parameters of the channel from result_data/{structure_dir}/structure_settings.json:
        - distance between atoms,
        - distance between hexagon layers.
        """

        file_name: str = self.file_name or Constants.file_names.INIT_DAT_FILE

        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        min_dist_between_atoms: np.floating = np.mean(
            DistanceMeasure.calculate_min_distances_between_points(carbon_channel.points)
        )

        hexagons: list[CarbonHoneycombHexagon] = [
            hexagon for plane in carbon_channel.planes
            for hexagon in plane.hexagons
        ]
        hexagon_centers: np.ndarray = np.array([hexagon.center for hexagon in hexagons])
        hexagon_centers_z_coords: np.ndarray = np.sort(np.round(np.unique(hexagon_centers[:, 2]), 3))
        logger.info(f"Hexagon centers Z coordinates ({structure_dir}): {hexagon_centers_z_coords}")

        # Get all possible distances between hexagon center Z coordinates
        dists_between_hexagon_center_layers: np.ndarray = np.abs(
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
