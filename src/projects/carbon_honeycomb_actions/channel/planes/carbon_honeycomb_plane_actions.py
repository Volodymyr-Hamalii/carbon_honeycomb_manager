from typing import Type, Sequence, overload
import numpy as np

from src.services import PointsOrganizer, DistanceMeasurer
from src.interfaces import PCoordinateLimits

from ...carbon_honeycomb_utils import CarbonHoneycombUtils
from .plane_polygons import CarbonHoneycombPolygon, CarbonHoneycombPentagon, CarbonHoneycombHexagon


class CarbonHoneycombPlaneActions:
    # A pair of plane atoms is treated as a polygon edge (a C-C bond) when the distance between them
    # does not exceed the shortest interatomic distance in the plane multiplied by this coefficient.
    #
    # The walls are slightly distorted, so the real bond lengths are not identical: in the shipped
    # structures they spread from 1.440 to 1.540 A (+6.9% over the shortest one). The shortest
    # non-bonded pair (the two atoms flanking an edge hole of an armchair-oriented wall, e.g. in the
    # C-family structures) is 1.641 A (+14.0%), so 1.1 separates bonds from non-bonds with a margin
    # on both sides.
    #
    # NOTE: this used to be `max(min_distance_per_point) * 1.25`, which resolved to 1.863 A and
    # therefore accepted those 1.641 A non-bonded pairs as edges. The spurious edges short-circuited
    # the real hexagons of the C-family walls into 5-cycles, which is why `ar/C0-7_h3` used to report
    # 17 pentagons and 0 hexagons per plane.
    BOND_LENGTH_CLEARANCE_COEFFICIENT: float = 1.1

    @classmethod
    def define_plane_pentagons(cls, points: np.ndarray) -> Sequence[CarbonHoneycombPentagon]:
        points_grouped_by_lines, plane_polygon_indexes = cls._define_point_for_plane_polygon(
            points, num_of_sides=5)

        return cls._build_plane_polygon(
            points_grouped_by_lines, plane_polygon_indexes, polygon_class=CarbonHoneycombPentagon)

    @classmethod
    def define_plane_hexagons(cls, points: np.ndarray) -> Sequence[CarbonHoneycombHexagon]:
        points_grouped_by_lines, plane_polygon_indexes = cls._define_point_for_plane_polygon(
            points, num_of_sides=6)

        return cls._build_plane_polygon(
            points_grouped_by_lines, plane_polygon_indexes, polygon_class=CarbonHoneycombHexagon)

    @classmethod
    def _define_point_for_plane_polygon(
            cls,
            points: np.ndarray,
            num_of_sides: int,
    ) -> tuple[list[np.ndarray], list[list[int]]]:
        points_grouped_by_lines: list[np.ndarray] = PointsOrganizer.group_by_lines(points)

        distances_between_points: np.ndarray = DistanceMeasurer.calculate_min_distances_between_points(points)

        max_distance_between_points: np.floating = (
            np.min(distances_between_points) * cls.BOND_LENGTH_CLEARANCE_COEFFICIENT
        )

        points_grouped_by_lines = CarbonHoneycombUtils.split_groups_by_max_distances(
            points_grouped_by_lines, max_distance_between_points)

        end_points: list[tuple[tuple, tuple]] = cls._find_end_points(points_grouped_by_lines)

        plane_polygon_indexes: list[list[int]] = CarbonHoneycombUtils.found_polygon_node_indexes(
            end_points, num_of_sides)

        return points_grouped_by_lines, plane_polygon_indexes

    @staticmethod
    def _find_end_points(points_grouped_by_lines: list[np.ndarray]) -> list[tuple[tuple, tuple]]:

        end_points_of_groups: list[tuple[tuple, tuple]] = []

        for group in points_grouped_by_lines:
            coordinates_to_check: tuple[str, str] = ("x", "z")  # default

            # Chech if all x coordinates are equal
            x_coord: np.ndarray = group[:, 0]
            all_x_equal: np.bool_ = np.all(x_coord == x_coord[0])

            if all_x_equal:
                # Replace "x" with "y":
                coordinates_to_check: tuple[str, str] = ("y", "z")

            start, end = CarbonHoneycombUtils.find_end_points(
                points_on_line=group, coordinates_to_check=coordinates_to_check)
            end_points_of_groups.append((start, end))

        # return sorted(end_points_of_groups, key=lambda p: p[0][0])
        return end_points_of_groups

    # Overload 1: Hexagon
    @overload
    @staticmethod
    def _build_plane_polygon(
        points_grouped_by_lines: list[np.ndarray],
        plane_hexagons_indexes: list[list[int]],
        polygon_class: Type[CarbonHoneycombHexagon],
    ) -> Sequence[CarbonHoneycombHexagon]:
        ...

    # Overload 2: Pentagon
    @overload
    @staticmethod
    def _build_plane_polygon(
        points_grouped_by_lines: list[np.ndarray],
        plane_hexagons_indexes: list[list[int]],
        polygon_class: Type[CarbonHoneycombPentagon],
    ) -> Sequence[CarbonHoneycombPentagon]:
        ...

    @staticmethod
    def _build_plane_polygon(
            points_grouped_by_lines: list[np.ndarray],
            plane_hexagons_indexes: list[list[int]],
            polygon_class: Type[CarbonHoneycombPolygon],
    ) -> Sequence[CarbonHoneycombPolygon]:
        plane_hexagons: list[CarbonHoneycombPolygon] = []

        for plane_group_indexes in plane_hexagons_indexes:
            unique_points_set = set()

            for i in plane_group_indexes:
                for point in points_grouped_by_lines[i]:
                    # Convert to tuple to store in a set
                    point_tuple = tuple(point)
                    unique_points_set.add(point_tuple)

            # Convert the set of tuples back to a numpy array
            honeycomb_points: np.ndarray = np.array(list(unique_points_set))
            honeycomb_channel = polygon_class(points=honeycomb_points)
            plane_hexagons.append(honeycomb_channel)

        return plane_hexagons

    @classmethod
    def calculate_edge_holes(
        cls,
        points: np.ndarray,
        coordinate_limits: PCoordinateLimits,
    ) -> np.ndarray:

        # Take the extreme points from the both sides
        left_edge: np.ndarray = points[(points[:, 0] == coordinate_limits.x_min)]
        if len(left_edge) == len(points):
            # Filter by Y
            left_edge: np.ndarray = points[(points[:, 1] == coordinate_limits.y_min)]
            right_edge: np.ndarray = points[(points[:, 1] == coordinate_limits.y_max)]
        else:
            right_edge: np.ndarray = points[(points[:, 0] == coordinate_limits.x_max)]
        
        
        left_edge_holes: list[np.ndarray] = cls._calc_holes_for_edge(left_edge)
        right_edge_holes: list[np.ndarray] = cls._calc_holes_for_edge(right_edge)

        return np.array(left_edge_holes + right_edge_holes)

    @staticmethod
    def _calc_holes_for_edge(edge_points: np.ndarray) -> list[np.ndarray]:
        # Sort the edge points (by the z-coordinate)
        edge_points.sort(axis=0)

        # Get the min distance (or the approx length of the polygon edge)
        edge_dists: np.ndarray = DistanceMeasurer.calculate_dist_matrix(edge_points)
        min_dist: np.floating = edge_dists.min()

        # Distances to the next neighbor
        conseq_dists: np.ndarray = np.diag(edge_dists, k=1)

        holes: list[np.ndarray] = []

        for i, point in enumerate(edge_points[:-1]):
            dist: np.floating = conseq_dists[i]
            if dist.round(1) > min_dist.round(1):
                # The distance is more than minimal (or than polygon edge)
                # so, between this and the next point is edge hole
                hole: np.ndarray = (point + edge_points[i+1]) / 2
                holes.append(hole)

        if not holes:
            # Take each interval between neighbours as a hole
            for i, point in enumerate(edge_points[:-1]):
                hole: np.ndarray = (point + edge_points[i+1]) / 2
                holes.append(hole)

        return holes
