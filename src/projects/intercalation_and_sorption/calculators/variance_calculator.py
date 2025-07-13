import numpy as np
from numpy import floating
from scipy.spatial.distance import cdist

from src.interfaces import IPoints
from src.services import DistanceMeasurer


class VarianceCalculator:
    @classmethod
    def _calculate_distance_variance(
            cls,
            translation_vector: np.ndarray,
            channel_points: np.ndarray | IPoints,
            inner_points: np.ndarray | IPoints,
    ) -> floating | float:
        """
        Calculate the variance of the minimum distances between inner points
        and channel points after applying a translation.
        """
        if isinstance(inner_points, IPoints):
            inner_points = inner_points.points

        if isinstance(channel_points, IPoints):
            channel_points = channel_points.points

        # Apply translation to inner points
        translated_inner_points: np.ndarray = inner_points.copy()  # type: ignore
        translated_inner_points[:, 0] += translation_vector[0]  # Along Ox
        translated_inner_points[:, 1] += translation_vector[1]  # Along Oy

        # Calculate distances between each translated inner point and all channel points
        # distances: ndarray = cdist(translated_inner_points, channel_points)

        # # Get minimum distance from each inner point to any channel point
        # min_distances: floating = np.min(distances, axis=1)

        # # Calculate the variance of these minimum distances
        # variance: floating = np.var(min_distances)

        # TO CHECK ValueError: The user-provided objective function must return a scalar value.
        return -DistanceMeasurer.calculate_min_distance_sum(translated_inner_points, channel_points)

    @staticmethod
    def calculate_variance_related_channel(
        inner_points: np.ndarray | IPoints,
        channel_points: np.ndarray | IPoints,
    ) -> floating:
        """ Calculate variance of the minimum distances after translation and rotation. """
        if isinstance(inner_points, IPoints):
            inner_points = inner_points.points

        if isinstance(channel_points, IPoints):
            channel_points = channel_points.points

        distances: np.ndarray = cdist(inner_points, channel_points)
        min_distances: np.ndarray = np.min(distances, axis=1)
        variance: floating = np.var(min_distances)
        return variance

    @staticmethod
    def calculate_xy_variance(points: np.ndarray | IPoints) -> floating:
        if isinstance(points, IPoints):
            points = points.points

        """ Calculate variance of the x and y coordinates. """
        return np.var(points[:, 0]) + np.var(points[:, 1])
