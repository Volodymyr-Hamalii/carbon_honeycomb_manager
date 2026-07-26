
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import minimize_scalar, OptimizeResult

from src.interfaces import (
    ICarbonHoneycombChannel,
    ICarbonHoneycombPlane,
    IPoints,
    IFlatFigure,
)
from src.entities import Points
from src.services.utils import ConstantsAtomParams, Logger


logger = Logger("AtomsBuilder")


class InterAtomsBuilder:
    @classmethod
    def build_inter_atoms_near_planes(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            atom_params: ConstantsAtomParams,
            planes_limit: int | None = None,
    ) -> IPoints:
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
        logger.info(f"Distance from carbon atoms: {distance_from_carbon_atoms}")

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
    def build_inter_atoms_opposite_centers(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            atom_params: ConstantsAtomParams,
            planes_limit: int | None = None,
    ) -> IPoints:
        """
        Build intercalated atoms opposite the centers of the carbon honeycomb polygons
        (hexagons and pentagons).

        For each polygon a single atom is placed on the perpendicular to the polygon plane,
        drawn from the polygon center, at the distance atom_params.PLACE_OPPOSITE_CENTERS_DIST.
        The atom is placed on the side pointing towards the channel center (inside the channel).
        There is no atoms filtering or checking the distance between atoms here
        (that is done during the following steps).
        """

        inter_atoms: list[np.ndarray] = []
        carbon_channel_center: np.ndarray = carbon_channel.channel_center
        distance: float = atom_params.PLACE_OPPOSITE_CENTERS_DIST
        logger.info(f"Distance to place atoms opposite polygon centers: {distance}")

        for i, plane in enumerate(carbon_channel.planes):
            if planes_limit is not None and i == planes_limit:
                # To build only part of the planes
                break

            polygons: list[IFlatFigure] = [*plane.hexagons, *plane.pentagons]  # type: ignore
            for polygon in polygons:
                normal_vector: np.ndarray = cls._get_polygon_normal(polygon)
                intercalated_atom: np.ndarray = cls._place_point_towards_center(
                    point=polygon.center,
                    normal_vector=normal_vector,
                    carbon_channel_center=carbon_channel_center,
                    distance=distance,
                )
                inter_atoms.append(intercalated_atom)

        return Points(points=np.array(inter_atoms))

    @classmethod
    def build_inter_atoms_opposite_faces(
            cls,
            carbon_channel: ICarbonHoneycombChannel,
            atom_params: ConstantsAtomParams,
            planes_limit: int | None = None,
    ) -> IPoints:
        """
        Build intercalated atoms opposite the faces of the carbon honeycomb polygons
        (hexagons and pentagons).

        For each polygon the atoms are placed opposite 2 kinds of points:
        the polygon vertices and the midpoints of the polygon edges.
        Every atom is placed on the perpendicular to the polygon plane, drawn from the
        corresponding point, at the distance atom_params.PLACE_OPPOSITE_FACES_DIST, on the
        side pointing towards the channel center (inside the channel).
        There is no atoms filtering or checking the distance between atoms here
        (that is done during the following steps).
        """

        inter_atoms: list[np.ndarray] = []
        carbon_channel_center: np.ndarray = carbon_channel.channel_center
        distance: float = atom_params.PLACE_OPPOSITE_FACES_DIST
        logger.info(f"Distance to place atoms opposite polygon faces: {distance}")

        for i, plane in enumerate(carbon_channel.planes):
            if planes_limit is not None and i == planes_limit:
                # To build only part of the planes
                break

            polygons: list[IFlatFigure] = [*plane.hexagons, *plane.pentagons]  # type: ignore
            for polygon in polygons:
                normal_vector: np.ndarray = cls._get_polygon_normal(polygon)

                # The points opposite which the atoms are placed: vertices and edge midpoints
                vertices: np.ndarray = polygon.points
                edge_midpoints: np.ndarray = cls._calculate_polygon_edge_midpoints(vertices)

                source_points: np.ndarray = (
                    np.vstack([vertices, edge_midpoints]) if len(edge_midpoints) > 0 else vertices
                )

                for source_point in source_points:
                    intercalated_atom: np.ndarray = cls._place_point_towards_center(
                        point=source_point,
                        normal_vector=normal_vector,
                        carbon_channel_center=carbon_channel_center,
                        distance=distance,
                    )
                    inter_atoms.append(intercalated_atom)

        return Points(points=np.array(inter_atoms))

    @staticmethod
    def _get_polygon_normal(polygon: IFlatFigure) -> np.ndarray:
        """ Return the normalized normal vector to the polygon plane. """
        plane_params: tuple[float, float, float, float] = polygon.plane_params  # A, B, C, D
        normal_vector: np.ndarray = np.array(plane_params[:3])
        return normal_vector / np.linalg.norm(normal_vector)

    @staticmethod
    def _place_point_towards_center(
            point: np.ndarray,
            normal_vector: np.ndarray,
            carbon_channel_center: np.ndarray,
            distance: float,
    ) -> np.ndarray:
        """
        Offset the point along the normal vector by the given distance, choosing the
        direction that points towards the carbon channel center (inside the channel).
        """
        candidate1: np.ndarray = point + normal_vector * distance
        candidate2: np.ndarray = point - normal_vector * distance

        if np.sum(np.abs(candidate1 - carbon_channel_center)) < np.sum(np.abs(candidate2 - carbon_channel_center)):
            return candidate1
        return candidate2

    @staticmethod
    def _calculate_polygon_edge_midpoints(polygon_points: np.ndarray) -> np.ndarray:
        """
        Calculate the midpoints of the polygon edges.

        The edges are defined as pairs of vertices separated by the polygon side length
        (the minimal distance between vertices). Returns an array of midpoints.
        """
        if len(polygon_points) < 2:
            return np.empty((0, 3))

        dist_matrix: np.ndarray = cdist(polygon_points, polygon_points)

        # The polygon side length is the minimal non-zero distance between vertices
        non_zero_dists: np.ndarray = dist_matrix[dist_matrix > 0]
        if len(non_zero_dists) == 0:
            return np.empty((0, 3))
        side_length: float = float(np.min(non_zero_dists))

        # Allow a small clearance to treat a pair of vertices as an edge
        max_edge_dist: float = side_length * 1.25

        midpoints: list[np.ndarray] = []
        num_points: int = len(polygon_points)
        for i in range(num_points):
            for j in range(i + 1, num_points):
                if dist_matrix[i, j] <= max_edge_dist:
                    midpoints.append((polygon_points[i] + polygon_points[j]) / 2)

        return np.array(midpoints) if midpoints else np.empty((0, 3))

    @classmethod
    def _build_inter_atoms_near_polygons(
            cls,
            polygons: list[IFlatFigure],
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
        polygon: IFlatFigure,
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
        dist_from_center_to_point: np.floating = np.min(dists_from_center_to_vertex)

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
        plane: ICarbonHoneycombPlane,
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
