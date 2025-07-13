import numpy as np
from numpy.typing import NDArray
from collections import defaultdict

from src.interfaces import ICarbonHoneycombPlane
from src.services import Logger, PointsOrganizer, DistanceMeasurer

from .planes import CarbonHoneycombPlane


logger = Logger(__name__)


class CarbonHoneycombChannelActions:

    @classmethod
    def build_planes(cls, points: np.ndarray) -> list[ICarbonHoneycombPlane]:
        # 1. Group points into lines in the xOy plane
        groups_by_xy_lines: list[dict[tuple[np.float32, np.float32], np.ndarray]] = PointsOrganizer.group_by_the_xy_lines(
            coordinates_to_group=points, epsilon=1e-1, min_points_in_line=3)

        # 2. Build sets of (x, y) for each group and neighbor relationships
        xy_sets: list[set[tuple[np.floating, np.floating]]] = [set(group.keys()) for group in groups_by_xy_lines]
        point_group_neighbors: dict[int, list[int]] = cls._build_neighbors(xy_sets)

        # 3. Find the first (base) plane index and second plane index
        prev_plane_index, next_plane_index = cls._find_first_and_second_plane(xy_sets)

        if prev_plane_index == -1 or next_plane_index == -1:
            logger.warning("Planes not build")
            return []

        # 4. Build the planes by traversing neighbor relationships
        planes: list[ICarbonHoneycombPlane] = []
        for i in range(len(point_group_neighbors)):
            # If no planes are built yet, pick the "base" plane; otherwise pick the "next"
            if not planes:
                index: int = prev_plane_index
            else:
                index: int = next_plane_index
                # Advance the next_plane_index to a neighbor (avoiding the previous plane)
                for neighbor_index in point_group_neighbors[next_plane_index]:
                    if neighbor_index != prev_plane_index:
                        next_plane_index = neighbor_index
                        break
                prev_plane_index = index

            # 5. Concatenate all arrays in the chosen group to build one plane's coordinates
            plane_points: np.ndarray = np.concatenate(list(groups_by_xy_lines[index].values()), axis=0)

            planes.append(CarbonHoneycombPlane(points=plane_points))

        return planes

    @classmethod
    def _build_neighbors(
        cls,
        xy_sets: list[set[tuple[np.float32, np.float32]]]
    ) -> dict[int, list[int]]:
        """ Build neighbor relationships between groups that share at least one (x,y). """
        neighbors = defaultdict(list)
        for i, i_points in enumerate(xy_sets):
            for j, j_points in enumerate(xy_sets):
                if i != j and i_points & j_points:
                    neighbors[i].append(j)
        return neighbors

    @classmethod
    def _find_first_and_second_plane(
        cls,
        xy_sets: list[set[tuple[np.float32, np.float32]]],
        base_point: tuple[float | np.float32, float | np.float32] = (0., 0.),
    ) -> tuple[int, int]:
        """
        Identify two special planes:
          - The 'base' plane (prev_plane_index): one containing (0,0) plus some other point with y=0.
          - The 'second' plane (next_plane_index): if there's another group with (0,0), pick that too.
        """
        prev_plane_index: int = -1
        next_plane_index: int = -1

        for i, group in enumerate(xy_sets):
            # If a group contains (0,0), it might be our base or second plane
            if base_point in group:
                # If we haven't found the base yet, verify the group has another point with y=0
                if prev_plane_index == -1:
                    # for pt in group:
                    # e.g., at least one more point with x != 0 and y == 0
                    # if pt[0] != 0. and pt[1] == 0.:
                    if all(y == 0 for _, y in group):
                        prev_plane_index = i
                        break
                    # If we still haven't assigned prev_plane_index, then assign next_plane_index
                    if prev_plane_index == -1 and next_plane_index == -1:
                        next_plane_index = i
                else:
                    # If base is found, the next group containing (0,0) is second plane
                    next_plane_index = i

        if (prev_plane_index == -1 and next_plane_index == -1) and (base_point == (0., 0.)):
            # Take other base_point with x == 0
            for group in xy_sets:
                # Find the line on Ox
                if all(y == 0 for _, y in group):
                    # Sort by x coordinate
                    sorted_group: list[tuple[np.float32, np.float32]] = sorted(list(group), key=lambda x: x[0])
                    # point_index: int = round(len(sorted_group) / 2)

                    # Take the point with the lowest X
                    point: tuple[np.float32, np.float32] = sorted_group[0]
                    return cls._find_first_and_second_plane(xy_sets, base_point=point)

        # if prev_plane_index == -1:
        #     raise ValueError("Base plane (first plane) not found.")

        # if next_plane_index == -1:
        #     raise ValueError("Second plane not found.")

        return prev_plane_index, next_plane_index

    @staticmethod
    def calculate_ave_dist_between_closest_atoms(points: np.ndarray) -> np.floating:
        dists: np.ndarray = DistanceMeasurer.calculate_min_distances_between_points(points=np.array(points))
        average: np.floating = np.average(dists)

        max_deviation = 2  # percents
        lower_bound: np.floating = average * (1 - max_deviation / 100)
        upper_bound: np.floating = average * (1 + max_deviation / 100)

        # Filter all fluctuations (that have deviation from the average by more than max_deviation)
        dists_filtered: np.ndarray = dists[(dists >= lower_bound) & (dists <= upper_bound)]

        result: np.floating = np.average(dists_filtered)

        # Check if only wrong distances were filtered (there shouldn't be many of them)
        num_of_init: int = len(points)
        num_of_filtered: int = num_of_init - len(dists_filtered)
        if num_of_filtered > num_of_init / 3:
            percentage: float = round(num_of_filtered / num_of_init * 100, 2)
            logger.warning(f"Filtered {percentage}% of points to calculate "
                           f"the average distance ({result} A) between hexagon centers in all planes.")

        return result

    @staticmethod
    def calculate_ave_dist_between_closest_hexagon_centers(planes: list[ICarbonHoneycombPlane]) -> np.floating:
        hexagon_centers: list[NDArray[np.float64]] = [
            hexagon.center
            for plane in planes
            for hexagon in plane.hexagons
        ]

        dists_between_centers: np.ndarray = DistanceMeasurer.calculate_min_distances_between_points(
            points=np.array(hexagon_centers))

        return np.average(dists_between_centers)
