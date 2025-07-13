import numpy as np

from src.entities import Points
from ..distance_measurer import DistanceMeasurer


class PointsFilter:
    @classmethod
    def filter_coordinates_related_to_plane(
            cls,
            points: Points,
            A: float, B: float, C: float, D: float,
            direction: bool,
            min_distance: float = 0,
    ) -> Points:
        """
        A, B, C, D are the parameters from the
        Ax + By + Cz + D = 0 plane equation.
        """

        signed_distances: float = DistanceMeasurer.calculate_signed_distance_from_plane(
            points.points, A, B, C, D)

        if direction:
            # Keep points above the plane at the minimum distance
            result_points: np.ndarray = points.points[signed_distances >= min_distance]
        else:
            # Keep points below the plane at the minimum distance
            result_points: np.ndarray = points.points[signed_distances <= -min_distance]

        return Points(result_points)

    @staticmethod
    def filter_by_min_max_z(
            points_to_filter: Points,
            z_min: float,
            z_max: float,
            move_align_z: bool = False,
    ) -> Points:
        """Filter points_to_filter by min and max z coordinate of points_with_min_max_z."""

        if len(points_to_filter) == 0:
            return points_to_filter

        filtered_points: np.ndarray = points_to_filter.points[points_to_filter.points[:, 2] >= z_min]

        if len(filtered_points) == 0:
            return Points(filtered_points)

        if move_align_z:
            # Move intercalated atoms along Oz down to align
            # the lowest intercalated atom with the channel bottom
            move_to: np.float32 = np.min(filtered_points[:, 2]) - z_min
            filtered_points[:, 2] = filtered_points[:, 2] - move_to

        filtered_points = filtered_points[filtered_points[:, 2] <= z_max]

        return Points(filtered_points)
