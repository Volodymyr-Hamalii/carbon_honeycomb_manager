import numpy as np
from scipy.optimize import minimize

from src_1.utils import Logger, ConstantsAtomParams
from src_1.base_structure_classes import Points
from src_1.coordinate_operations import (
    PointsOrganizer,
    PointsRotator,
    PointsMover,
    DistanceMeasure,
)
from src_1.projects.carbon_honeycomb_actions import (
    CarbonHoneycombChannel,
    CarbonHoneycombPlane,
    CarbonHoneycombUtils,
)
# from src.structure_visualizer import StructureVisualizer

from ..based_on_planes_configs import InterAtomsFilter


logger = Logger("AlAtomsTranslator")


class InterAtomsTranslator:
    @classmethod
    def translate_for_all_channels(
        cls,
        coordinates_carbon: Points,
        carbon_channels: list[CarbonHoneycombChannel],
        inter_atoms_channel_coordinates: Points,
    ) -> Points:

        inter_atoms: np.ndarray = inter_atoms_channel_coordinates.points
        inter_atoms_fininter_atoms: np.ndarray = inter_atoms.copy()

        # inter_atoms_center: np.ndarray = inter_atoms_channel_coordinates.center
        inter_atoms_center: np.ndarray = carbon_channels[0].center

        for carbon_channel in carbon_channels[1:]:
            # Check that it's not the channel for which we have already translated atoms
            channel_center: np.ndarray = carbon_channel.center
            # if np.linalg.norm(channel_center - al_center) < 1:
            #     continue
            # Copy the Z coordinate from the inter_atoms_center
            channel_center[2] = inter_atoms_center[2]

            # Translate on the vector from the channel center to the inter_atoms center
            vector: np.ndarray = channel_center - inter_atoms_center
            inter_atoms_fininter_atoms = np.vstack(
                (inter_atoms_fininter_atoms, inter_atoms.copy() + vector))

        edge_channel_centers: list[np.ndarray] = cls._get_centers_of_edge_carbon_channels(coordinates_carbon)

        logger.info(f"CHECK THE Z COORDINATES OF THE EDGE CHANNELS: {inter_atoms_center}, {edge_channel_centers}")

        for center in edge_channel_centers:
            # Copy the Z coordinate from the inter_atoms_center
            center[2] = inter_atoms_center[2]

            vector: np.ndarray = center - inter_atoms_center
            inter_atoms_fininter_atoms = np.vstack(
                (inter_atoms_fininter_atoms, inter_atoms.copy() + vector))

        return Points(inter_atoms_fininter_atoms)

    @classmethod
    def translate_for_all_planes(
        cls,
        carbon_channel: CarbonHoneycombChannel,
        inter_atoms_plane_coordinates: Points,
        number_of_planes: int,
        to_try_to_reflect_inter_atoms: bool,
        atom_params: ConstantsAtomParams,
    ) -> Points:

        planes: list[CarbonHoneycombPlane] = carbon_channel.planes[:number_of_planes]

        # al_groups: list[np.ndarray] = cls._group_by_lines(al_plane_coordinates)
        plane_group_map: dict[int, np.ndarray] = cls._match_plane_with_group(
            inter_atoms_plane_coordinates, planes)

        all_inter_atoms_points: Points = cls._copy_inter_atoms_points_to_rest_planes(
            plane_group_map, carbon_channel, to_try_to_reflect_inter_atoms, atom_params)

        inter_atoms_points_upd: Points = InterAtomsFilter.replace_nearby_atoms_with_one_atom(
            all_inter_atoms_points, atom_params)

        return inter_atoms_points_upd

    @staticmethod
    def _match_plane_with_group(
        inter_atoms_plane_coordinates: Points,
        planes: list[CarbonHoneycombPlane],
    ) -> dict[int, np.ndarray]:
        """ Returns the dict with the plane index and corresponding intercalated atomspoints. """

        plane_group_map: dict[int, list[np.ndarray]] = {
            plane_i: [] for plane_i in range(len(planes))
        }

        for atom in inter_atoms_plane_coordinates.points:
            min_dist: float = np.inf
            plane_indexes: list[int] = []

            for plane_i, plane in enumerate(planes):
                min_distances: np.ndarray = DistanceMeasure.calculate_min_distances(np.array([atom]), plane.points)
                min_dist_plane: float = round(min(min_distances), 2)

                if min_dist_plane < min_dist:
                    min_dist: float = min_dist_plane
                    plane_indexes = [plane_i]

                elif min_dist == min_dist_plane:
                    plane_indexes.append(plane_i)

            for plane_i in plane_indexes:
                plane_group_map[plane_i].append(atom)

        # Filter plane groups with the max length
        plane_group_map = {
            key: value
            for key, value in plane_group_map.items()
            # if len(value) == max_len
            if value
        }

        return {
            key: np.array(value)
            for key, value
            in plane_group_map.items()
        }

    @classmethod
    def _copy_inter_atoms_points_to_rest_planes(
            cls,
            plane_group_map: dict[int, np.ndarray],
            carbon_channel: CarbonHoneycombChannel,
            to_try_to_reflect_inter_atoms: bool,
            atom_params: ConstantsAtomParams,
    ) -> Points:
        planes: list[CarbonHoneycombPlane] = carbon_channel.planes
        # channel_center: np.ndarray = carbon_channel.center
        all_inter_atoms_points: list[np.ndarray] = []
        min_allowed_dist: float = atom_params.MIN_ALLOWED_DIST_BETWEEN_ATOMS

        for plane_i, plane in enumerate(planes):
            if plane_i in plane_group_map:
                # Just add the related points
                all_inter_atoms_points.append(plane_group_map[plane_i])

                # Update the minimum allowed distance according to the built plane
                # (take 95% of the minimum distance for some margin)
                min_dist: float = np.min(
                    DistanceMeasure.calculate_min_distances(
                        plane_group_map[plane_i], plane.points
                    )
                )
                if min_dist * 0.98 < min_allowed_dist:
                    min_allowed_dist = min_dist
                    logger.warning(
                        "Min allowed distance betweenintercalated atoms and C atoms "
                        f"is less than {atom_params.DIST_BETWEEN_ATOMS:.2f}: {min_allowed_dist:.2f}"
                    )

            # Get the index of the related plane
            group_i: int = plane_i % len(plane_group_map)

            if group_i not in plane_group_map:
                logger.warning(f"Group {group_i} not found in plane_group_map ({plane_group_map.keys()})")
                continue

            inter_atoms_points = Points(plane_group_map[group_i])
            # inter_atoms_points_moved: Points = cls._move_inter_atoms_to_other_plane(
            #     inter_atoms_points, channel_center,
            #     inter_atoms_points_plane=planes[group_i],
            #     target_plane=plane,
            # )

            # all_inter_atoms.append(inter_atoms_moved.points)
            # continue

            angle: float = (group_i - plane_i) * np.pi / 3
            # logger.info(f"Angle: {angle / np.pi * 180} degrees")

            inter_atoms_points_rotated: Points = PointsRotator.rotate_around_z_parallel_line(
                inter_atoms_points, line_point=carbon_channel.center, angle=angle)

            # StructureVisualizer.show_two_structures(
            #     carbon_channel.points,
            #     np.concatenate(all_inter_atoms_points + [inter_atoms_points_rotated.points]),
            #     title=f"Plane {plane_i}",
            #     to_build_bonds=True
            # )

            # all_inter_atoms_points.append(inter_atoms_points_rotated.points)
            # continue

            # inter_atoms_adjusted: Points = cls._adjust_inter_atoms(inter_atoms_rotated, plane)

            if to_try_to_reflect_inter_atoms:
                # Check if we need to reflect points
                inter_atoms_points_reflected: Points = PointsMover.reflect_through_vertical_axis(
                    inter_atoms_points_rotated)

                reflected_min_dists: np.ndarray = DistanceMeasure.calculate_min_distances(
                    inter_atoms_points_reflected.points, plane.points)
                rotated_min_dists: np.ndarray = DistanceMeasure.calculate_min_distances(
                    inter_atoms_points_rotated.points, plane.points)

                if np.min(reflected_min_dists) > min_allowed_dist and (
                        np.sum(reflected_min_dists) > np.sum(rotated_min_dists)):
                    all_inter_atoms_points.append(inter_atoms_points_reflected.points)
                else:
                    all_inter_atoms_points.append(inter_atoms_points_rotated.points)

            else:
                all_inter_atoms_points.append(inter_atoms_points_rotated.points)

        inter_atoms_points_ndarray: np.ndarray = np.concatenate(all_inter_atoms_points)
        return Points(inter_atoms_points_ndarray)

    @staticmethod
    def _move_inter_atoms_to_other_plane(
        inter_atoms_points: Points,
        channel_center: np.ndarray,
        inter_atoms_points_plane: CarbonHoneycombPlane,
        target_plane: CarbonHoneycombPlane,
    ) -> Points:
        """
        It does 3 steps:
        1) move inter_atoms from inter_atoms center to the center of the inter_atoms_plane,
        2) move inter_atoms from 1) step point to target_plane center,
        3) move inter_atoms from 2) step point in the direction to the channel_center on the distance,
        that equals length of the vector from 1) step (to keep the same distance betweenintercalated atoms and plane).
        """

        # Step 1: Move intercalated atoms to `inter_atoms_plane` center
        vector_1: np.ndarray = inter_atoms_points_plane.center - inter_atoms_points.center
        dist_from_plane: np.floating = np.linalg.norm(vector_1)

        # Step 2: Move from `inter_atoms_points_plane.center` to `target_plane.center`
        vector_2: np.ndarray = target_plane.center - inter_atoms_points_plane.center

        # Step 3: Move in the direction of `channel_center` to maintain distance
        direction_vector = channel_center - target_plane.center

        # Compute length and normalize direction vector
        direction_length: np.floating = np.linalg.norm(direction_vector)
        if direction_length == 0:
            return Points(points=inter_atoms_points.points + vector_1 + vector_2)  # No need to move further

        unit_direction = direction_vector / direction_length
        scaled_vector = unit_direction * dist_from_plane  # Keep the same distance

        # Compute final transformed points
        transformed_points: np.ndarray = inter_atoms_points.points + vector_1 + vector_2 + scaled_vector

        return Points(points=transformed_points)

    @classmethod
    def _adjust_inter_atoms(
        cls,
        inter_atoms_points: Points,
        plane: CarbonHoneycombPlane,
    ) -> Points:
        """
        Rotate a bit to find the min distance variation 
        between inter_atoms points and the plane. 
        """
        init_angle: np.ndarray = np.array([0.0])

        result = minimize(
            cls._func_to_minimize,
            init_angle,
            args=(inter_atoms_points, plane),
            method="Powell",
            options={"disp": True},
        )

        result_angle: float = result.x.item()

        rotated_points: Points = PointsRotator.rotate_on_angle_related_center(
            inter_atoms_points, angle_z=result_angle)

        return rotated_points

    @staticmethod
    def _func_to_minimize(
        angle_z: np.ndarray,
        inter_atoms_points: Points,
        plane: CarbonHoneycombPlane,
    ) -> np.floating:
        rotated_points: Points = PointsRotator.rotate_on_angle_related_center(
            inter_atoms_points, angle_z=angle_z[0])

        min_dists: np.ndarray = DistanceMeasure.calculate_min_distances(
            rotated_points.points, plane.points)

        var_result: np.floating = np.var(min_dists)

        if np.any(min_dists < 1.0):
            # Avoid situations whenintercalated atoms are too close to the plane
            return var_result * 10

        return var_result

    @staticmethod
    def _get_centers_of_edge_carbon_channels(
        coordinates_carbon: Points,
    ) -> list[np.ndarray]:
        """ 
        Takes the lines with the pointns with the same Y coordinate, 
        takes left and right (with the min and max X coordinate) parallel segments from the lines
        and returns the centers of the segment pairs.
        """

        # Get the lines with the points with the same Y coordinate
        groups_by_the_xy_lines: list[dict[tuple[np.float32, np.float32], np.ndarray]] = PointsOrganizer.group_by_the_xy_lines(
            PointsOrganizer.group_by_unique_xy(coordinates_carbon.points), epsilon=1e-1, min_points_in_line=3)

        honeycomb_planes_groups: list[
            dict[tuple[np.float32, np.float32], np.ndarray]
        ] = CarbonHoneycombUtils.split_xy_groups_by_max_distances(
            groups_by_the_xy_lines, max_distance_between_xy_groups=3)

        # Filter honeycomb_planes_groups groups with the same Y in the group
        honeycomb_planes_groups = [
            group for group in honeycomb_planes_groups
            if list(group.keys())[0][1] == list(group.keys())[1][1]
        ]

        # Keep only planes, that contains max or min X coordinate along the all groups
        max_x: np.floating = max(
            subgroup[0]
            for group in honeycomb_planes_groups
            for subgroup in group.keys()
        )
        min_x: np.floating = min(
            subgroup[0]
            for group in honeycomb_planes_groups
            for subgroup in group.keys()
        )

        honeycomb_planes_groups_left = [
            group for group in honeycomb_planes_groups
            if any(key[0] in [min_x] for key in group.keys())
        ]

        honeycomb_planes_groups_right = [
            group for group in honeycomb_planes_groups
            if any(key[0] in [max_x] for key in group.keys())
        ]

        honeycomb_planes_groups_left_coordinates = [
            point for group in honeycomb_planes_groups_left
            for point in group.values()
        ]

        honeycomb_planes_groups_right_coordinates = [
            point for group in honeycomb_planes_groups_right
            for point in group.values()
        ]

        left_centers = np.mean(np.concatenate(honeycomb_planes_groups_left_coordinates), axis=0)
        right_centers = np.mean(np.concatenate(honeycomb_planes_groups_right_coordinates), axis=0)

        return [left_centers, right_centers]
