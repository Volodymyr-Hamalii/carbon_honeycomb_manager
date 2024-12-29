import numpy as np

from src.coordinate_operations import PointsOrganizer, DistanceMeasure
from src.structure_visualizer import StructureVisualizer

from .carbon_honeycomb_utils import CarbonHoneycombUtils
from .channel import CarbonHoneycombChannel


class CarbonHoneycombActions:

    @staticmethod
    def _filter_honeycomb_planes_groups(
        honeycomb_planes_groups: list[dict[tuple[np.float32, np.float32], np.ndarray]]
    ) -> list[dict[tuple[np.float32, np.float32], np.ndarray]]:

        lengths: list[int] = [len(i.values()) for i in honeycomb_planes_groups]

        # TODO: refactor (use list instead of the dict)
        lengths_counter_map: dict[int, int] = {}
        for i in lengths:
            if i not in lengths_counter_map:
                lengths_counter_map[i] = 0
            lengths_counter_map[i] += 1

        allowed_lengths: list[int] = []
        for i in sorted(lengths_counter_map.keys(), reverse=True):
            if (len(allowed_lengths) < 3) or (i > 4):
                allowed_lengths.append(i)

        # Filter not allowed lengths and duplicates
        filtered_honeycomb_planes_groups: list[dict[tuple[np.float32, np.float32], np.ndarray]] = []
        for i in honeycomb_planes_groups:
            if i not in filtered_honeycomb_planes_groups and len(i.values()) in allowed_lengths:
                filtered_honeycomb_planes_groups.append(i)

        return filtered_honeycomb_planes_groups

    @staticmethod
    def _build_honeycomb_channels(
        honeycomb_planes_groups: list[dict[tuple[np.float32, np.float32], np.ndarray]],
        plane_groups_indexes: list[list[int]]
    ) -> list[CarbonHoneycombChannel]:

        channels: list[CarbonHoneycombChannel] = []
        for plane_group_indexes in plane_groups_indexes:
            unique_points_set = set()
            is_main_channel = False  # With (0,0) point

            for i in plane_group_indexes:
                for point_array in honeycomb_planes_groups[i].values():
                    # point_array is something like a 2D array of shape (n,3)
                    for point in point_array:
                        # Convert to tuple to store in a set
                        point_tuple = tuple(point)
                        unique_points_set.add(point_tuple)

                        if point[0] == 0. and point[1] == 0.:
                            is_main_channel = True

            # Convert the set of tuples back to a numpy array
            honeycomb_points: np.ndarray = np.array(list(unique_points_set))
            honeycomb_channel = CarbonHoneycombChannel(points=honeycomb_points)

            if is_main_channel:
                channels.insert(0, honeycomb_channel)
            else:
                channels.append(honeycomb_channel)

        return channels

    @classmethod
    def split_init_structure_into_separate_channels(
            cls, carbon_coordinates: np.ndarray
    ) -> list[CarbonHoneycombChannel]:

        # Create groups with the same X and Y coordinate
        # (like, to split all points into columns)
        groups_by_xy: dict[
            tuple[np.float32, np.float32], np.ndarray
        ] = PointsOrganizer.group_by_unique_xy(carbon_coordinates)

        # Define groups that lie on the same line
        groups_by_the_xy_lines: list[
            dict[tuple[np.float32, np.float32], np.ndarray]
        ] = PointsOrganizer.group_by_the_xy_lines(groups_by_xy, epsilon=1e-1, min_points_in_line=3)

        # Define 2D honeycomb structure
        x_y_points: np.ndarray = np.array([
            [i[0], i[1]] for i in groups_by_xy.keys()
        ])

        # StructureVisualizer.show_2d_graph(x_y_points)

        # Split by the max distance between groups (to define separate channel planes)
        distances_between_xy_groups: np.ndarray = DistanceMeasure.calculate_min_distances_between_points(x_y_points)

        clearance_dist_coefficient = 1.5
        max_distance_between_xy_groups: np.floating = np.max(distances_between_xy_groups) * clearance_dist_coefficient

        honeycomb_planes_groups: list[
            dict[tuple[np.float32, np.float32], np.ndarray]
        ] = CarbonHoneycombUtils.split_xy_groups_by_max_distances(
            groups_by_the_xy_lines, max_distance_between_xy_groups)

        honeycomb_planes_groups = cls._filter_honeycomb_planes_groups(honeycomb_planes_groups)

        end_points_of_groups: list[
            tuple[tuple[np.float32, np.float32], tuple[np.float32, np.float32]]
        ] = CarbonHoneycombUtils.find_end_points_of_honeycomb_planes_groups(
            honeycomb_planes_groups)

        plane_groups_indexes: list[list[int]] = CarbonHoneycombUtils.found_polygon_node_indexes(end_points_of_groups)

        honeycomb_channels: list[CarbonHoneycombChannel] = cls._build_honeycomb_channels(
            honeycomb_planes_groups, plane_groups_indexes)

        # honeycomb_channel = honeycomb_channels[0]
        # plane = honeycomb_channel.planes[0]

        # StructureVisualizer.show_structure(plane.points)

        # hexagon = plane.hexagons[1]
        # points = []

        # # for plane in honeycomb_channels[0].planes:
        # for hexagon in plane.pentagons:
        #     for point in hexagon.points:
        #         points.append(point)
        #     points.append(hexagon.center)

        # StructureVisualizer.show_structure(np.array(points), to_build_bonds=True, num_of_min_distances=2)
        return honeycomb_channels
