import numpy as np
from numpy import ndarray, floating
from scipy.optimize import minimize

from src.utils import Logger, execution_time_logger
from src.base_structure_classes import Points
from src.data_preparation import StructureSettings
from src.coordinate_operations import (
    DistanceMeasure,
    PointsMover,
    PointsRotator,
)
from src.projects.carbon_honeycomb_actions import CarbonHoneycombChannel

from ...intercalated_coordinates_utils import IntercalatedCoordinatesUtils
from .variance_calculator import VarianceCalculator
from .al_atoms_filter import AlAtomsFilter


logger = Logger("equidistant_points_sets_in_channel")


class AlAtomsSetter:
    @classmethod
    def equidistant_points_sets_in_channel(
            cls,
            carbon_channel: CarbonHoneycombChannel,
            inner_points: Points,
            structure_settings: StructureSettings,
            # to_rotate: bool = True,
    ) -> Points:
        """
        Move the points inside the channel (from inner_points set) to occupy equilibrium positions,
        i.e., maximally equidistant from the channel atoms.

        If to_rotate=True -> rotate init points to have the min deviations.

        Returns updated inner_points.
        """

        if len(inner_points) == 0:
            logger.warning("No points provided to equidistant_points_sets_in_channel.")
            return inner_points

        return cls.rotate_and_translate_points(
            carbon_channel=carbon_channel,
            inner_points=inner_points,
            structure_settings=structure_settings,
        )

    @classmethod
    def rotate_and_translate_points(
            cls,
            carbon_channel: CarbonHoneycombChannel,
            inner_points: Points,
            structure_settings: StructureSettings,
    ) -> Points:
        # translation coordinates (X and Y) and rotation angles (along Ox and Oy)
        initial_vectors: ndarray = np.array([0.0, 0.0, 0.0, 0.0])

        IntercalatedCoordinatesUtils.align_inner_points_along_channel_oz(
            channel_points=carbon_channel, intercaleted_points=inner_points
        )

        # Use optimization to find the best translation that minimizes the variance
        result = minimize(
            cls.calculate_distance_and_rotation_variance,
            initial_vectors,
            args=(inner_points, carbon_channel, structure_settings),
            method="BFGS",
            options={"disp": True}
        )

        # Optimal translation vector found
        optimal_vectors: ndarray = result.x

        moved_points: Points = cls.move_and_rotate_related_xy(
            vectors=optimal_vectors, points=inner_points)

        return moved_points

    @classmethod
    def calculate_distance_and_rotation_variance(
            cls,
            initial_vectors: ndarray,
            inner_points: Points,
            carbon_channel: CarbonHoneycombChannel,
            structure_settings: StructureSettings,
    ) -> float | floating:

        num_of_atoms: int = len(inner_points)

        moved_points: Points = cls.move_and_rotate_related_xy(
            vectors=initial_vectors, points=inner_points)

        filtered_atoms: Points = AlAtomsFilter.filter_al_atoms_related_carbon(
            coordinates_al=inner_points,
            carbon_channel=carbon_channel,
            structure_settings=structure_settings)
        num_of_atoms_after_filter: int = len(filtered_atoms)

        if num_of_atoms_after_filter < num_of_atoms:
            return np.inf

        min_distance_sum: floating = DistanceMeasure.calculate_min_distance_sum(
            moved_points.points, carbon_channel.points)

        variance_related_channel: floating = VarianceCalculator.calculate_variance_related_channel(
            moved_points, carbon_channel)

        distance_and_rotation_variance: floating = variance_related_channel * len(inner_points) - min_distance_sum
        return distance_and_rotation_variance

    @staticmethod
    def move_and_rotate_related_xy(vectors: ndarray, points: Points) -> Points:
        translation_x, translation_y = vectors[:2]
        move_vector: np.ndarray = np.array([translation_x, translation_y, 0])

        angle_x, angle_y = vectors[2:]

        moved_points: Points = PointsMover.move_on_vector(
            points=points,
            vector=move_vector,
        )
        # Rotate inner points by angle_x and angle_y
        return PointsRotator.rotate_on_angle_related_center(
            moved_points, angle_x=angle_x, angle_y=angle_y)
