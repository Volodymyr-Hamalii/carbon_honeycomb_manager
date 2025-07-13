import numpy as np
from itertools import combinations

from src.services.utils import Logger
# from src.base_structure_classes import Points


logger = Logger(__name__)


class PointsOrganizer:
    @staticmethod
    def group_by_unique_xy(
        coordinates: np.ndarray
    ) -> dict[tuple[np.float32, np.float32], np.ndarray]:
        """
        Returns dict like
        {(x, y): [points_with_these_x_and_y]}
        """

        # Extract x and y coordinates
        xy_coordinates: np.ndarray = coordinates[:, :2]  # Get only x and y columns

        # Find unique x, y pairs and their indices
        unique_xy, indices = np.unique(xy_coordinates, axis=0, return_inverse=True)

        # Group z-coordinates by unique x, y pairs
        groups = {tuple(xy): [] for xy in unique_xy}

        for i, xy_index in enumerate(indices):
            groups[tuple(unique_xy[xy_index])].append(coordinates[i])

        # Convert each group back to NumPy arrays
        return {key: np.array(value) for key, value in groups.items()}

    @classmethod
    def group_by_the_xy_lines(
            cls,
            groups_by_xy: dict[tuple[np.float32, np.float32], np.ndarray] = {},
            coordinates_to_group: np.ndarray = np.array([]),
            epsilon: float = 1e-4,
            min_points_in_line: int = 2,
    ) -> list[dict[tuple[np.float32, np.float32], np.ndarray]]:
        """
        Groups the coordinates into sets of points that lie on lines in the xOy plane.

        Params:
        groups_by_xy - result of the PointsOrganizer._group_by_unique_xy(coordinates),
        epsilon - distance threshold to consider collinearity.

        Returns a list of dicts from groups_by_xy, each dict contains the points of one xOy line.
        """

        if not groups_by_xy and not coordinates_to_group.any():
            raise ValueError(
                "Provide groups_by_xy or coordinates_to_group for PointsOrganizer.group_by_the_xy_lines method.")

        if not groups_by_xy:
            groups_by_xy = cls.group_by_unique_xy(coordinates_to_group)
        elif coordinates_to_group:
            logger.warning("Provided both groups_by_xy and coordinates_to_group; coordinates_to_group are ignored.")

        points = list(groups_by_xy.keys())
        grouped_lines: list[dict[tuple[np.float32, np.float32], np.ndarray]] = []

        # TODO: concider replace the logic below with using cls.group_by_lines method

        # Check all combinations of 2 points to define candidate lines
        for p1, p2 in combinations(points, 2):
            line_group: dict[tuple[np.float32, np.float32], np.ndarray] = {
                p1: groups_by_xy[p1],
                p2: groups_by_xy[p2]
            }

            for p3 in points:
                if p3 == p1 or p3 == p2:
                    continue

                # Check if p3 is on the line formed by p1 and p2
                det: np.floating = (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p1[1] - p3[1]) * (p2[0] - p3[0])
                if abs(det) < epsilon:
                    line_group[p3] = groups_by_xy[p3]

            # Add to the grouped_lines if it contains at least 3 points
            if len(line_group) >= min_points_in_line:
                # Check if it's a new group (no complete overlap with existing groups)
                if not any(set(line_group.keys()).issubset(set(existing.keys())) for existing in grouped_lines):
                    grouped_lines.append(line_group)

        return grouped_lines

    @staticmethod
    def group_by_lines(
        points: np.ndarray | list[np.ndarray],
        epsilon: float = 1e-4,
        min_points_in_line: int = 2
    ) -> list[np.ndarray]:
        """
        Groups the given 2D points (or points already projected onto a plane)
        into lines, returning a list of arrays where each array holds
        the points that lie on the same line.

        Params:
        points - 2D points (shape (N,2)) or a list of such points,
        epsilon - distance threshold to consider collinearity,
        min_points_in_line - minimum number of points required to form a line.

        Returns a list of NumPy arrays, each array contains the points of one line.
        """

        # Ensure points is a NumPy array
        if isinstance(points, list):
            points = np.array(points, dtype=float)  # or float32 as needed

        # If we have fewer points than needed to form any line, return empty list
        if len(points) < min_points_in_line:
            return []

        # Convert each point to a tuple so we can easily use them in sets and comparisons
        point_tuples = [tuple(p) for p in points]

        # Prepare the result list of lines
        lines = []

        # Check all combinations of 2 distinct points to define candidate lines
        for (p1, p2) in combinations(point_tuples, 2):
            if p1 == p2:
                # Same point, skip
                continue

            # Start a line set with these two points
            line_points = {p1, p2}

            # Convert them to np arrays for vector operations
            v1 = np.array(p1)
            v2 = np.array(p2)
            direction = v2 - v1  # direction vector for the candidate line

            # Check remaining points to see if they are collinear with p1 & p2
            for p3 in point_tuples:
                if p3 == p1 or p3 == p2:
                    continue
                v3 = np.array(p3)
                # Cross product of (v2-v1) and (v3-v1)
                cross_prod = np.cross(direction, (v3 - v1))
                # If the norm of the cross product is near zero, they are collinear
                if np.linalg.norm(cross_prod) < epsilon:
                    line_points.add(p3)

            # Only add lines if they have enough points
            if len(line_points) >= min_points_in_line:
                # Convert to a NumPy array for final storage
                line_array = np.array(list(line_points), dtype=points.dtype)

                # Check if this set of points is already a subset of an existing line
                # (We don't want duplicates)
                if not any(set(map(tuple, existing_line)) >= line_points for existing_line in lines):
                    lines.append(line_array)

        return lines
