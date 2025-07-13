import math
from typing import Callable

import numpy as np
from numpy import ndarray, floating
from scipy.optimize import minimize

from src.interfaces import IPoints
from src.services.utils import Logger, execution_time_logger
from src.services import PointsRotator
from src.projects.carbon_honeycomb_actions import CarbonHoneycombChannel

from ..build_intercalated_structure.by_variance.variance_calculator import VarianceCalculator
from ..intercalated_coordinates_utils import IntercalatedCoordinatesUtils


logger = Logger("InterAtomsOptimizer")


class InterAtomsOptimizer:
    """ To find equilibrium positions of the intercalated (or sorbed) points. """

    @classmethod
    def rotate_to_find_min_variance_by_minimize(
        cls,
        inner_points: IPoints,
        variance_function: Callable,
        variance_function_args: tuple | None = None,
        minimize_method: str = "BFGS",  # TODO: check the method
    ) -> IPoints:
        """
        Rotate the points inside the channel (from inner_points set) to find equilibrium positions,
        i.e., maximally equidistant from the channel atoms.
        """

        # Initial guess for angles (both x and y) in radians
        initial_angles: ndarray = np.array([0.0, 0.0])

        # Minimize the objective function with respect to the rotation angles
        result = minimize(
            variance_function,
            initial_angles,
            args=variance_function_args,
            method=minimize_method,
            options={"disp": True, "maxiter": 1000}
        )

        # Extract the optimal angles
        optimal_angle_x, optimal_angle_y = result.x

        # Apply the optimal rotations to the inner points
        return PointsRotator.rotate_on_angle_related_center(
            inner_points, angle_x=optimal_angle_x, angle_y=optimal_angle_y
        )

    @classmethod
    @execution_time_logger
    def rotate_to_find_min_variance_by_iterations(
            cls,
            carbon_channel: CarbonHoneycombChannel,
            inner_points: IPoints,
    ) -> IPoints:
        """
        Rotate the points inside the channel (from inner_points set) to find equilibrium positions,
        i.e., maximally equidistant from the channel atoms.
        """

        min_variance: float | floating = np.inf  # To track the minimal variance found
        best_inner_points: IPoints = inner_points.copy()

        # Define angle ranges to rotate over
        angle_range_to_rotate: ndarray = np.arange(- math.pi / 16, math.pi / 16, math.pi / 64)

        for angle_x in angle_range_to_rotate:
            # Rotate inner points around the x-axis
            x_rotated_points: IPoints = PointsRotator.rotate_on_angle_related_center(
                inner_points, angle_x=angle_x)

            for angle_y in angle_range_to_rotate:
                # Rotate inner points around the y-axis after the x-axis rotation
                xy_rotated_points: IPoints = PointsRotator.rotate_on_angle_related_center(
                    x_rotated_points, angle_y=angle_y)

                IntercalatedCoordinatesUtils.align_inner_points_along_channel_oz(
                    channel_points=carbon_channel, intercaleted_points=xy_rotated_points)

                if min(inner_points.points[:, 2]) < min(carbon_channel.points[:, 2]):
                    # Skip if some inner_points are out the channel along Oz
                    continue

                # Calculate the variance after this rotation
                variance: floating = VarianceCalculator.calculate_variance_related_channel(
                    channel_points=carbon_channel, inner_points=xy_rotated_points)

                # Check if this is the best configuration so far
                if variance < min_variance:
                    min_variance = variance
                    best_inner_points = xy_rotated_points

        return best_inner_points
