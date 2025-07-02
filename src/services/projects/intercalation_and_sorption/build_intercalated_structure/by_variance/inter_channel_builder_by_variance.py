import math
from pathlib import Path

import numpy as np
# from scipy.spatial.distance import cdist
# from scipy.optimize import minimize

from src.interfaces import ICarbonHoneycombChannel, IPoints
from src.services import Logger, PointsRotator, execution_time_logger
from src.entities import Points

from .inter_atoms_filter import InterAtomsFilter
from .inter_atoms_setter import InterAtomsSetter


logger = Logger("IntercalatedChannelBuilder")


class InterChannelBuilderByVariance:
    @classmethod
    def build_inter_atoms_in_carbon(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            coordinates_inter_atoms: IPoints,
            lattice_param: float,
            to_filter_inter_atoms: bool = True,
            equidistant_inter_atoms: bool = True
    ) -> IPoints:
        """ Returns coordinates_al """

        if to_filter_inter_atoms:
            coordinates_inter_atoms_filtered: IPoints = cls.find_max_filtered_atoms(
                carbon_channel=carbon_channel,
                coordinates_inter_atoms=coordinates_inter_atoms,
                lattice_param=lattice_param)

            if equidistant_inter_atoms:
                # Set intercalated atoms maximally equidistant from the channel atoms
                coordinates_inter_atoms_filtered: IPoints = InterAtomsSetter.equidistant_points_sets_in_channel(
                    carbon_channel=carbon_channel,
                    inner_points=coordinates_inter_atoms_filtered)

            return coordinates_inter_atoms_filtered

        logger.info("Build intercalated atoms in the channel without filtering.")
        return coordinates_inter_atoms

    @classmethod
    @execution_time_logger
    def find_max_filtered_atoms(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            coordinates_inter_atoms: IPoints,
            lattice_param: float,
    ) -> IPoints:
        """
        Parallel move, rotate and filter intercalated atoms related carbon atoms
        to find the option with the maximumintercalated atoms after filtering.
        """

        max_atoms: int = 0
        min_dist_between_atoms_sum: float = np.inf
        dist_and_rotation_variance: float | np.floating = 0

        coordinates_atoms_result: IPoints = Points(points=np.array([]))

        step_to_move: float = lattice_param / 25
        range_to_move: np.ndarray = np.arange(0, lattice_param, step_to_move)

        step_to_rotate: float = math.pi / 45
        angle_range_to_rotate: np.ndarray = np.arange(0, math.pi / 3, step_to_rotate)

        for step_x in range_to_move:
            moved_x_coordinates: IPoints = coordinates_inter_atoms.copy()
            moved_x_coordinates.points[:, 0] += step_x

            for step_y in range_to_move:
                moved_xy_coordinates: IPoints = moved_x_coordinates.copy()
                moved_xy_coordinates.points[:, 1] += step_y

                for angle_x in angle_range_to_rotate:
                    x_rotaded_coordinates: IPoints = PointsRotator.rotate_on_angle_related_center(
                        moved_xy_coordinates.copy(), angle_x=angle_x)

                    for angle_y in angle_range_to_rotate:
                        xy_rotaded_coordinates: IPoints = PointsRotator.rotate_on_angle_related_center(
                            x_rotaded_coordinates.copy(), angle_y=angle_y)

                        for angle_z in angle_range_to_rotate:
                            xyz_rotaded_coordinates: IPoints = PointsRotator.rotate_on_angle_related_center(
                                xy_rotaded_coordinates.copy(), angle_z=angle_z)

                            result: tuple = InterAtomsFilter.get_filtered_atoms_atoms(
                                carbon_channel=carbon_channel,
                                coordinates_atoms=xyz_rotaded_coordinates,
                                coordinates_atoms_prev=coordinates_atoms_result,
                                max_atoms=max_atoms,
                                min_dist_between_atoms_sum_prev=min_dist_between_atoms_sum,
                                dist_and_rotation_variance_prev=dist_and_rotation_variance,
                            )

                            coordinates_atoms_result = result[0]
                            min_dist_between_atoms_sum = result[1]
                            dist_and_rotation_variance = result[2]
                            max_atoms = result[3]

        return coordinates_atoms_result
