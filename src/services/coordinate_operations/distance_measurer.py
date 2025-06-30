from math import sqrt

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.distance import cdist

from src.interfaces import IDistanceMeasurer, IPoints
from src.services.utils import Logger


logger = Logger("DistanceMeasurer")


class DistanceMeasurer(IDistanceMeasurer):
    @staticmethod
    def calculate_distance_between_2_points(
            p1: tuple | NDArray[np.float64],
            p2: tuple | NDArray[np.float64],
    ) -> float:
        """
        Compute distance between two points (x1, y1, z1) and (x2, y2, z2),
        where z1 and z2 are optional.
        """
        # Add z coordinate if it doesn't exist
        if len(p1) == 2:
            p1 = (p1[0], p1[1], 0)

        if len(p2) == 2:
            p2 = (p2[0], p2[1], 0)

        # Calculate the distance
        return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

    @staticmethod
    def calculate_distance_from_plane(
            points: NDArray[np.float64] | IPoints,
            line_params: tuple[float, float, float, float],
    ) -> float:
        """ Calculate the distance of each point from the line. """

        if isinstance(points, IPoints):
            points = points.points

        # Convert 2D to 3D if no z coordinate
        if points.shape[1] == 2:
            points = np.hstack((points, np.zeros((points.shape[0], 1))))

        A, B, C, D = line_params

        numerator: NDArray[np.float64] = np.abs(A * points[:, 0] + B * points[:, 1] + C * points[:, 2] + D)
        denominator: np.float64 = np.sqrt(A**2 + B**2 + C**2)
        return (numerator / denominator)[0]

    @staticmethod
    def calculate_signed_distance_from_plane(
            points: NDArray[np.float64] | IPoints,
            A: float,
            B: float,
            C: float,
            D: float,
    ) -> float:
        """ Calculate the signed distance of each point from the plane. """
        if isinstance(points, IPoints):
            points = points.points

        # Convert 2D to 3D if no z coordinate
        if points.shape[1] == 2:
            points = np.hstack((points, np.zeros((points.shape[0], 1))))

        numerator: NDArray[np.float64] = A * points[:, 0] + B * points[:, 1] + C * points[:, 2] + D
        denominator = np.sqrt(A**2 + B**2 + C**2)
        return numerator / denominator

    @staticmethod
    def calculate_dist_matrix(
            points: NDArray[np.float64] | IPoints,
    ) -> NDArray[np.float64]:
        """ Calculate distance matrix between provided points (with inf in diagonal). """
        if isinstance(points, IPoints):
            points = points.points

        inf_diag_matrix: NDArray[np.float64] = np.diag([np.inf] * len(points))

        # Add inf_diag_matrix to distances tp remove zeros
        return cdist(points, points) + inf_diag_matrix

    @staticmethod
    def calculate_min_distances(
            points_1: NDArray[np.float64] | IPoints,
            points_2: NDArray[np.float64] | IPoints,
    ) -> NDArray[np.float64]:
        """ Returns min distance between 2 provided point sets. """
        if isinstance(points_1, IPoints):
            points_1 = points_1.points

        if isinstance(points_2, IPoints):
            points_2 = points_2.points

        distances: NDArray[np.float64] = cdist(points_1, points_2)
        return np.min(distances, axis=1)

    @classmethod
    def calculate_min_distance_sum(
            cls,
            points_1: NDArray[np.float64] | IPoints,
            points_2: NDArray[np.float64] | IPoints,
    ) -> np.float64:
        """ Returns sum of min distances between 2 provided point sets. """
        min_distances: NDArray[np.float64] = cls.calculate_min_distances(points_1, points_2)
        return np.sum(min_distances)

    @classmethod
    def calculate_min_distances_between_points(
            cls,
            points: NDArray[np.float64] | IPoints,
    ) -> NDArray[np.float64]:
        """ Returns min distances between points. """
        if isinstance(points, IPoints):
            points = points.points

        distances: NDArray[np.float64] = cls.calculate_dist_matrix(points)
        return np.min(distances, axis=1)
