import math
import numpy as np
from numpy import ndarray, floating

from src_1.utils import Logger
from src_1.base_structure_classes import Points, CoordinateLimits
from src_1.data_preparation import StructureSettings
from src_1.coordinate_operations import (
    DistanceMeasure,
    PointsFilter,
)

from src_1.projects.carbon_honeycomb_actions import CarbonHoneycombChannel
from .variance_calculator import VarianceCalculator


logger = Logger("AlAtomsFilter")


class InterAtomsFilter:
    @classmethod
    def get_filtered_atoms_atoms(
            cls,
            carbon_channel: CarbonHoneycombChannel,
            coordinates_atoms: Points,
            coordinates_atoms_prev: Points,
            max_atoms: int,
            min_dist_between_atoms_sum_prev: float,
            dist_and_rotation_variance_prev: float | floating,
    ) -> tuple[Points, float, float | floating, int]:

        # Prev values by default
        coordinates_atoms_result: Points = coordinates_atoms_prev
        min_dist_between_atoms_sum_result: float = min_dist_between_atoms_sum_prev
        dist_and_rotation_variance_result: float | floating = dist_and_rotation_variance_prev
        max_atoms_result: int = max_atoms

        atoms_filtered: Points = cls.filter_atoms_related_carbon(
            coordinates_atoms, carbon_channel)

        num_of_atoms: int = len(atoms_filtered)

        if num_of_atoms > max_atoms:
            coordinates_atoms_result = atoms_filtered
            max_atoms_result = len(coordinates_atoms_result)

            # Update min distances betweenintercalated atoms
            min_dist_between_atoms_sum_result = cls._calculate_min_dist_between_inter_atoms_sum(
                atoms_filtered)

            # Reset dist_and_rotation_variance
            dist_and_rotation_variance_result = 0

            if num_of_atoms > 1:
                logger.info(f"Number ofintercalated atoms: {num_of_atoms}")

                # Print average min distance betweenintercalated atoms
                ave_min_dist: float = round(min_dist_between_atoms_sum_result / max_atoms_result, 4)
                logger.info(f"Average min distance betweenintercalated atoms: {ave_min_dist}")

        elif num_of_atoms > 0 and num_of_atoms == max_atoms:

            # Calculate min distances betweenintercalated atoms
            current_min_dist: float = cls._calculate_min_dist_between_inter_atoms_sum(
                atoms_filtered)

            # The nearest atoms have priority
            if current_min_dist < min_dist_between_atoms_sum_prev:
                coordinates_atoms_result = atoms_filtered
                max_atoms_result = len(coordinates_atoms_result)
                min_dist_between_atoms_sum_result = current_min_dist

                # Print average min distance betweenintercalated atoms
                ave_min_dist: float = round(min_dist_between_atoms_sum_result / max_atoms_result, 4)
                logger.info(f"Average min distance betweenintercalated atoms: {ave_min_dist}")

                # Reset dist_and_rotation_variance
                dist_and_rotation_variance_result = 0

            else:
                # Check variance
                current_min_dist_sum: floating = DistanceMeasure.calculate_min_distance_sum(
                    atoms_filtered.points, carbon_channel.points)
                variance_related_channel: floating = VarianceCalculator.calculate_variance_related_channel(
                    atoms_filtered, carbon_channel)

                current_dist_and_rotation_variance: floating = current_min_dist_sum - variance_related_channel

                if current_dist_and_rotation_variance > dist_and_rotation_variance_prev:
                    coordinates_atoms_result = atoms_filtered
                    max_atoms_result = len(coordinates_atoms_result)
                    dist_and_rotation_variance_result = current_dist_and_rotation_variance

        return (
            coordinates_atoms_result,
            min_dist_between_atoms_sum_result,
            dist_and_rotation_variance_result,
            max_atoms_result,
        )

    @staticmethod
    def _calculate_min_dist_between_inter_atoms_sum(inter_points: Points) -> float:
        min_dist: ndarray = DistanceMeasure.calculate_min_distances_between_points(
            inter_points.points)
        return round(np.sum(min_dist), 4)

    @classmethod
    def filter_atoms_related_carbon(
            cls,
            inter_points: Points,
            carbon_channel: CarbonHoneycombChannel,
            # structure_settings: StructureSettings,
    ) -> Points:
        """Filter intercalated atoms related planes and then related carbon atoms."""

        inter_points_filtered: Points = cls.filter_atoms_related_clannel_planes(
            inter_points=inter_points,
            carbon_channel=carbon_channel,
            # distance_from_plane=structure_settings.distance_from_plane,
        )

        limits: CoordinateLimits = carbon_channel.coordinate_limits

        inter_points_filtered = PointsFilter.filter_by_min_max_z(
            points_to_filter=inter_points_filtered,
            z_min=limits.z_min,
            z_max=limits.z_max,
            move_align_z=True)

        return cls._filter_atoms_relates_carbon_atoms(
            inter_points=inter_points_filtered,
            carbon_points=carbon_channel,
            max_distance_to_carbon_atoms=0,
        )

    @staticmethod
    def filter_atoms_related_clannel_planes(
            inter_points: Points,
            carbon_channel: CarbonHoneycombChannel,
            distance_from_plane: float = 0,
    ) -> Points:
        """
        Filter points from coordinates array by planes
        (remove atoms that are outside channel and atoms inside that are closer than distance_from_plane param).
        """

        filtered_points: Points = inter_points.copy()
        carbon_channel_center: np.ndarray = carbon_channel.channel_center

        for plane in carbon_channel.planes:
            # Build plane parameters
            A, B, C, D = plane.plane_params

            direction: bool = plane.get_direction_to_center(carbon_channel_center)

            filtered_points = PointsFilter.filter_coordinates_related_to_plane(
                filtered_points,
                A, B, C, D,
                direction=direction,
                min_distance=distance_from_plane)

            # from src.structure_visualizer import StructureVisualizer
            # StructureVisualizer.show_two_structures(carbon_channel.points, filtered_points.points)

            if len(filtered_points) == 0:
                return filtered_points

        return filtered_points

    @staticmethod
    def _filter_atoms_relates_carbon_atoms(
        inter_points: Points,
        carbon_points: Points,
        max_distance_to_carbon_atoms: float,
    ) -> Points:
        """
        Filter points from the inter_points array
        by the max distance (max_distance_to_carbon_atoms param)
        to the points in the carbon_points array.
        """

        # Find the minimum distance for each atom in coordinates_atoms to any atom in coordinates_carbon
        min_distances: np.ndarray = DistanceMeasure.calculate_min_distances(
            inter_points.points, carbon_points.points
        )

        filtered_atoms_coordinates: Points = Points(
            points=inter_points.points[min_distances >= max_distance_to_carbon_atoms]
        )

        return filtered_atoms_coordinates
