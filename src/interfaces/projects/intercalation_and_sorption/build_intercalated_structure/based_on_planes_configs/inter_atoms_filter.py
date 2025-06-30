import numpy as np

from src_1.utils import Logger, execution_time_logger, ConstantsAtomParams
from src_1.base_structure_classes import Points
from src_1.coordinate_operations import DistanceMeasure


logger = Logger("AtomsFilter")


class InterAtomsFilter:
    @classmethod
    # @execution_time_logger
    def replace_nearby_atoms_with_one_atom(
            cls,
            inter_atoms: Points,
            atom_params: ConstantsAtomParams,
    ) -> Points:
        """
        If there are 2 or more atoms have the distance between them less than dist_between_atoms / 3
        replace these atoms with one that places on the center between the replaced group.

        Returnes the updated inter_atoms (with replaced atoms).
        """

        dist_matrix: np.ndarray = DistanceMeasure.calculate_dist_matrix(inter_atoms.points)

        min_allowed_dist: float = atom_params.DIST_TO_REPLACE_NEARBY_ATOMS

        # Keep track of groups of atoms to merge
        merged_indices = set()
        points_upd: list[np.ndarray] = []

        # Iterate through each atom
        for i, point in enumerate(inter_atoms.points):
            if i in merged_indices:
                continue  # Skip atoms that are already merged

            # Find atoms within the min_allowed_dist
            close_atoms: np.ndarray = np.where(dist_matrix[i] < min_allowed_dist)[0]

            # Merge these atoms if some close atoms are found
            if len(close_atoms) > 0:
                close_atoms = np.concatenate((close_atoms, [i]))
                merged_indices.update(close_atoms)

                # Calculate the center of the group
                group_center: np.ndarray = inter_atoms.points[close_atoms].mean(axis=0)
                points_upd.append(group_center)
            else:
                # Keep this atom as is if no nearby atoms are found
                points_upd.append(point)

        inter_atoms_upd = Points(points=np.array(points_upd))
        dist_matrix_upd: np.ndarray = DistanceMeasure.calculate_dist_matrix(inter_atoms_upd.points)

        if np.any(dist_matrix_upd < min_allowed_dist):
            # Run replacement one more time
            return cls.replace_nearby_atoms_with_one_atom(
                inter_atoms_upd, atom_params)

        return inter_atoms_upd

    @staticmethod
    @execution_time_logger
    def remove_too_close_atoms(
            inter_atoms: Points,
            atom_params: ConstantsAtomParams,
    ) -> Points:
        """
        If there are 2 or more atoms have the distance between them less allowed
        keep only one atom and remove the rest.

        Returnes the updated inter_atoms (with removed atoms).
        """

        min_allowed_dist: float = atom_params.MIN_ALLOWED_DIST_BETWEEN_ATOMS

        dist_matrix: np.ndarray = DistanceMeasure.calculate_dist_matrix(inter_atoms.points)
        # min_dists: np.ndarray = np.min(dist_matrix, axis=1)

        # Keep track of groups of atoms to merge
        merged_indices = set()
        points_upd: list[np.ndarray] = []

        # Iterate through each atom
        for i, point in enumerate(inter_atoms.points):
            if i in merged_indices:
                continue  # Skip atoms that are already merged

            points_upd.append(point)

            # Find atoms within the min_allowed_dist
            close_atoms: np.ndarray = np.where(dist_matrix[i] < min_allowed_dist)[0]

            # Skip too close atoms some close atoms are found
            if len(close_atoms) > 0:
                close_atoms = np.concatenate((close_atoms, [i]))
                merged_indices.update(close_atoms)

        return Points(points=np.array(points_upd))

    @classmethod
    # @execution_time_logger
    def remove_some_close_atoms(
            cls,
            inter_atoms: Points,
            min_dist: float,
            max_neighbours: int = -1,
            num_of_points_to_skip: int = 0,

            # inner params
            percent_to_remove: float = 1,
            init_amount: int = 0,
            removed_amount: int = 0,
    ) -> tuple[Points, int]:
        """
        Works recursively:
        1. Sort atoms by the biggest num of close neighbours and the min ave dist (if there are no such atoms - return the initial inter_atoms)
        2. Take the indexes of the atoms with the biggest num of close neighbours
        3. Iterate through each atom index
            3.1. Delete atom with provided index (=0 by default)
            3.2. Run the recursive function
            3.3. If the returned number of atoms bigger than the previous one - save the result
        4. Return the best result (with the biggest number of atoms)

        Returnes the updated inter_atoms (with removed atoms).
        """

        if percent_to_remove < 1 and init_amount == 0:
            init_amount = len(inter_atoms)

        dist_matrix: np.ndarray = DistanceMeasure.calculate_dist_matrix(inter_atoms.points)

        # Create a mask for values less than `min_dist`
        mask: np.ndarray = dist_matrix < min_dist

        # Replace values not satisfying the condition with `NaN`
        filtered_matrix: np.ndarray = np.where(mask, dist_matrix, np.nan)

        num_of_too_close_neighbours: np.ndarray = np.sum(~np.isnan(filtered_matrix), axis=1)

        if np.all(num_of_too_close_neighbours == 0):
            return inter_atoms, max_neighbours

        # Get the first max_neighbours
        if max_neighbours == -1:
            max_neighbours = np.max(num_of_too_close_neighbours)

        # Sort atoms by the biggest num of close neighbours and the min ave dist
        max_neighbour_indices = np.where(num_of_too_close_neighbours >= max_neighbours)[0]

        if len(max_neighbour_indices) == 0:
            return inter_atoms, max_neighbours

        if num_of_points_to_skip >= len(max_neighbour_indices):
            num_of_points_to_skip = len(max_neighbour_indices) - 1

        # try:
        new_points: np.ndarray = np.delete(inter_atoms.points, max_neighbour_indices[num_of_points_to_skip], axis=0)
        # except IndexError:
        #     pass

        new_inter_atoms = Points(points=new_points)

        if percent_to_remove < 1:
            removed_amount += 1
            if removed_amount > init_amount * percent_to_remove:
                return new_inter_atoms, max_neighbours

        result_points, max_neighbours = cls.remove_some_close_atoms(
            new_inter_atoms, min_dist, max_neighbours,

            percent_to_remove=percent_to_remove,
            init_amount=init_amount,
            removed_amount=removed_amount,
        )

        return result_points, max_neighbours
