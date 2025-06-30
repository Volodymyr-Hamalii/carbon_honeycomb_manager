
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import minimize_scalar, OptimizeResult

from src_1.utils import ConstantsAtomParams, Logger, execution_time_logger
# from src.coordinate_operations import DistanceMeasure
from src_1.base_structure_classes import Points, FlatFigure
from src_1.projects.carbon_honeycomb_actions import CarbonHoneycombChannel, CarbonHoneycombPlane


logger = Logger("AtomsBuilder")


class InterAtomsBuilder:
    @classmethod
    def build_inter_atoms_near_planes(
            cls,
            carbon_channel: CarbonHoneycombChannel,
            atom_params: ConstantsAtomParams,
            planes_limit: int | None = None,
    ) -> Points:
        """
        Build intercalated atoms near the carbon honeycomb planes (opposite polygons and holes on the planes).
        There is no any atoms filtering or cheching the distance between intercalated atoms
        (that will be done during the following steps).
        """

        inter_atoms: list[np.ndarray] = []
        carbon_channel_center: np.ndarray = carbon_channel.channel_center

        # Calculate the average distance between intercalated and C atoms
        dist_between_carbon_atoms: float = float(carbon_channel.ave_dist_between_closest_atoms)
        distance_from_carbon_atoms: float = (atom_params.DIST_BETWEEN_ATOMS + dist_between_carbon_atoms) / 2

        for i, plane in enumerate(carbon_channel.planes):  # To build only part of the planes

            if planes_limit is not None and i == planes_limit:
                # To build only part of the planes
                break

            # for plane in carbon_channel.planes:
            plane_inter_atoms: list[np.ndarray] = cls._build_inter_atoms_near_polygons(
                polygons=plane.hexagons,  # type: ignore
                carbon_channel_center=carbon_channel_center,
                distance_from_carbon_atoms=distance_from_carbon_atoms,
            )
            inter_atoms.extend(plane_inter_atoms)

            plane_inter_atoms: list[np.ndarray] = cls._build_inter_atoms_near_polygons(
                polygons=plane.pentagons,  # type: ignore
                carbon_channel_center=carbon_channel_center,
                distance_from_carbon_atoms=distance_from_carbon_atoms,
            )
            inter_atoms.extend(plane_inter_atoms)

            intercalated_atoms_near_edges: list[np.ndarray] = cls._build_inter_atoms_near_edges(
                plane=plane,
                carbon_channel_center=carbon_channel_center,
                distance_from_carbon_atoms=distance_from_carbon_atoms,
            )
            inter_atoms.extend(intercalated_atoms_near_edges)

        return Points(points=np.array(inter_atoms))

    @classmethod
    def _build_inter_atoms_near_polygons(
            cls,
            polygons: list[FlatFigure],
            carbon_channel_center: np.ndarray,
            distance_from_carbon_atoms: float,
    ) -> list[np.ndarray]:
        plane_inter_atoms: list[np.ndarray] = []
        for polygon in polygons:
            intercalated_atom: np.ndarray = cls._build_inter_atom_near_polygon(
                polygon, carbon_channel_center, distance_from_carbon_atoms)
            plane_inter_atoms.append(intercalated_atom)
        return plane_inter_atoms

    @staticmethod
    def _build_inter_atom_near_polygon(
        polygon: FlatFigure,
        carbon_channel_center: np.ndarray,
        distance_from_carbon_atoms: float,
    ) -> np.ndarray:
        """
        Calculate the intercalated atom coordinates near the polygon such that the
        average distance between the intercalated atom and polygon.points equals
        distance_from_carbon_atoms. Return the position closest to the polygon_center.
        """

        # Get polygon properties
        polygon_center: np.ndarray = polygon.center
        plane_params: tuple[float, float, float, float] = polygon.plane_params  # A, B, C, D

        normal_vector: np.ndarray = np.array(plane_params[:3])  # The normal vector to the polygon's plane

        # Normalize the normal vector
        normal_vector = normal_vector / np.linalg.norm(normal_vector)

        # Calculate the average dist from center to vertex
        dists_from_center_to_vertex: np.ndarray = cdist(polygon.points, [polygon_center])
        dist_from_center_to_point: np.floating = np.average(dists_from_center_to_vertex)

        # Calculate dist_from_polygon_center by Pythagorean theorem
        dist_from_polygon_center: float = np.sqrt(distance_from_carbon_atoms**2 - dist_from_center_to_point**2)

        # Calculate two candidate positions for the intercalated atom
        intercalated_candidate1: np.ndarray = polygon_center + normal_vector * dist_from_polygon_center
        intercalated_candidate2: np.ndarray = polygon_center - normal_vector * dist_from_polygon_center

        # Choose the candidate that is closer to carbon_channel_center (inside channel)
        if np.sum(np.abs(intercalated_candidate1 - carbon_channel_center)) < np.sum(np.abs(intercalated_candidate2 - carbon_channel_center)):
            return intercalated_candidate1
        else:
            return intercalated_candidate2

    @classmethod
    def _build_inter_atoms_near_edges(
        cls,
        plane: CarbonHoneycombPlane,
        carbon_channel_center: np.ndarray,
        distance_from_carbon_atoms: float,
    ) -> list[np.ndarray]:
        """ Build intercalated atoms opposite the edge holes. """

        edge_holes: np.ndarray = plane.edge_holes
        intercalated_atoms: list[np.ndarray] = []

        for hole_point in edge_holes:
            point_for_line: np.ndarray = np.array([
                carbon_channel_center[0],
                carbon_channel_center[1],
                hole_point[2]
            ])

            points_around_hole: np.ndarray = cls._find_the_points_around_hole(
                plane_points=plane.points, hole_point=hole_point)

            # Vector from hole_point to point_for_line
            line_vector: np.ndarray = point_for_line - hole_point
            line_length: np.floating = np.linalg.norm(line_vector)

            # Normalize the line vector
            line_unit_vector: np.ndarray = line_vector / line_length

            # Find the intercalated atom coordinates
            def objective_func(t) -> np.floating:
                candidate_point: np.ndarray = hole_point + t * line_unit_vector
                distances: np.ndarray = np.linalg.norm(points_around_hole - candidate_point, axis=1)
                return abs(np.mean(distances) - distance_from_carbon_atoms)

            # Optimize t to find the intercalated_atom
            result: OptimizeResult = minimize_scalar(
                objective_func,
                bounds=(0, line_length),
                method='bounded',
            )  # type: ignore
            t_optimal: np.ndarray = result.x

            # Compute the optimal intercalated atom position
            intercalated_atom: np.ndarray = hole_point + t_optimal * line_unit_vector

            # matrix = cdist(plane.points, [intercalated_atom])
            # matrix = matrix[matrix <= 2.5]

            intercalated_atoms.append(intercalated_atom)

        return intercalated_atoms

    @staticmethod
    def _find_the_points_around_hole(plane_points: np.ndarray, hole_point: np.ndarray) -> np.ndarray:
        # Get the points around the hole
        dists_to_hole: np.ndarray = cdist(plane_points, [hole_point])
        min_dist: float = np.min(dists_to_hole)

        # Take points that are within a radius x1.5 the distance to the nearest point
        points_radius: float = min_dist*1.5
        the_closest_points_indexes: np.ndarray = np.where(dists_to_hole <= points_radius)[0]
        return plane_points[the_closest_points_indexes]
