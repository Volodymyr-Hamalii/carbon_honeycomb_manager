import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import cdist

from src.interfaces import ICarbonHoneycombChannel, IPoints
from src.services.utils import ConstantsAtomParams, Logger
from src.entities import Points
from src.services import PointsMover, DistanceMeasurer
from ..by_variance import (
    InterAtomsFilter,
)

logger = Logger("FullChannelBuilder")


class FullChannelBuilder:
    @classmethod
    def build_full_channel(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            channel_planes_coordinates: IPoints,
            inter_atoms_bulk: IPoints,
            atom_params: ConstantsAtomParams,
    ) -> IPoints:

        inter_atoms_bulk = InterAtomsFilter.filter_atoms_related_clannel_planes(
            inter_points=inter_atoms_bulk,
            carbon_channel=carbon_channel,
            distance_from_plane=atom_params.MIN_ALLOWED_DIST_BETWEEN_ATOMS,
        )

        inter_atoms_bulk = cls._find_optimal_positions_for_inter_atoms(
            inter_atoms_bulk=inter_atoms_bulk,
            channel_planes_coordinates=channel_planes_coordinates,
            atom_params=atom_params,
        )

        inter_atoms_bulk = cls._adjust_the_closest_inter_atoms(
            inter_atoms_bulk=inter_atoms_bulk,
            channel_planes_coordinates=channel_planes_coordinates,
            atom_params=atom_params,
        )

        logger.info(f"Intercalated atoms bulk atoms added: {len(inter_atoms_bulk.points)}")

        return Points(
            points=np.vstack([channel_planes_coordinates.points, inter_atoms_bulk.points])
        )

    @staticmethod
    def _filter_related_plane_inter_atoms(
        inter_atoms_bulk: IPoints,
        channel_planes_coordinates: IPoints,
        atom_params: ConstantsAtomParams,
    ) -> IPoints:
        # Find the minimum distance for each atom in coordinates_al to any atom in coordinates_carbon
        min_distances: np.ndarray = DistanceMeasurer.calculate_min_distances(
            inter_atoms_bulk.points, channel_planes_coordinates.points
        )

        filtered_inter_atoms_coordinates: Points = Points(
            points=inter_atoms_bulk.points[min_distances >= atom_params.MIN_RECOMENDED_DIST_BETWEEN_ATOMS]
        )

        return filtered_inter_atoms_coordinates

    @classmethod
    def _find_optimal_positions_for_inter_atoms(
        cls,
        inter_atoms_bulk: IPoints,
        channel_planes_coordinates: IPoints,
        atom_params: ConstantsAtomParams,
    ) -> IPoints:
        init_vector: np.ndarray = np.array([0.0, 0.0])

        result = minimize(
            cls._objective_function,
            init_vector,
            args=(inter_atoms_bulk, channel_planes_coordinates, atom_params),
            method="BFGS",
            options={"disp": True}
        )

        vector_to_move: np.ndarray = result.x

        if len(vector_to_move) == 2:
            vector_to_move = np.append(vector_to_move, 0.0)

        inter_atoms_bulk = PointsMover.move_on_vector(
            points=inter_atoms_bulk,
            vector=vector_to_move,
        )

        inter_atoms_bulk = cls._filter_related_plane_inter_atoms(
            inter_atoms_bulk=inter_atoms_bulk,
            channel_planes_coordinates=channel_planes_coordinates,
            atom_params=atom_params,
        )

        return inter_atoms_bulk

    @classmethod
    def _objective_function(
        cls,
        vector_to_move: np.ndarray,
        inter_atoms_bulk: IPoints,
        channel_planes_coordinates: IPoints,
        atom_params: ConstantsAtomParams,
    ) -> float | np.floating:

        if len(vector_to_move) == 2:
            vector_to_move = np.append(vector_to_move, 0.0)

        moved_inter_atoms: IPoints = PointsMover.move_on_vector(
            points=inter_atoms_bulk,
            vector=vector_to_move,
        )

        # filtered_inter_atoms: Points = cls._filter_related_plane_inter_atoms(
        #     inter_atoms_bulk=moved_inter_atoms,
        #     channel_planes_coordinates=channel_planes_coordinates,
        #     atom_params=atom_params,
        # )

        if len(moved_inter_atoms.points) == 0:
            return np.inf

        # Calculate the maximum possible number of atoms (before filtering)
        max_possible_atoms: int = len(inter_atoms_bulk.points)

        # Calculate atom count penalty (increases as we lose more atoms)
        atoms_penalty: float = ((max_possible_atoms - len(moved_inter_atoms.points)) / max_possible_atoms) ** 2

        # Calculate distance variance as before
        min_dists_var: np.floating = cls._calculate_min_dists_var(
            moved_inter_atoms, channel_planes_coordinates
        )

        # Combine penalties with appropriate weights
        # The atom count penalty is dominant (multiplied by 1000)
        # The distance variance is secondary (multiplied by 1)
        return 1000 * atoms_penalty + min_dists_var

    @staticmethod
    def _calculate_min_dists_var(
        points_1: IPoints,
        points_2: IPoints,
    ) -> np.floating:
        min_distances: np.ndarray = DistanceMeasurer.calculate_min_distances(
            points_1.points, points_2.points)

        return np.var(min_distances)

    @staticmethod
    def _adjust_the_closest_inter_atoms(
        inter_atoms_bulk: IPoints,
        channel_planes_coordinates: IPoints,
        atom_params: ConstantsAtomParams,
    ) -> IPoints:
        """
        Check distances between atoms in inter_atoms_bulk and channel_planes_coordinates.
        If the distance is less than Constants.phys.al.DIST_BETWEEN_ATOMS,
        get 3 the closest atoms in inter_atoms_bulk and all atoms in channel_planes_coordinates
        that are closer than Constants.phys.al.DIST_BETWEEN_ATOMS and move the atom to the center of these atoms.
        """
        min_dists: np.ndarray = DistanceMeasurer.calculate_min_distances(
            inter_atoms_bulk.points, channel_planes_coordinates.points
        )

        counter: int = 0

        for i in range(len(min_dists)):
            if min_dists[i] < atom_params.DIST_BETWEEN_ATOMS:
                dists_plane_bulk: np.ndarray = cdist(inter_atoms_bulk.points, channel_planes_coordinates.points)
                dists_bulk: np.ndarray = DistanceMeasurer.calculate_dist_matrix(inter_atoms_bulk.points)

                # Get the closest atoms from the plane
                closest_atoms_from_plane: np.ndarray = channel_planes_coordinates.points[
                    dists_plane_bulk[i] < atom_params.DIST_BETWEEN_ATOMS * 1.01]

                # Get the closest atoms from the bulk
                closest_atoms_from_bulk: np.ndarray = inter_atoms_bulk.points[
                    dists_bulk[i] < atom_params.DIST_BETWEEN_ATOMS * 1.01]

                if len(closest_atoms_from_plane) == 0 or len(closest_atoms_from_bulk) == 0:
                    continue

                adjusted_atom: np.ndarray = np.mean(
                    np.vstack([closest_atoms_from_plane, closest_atoms_from_bulk]), axis=0)

                inter_atoms_bulk.points[i] = adjusted_atom
                counter += 1

        logger.info(f"Adjusted {counter} atoms.")

        return inter_atoms_bulk
