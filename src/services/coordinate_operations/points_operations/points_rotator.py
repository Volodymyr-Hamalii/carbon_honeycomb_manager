import numpy as np

from src.entities import Points


class PointsRotator:
    @classmethod
    def rotate_on_angle_related_center(
            cls,
            points: Points,
            angle_x: float = 0,
            angle_y: float = 0,
            angle_z: float = 0,
    ) -> Points:
        if angle_x == 0 and angle_y == 0 and angle_z == 0:
            return points

        # Calculate the centroid (center) of the points
        centroid: np.ndarray = np.mean(points.points, axis=0)

        # Move the points to the origin (centroid becomes the origin)
        centered_points: np.ndarray = points.points - centroid

        # Define rotation matrices for X, Y, and Z axis
        rotation_matrix_x: np.ndarray = cls._get_rotation_matrix_x(angle_x)
        rotation_matrix_y: np.ndarray = cls._get_rotation_matrix_y(angle_y)
        rotation_matrix_z: np.ndarray = cls._get_rotation_matrix_z(angle_z)

        # Combine the rotation matrices
        rotation_matrix: np.ndarray = rotation_matrix_z @ rotation_matrix_y @ rotation_matrix_x

        # Apply the rotation to the points
        rotated_points: np.ndarray = centered_points @ rotation_matrix.T

        # Move the points back to the original position (reverse translation)
        final_points: np.ndarray = rotated_points + centroid

        return Points(
            points=final_points
        )

    @staticmethod
    def _get_rotation_matrix_x(angle_x: float) -> np.ndarray:
        return np.array([
            [1, 0, 0],
            [0, np.cos(angle_x), -np.sin(angle_x)],
            [0, np.sin(angle_x), np.cos(angle_x)]
        ])

    @staticmethod
    def _get_rotation_matrix_y(angle_y: float) -> np.ndarray:
        return np.array([
            [np.cos(angle_y), 0, np.sin(angle_y)],
            [0, 1, 0],
            [-np.sin(angle_y), 0, np.cos(angle_y)]
        ])

    @staticmethod
    def _get_rotation_matrix_z(angle_z: float) -> np.ndarray:
        return np.array([
            [np.cos(angle_z), -np.sin(angle_z), 0],
            [np.sin(angle_z), np.cos(angle_z), 0],
            [0, 0, 1]
        ])

    @classmethod
    def rotate_around_z_parallel_line(
            cls,
            points: Points,
            line_point: np.ndarray,
            angle: float
    ) -> Points:
        """
        Rotate points around a line that is parallel to the Z axis and passes through the specified point.

        Args:
            points: Points to rotate
            line_point: Point that the rotation line passes through (only x,y coordinates matter)
            angle: Rotation angle in radians
        """
        if angle == 0:
            return points

        # Extract only x,y coordinates of the rotation point
        rotation_center: np.ndarray = line_point[:2]

        # Separate x,y coordinates and z coordinates of points
        xy_coords: np.ndarray = points.points[:, :2]
        z_coords: np.ndarray = points.points[:, 2:]

        # Translate points so the rotation line passes through origin
        centered_xy: np.ndarray = xy_coords - rotation_center

        # Create 2D rotation matrix
        cos_angle: float = np.cos(angle)
        sin_angle: float = np.sin(angle)
        rotation_matrix_2d: np.ndarray = np.array([
            [cos_angle, -sin_angle],
            [sin_angle, cos_angle]
        ])

        # Apply rotation to x,y coordinates
        rotated_xy: np.ndarray = centered_xy @ rotation_matrix_2d.T

        # Translate back and combine with z coordinates
        final_xy: np.ndarray = rotated_xy + rotation_center
        final_points: np.ndarray = np.hstack([final_xy, z_coords])

        return Points(points=final_points)
