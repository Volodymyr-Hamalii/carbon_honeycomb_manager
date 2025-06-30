import numpy as np
from numpy import floating
from scipy.spatial.distance import cdist

from src_1.base_structure_classes import Points
from src_1.coordinate_operations.distance_measurer import DistanceMeasure


class VarianceCalculator:
    @classmethod
    def _calculate_distance_variance(
            cls,
            translation_vector: np.ndarray,
            channel_points: Points,
            inner_points: Points,
    ) -> floating | float:
        """
        Calculate the variance of the minimum distances between inner points
        and channel points after applying a translation.
        """

        # Apply translation to inner points
        translated_inner_points: Points = inner_points.copy()
        translated_inner_points.points[:, 0] += translation_vector[0]  # Along Ox
        translated_inner_points.points[:, 1] += translation_vector[1]  # Along Oy

        # Calculate distances between each translated inner point and all channel points
        # distances: np.ndarray = cdist(translated_inner_points, channel_points)

        # # Get minimum distance from each inner point to any channel point
        # min_distances: floating = np.min(distances, axis=1)

        # # Calculate the variance of these minimum distances
        # variance: floating = np.var(min_distances)

        return -DistanceMeasure.calculate_min_distance_sum(translated_inner_points.points, channel_points.points)

    @staticmethod
    def calculate_variance_related_channel(
        inner_points: Points, channel_points: Points
    ) -> floating:
        """ Calculate variance of the minimum distances after translation and rotation. """

        distances: np.ndarray = cdist(inner_points.points, channel_points.points)
        min_distances: np.ndarray = np.min(distances, axis=1)
        variance: floating = np.var(min_distances)
        return variance

    @staticmethod
    def calculate_xy_variance(points: Points) -> floating:
        """ Calculate variance of the x and y coordinates. """
        return np.var(points.points[:, 0]) + np.var(points.points[:, 1])
