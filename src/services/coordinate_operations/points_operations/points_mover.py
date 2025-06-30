import numpy as np

from src_1.base_structure_classes import Points


class PointsMover:
    @staticmethod
    def move_on_vector(
            points: Points,
            vector: np.ndarray,
            axis: list[str] = ["x", "y", "z"],
    ) -> Points:
        """
        Moves points on vector along provided axis.
        Returnes moved points.
        """

        translated_inner_points: Points = points.copy()

        if "x" in axis:
            translated_inner_points.points[:, 0] += vector[0]
        if "y" in axis:
            translated_inner_points.points[:, 1] += vector[1]
        if "z" in axis:
            translated_inner_points.points[:, 1] += vector[2]

        return translated_inner_points

    @staticmethod
    def reflect_through_vertical_axis(points: Points) -> Points:
        """Reflects points through a vertical (Z) axis passing through the centroid.

        Returns:
            Points: A new Points object containing the reflected coordinates
        """
        centroid: np.ndarray = points.center

        # Create reflection matrix for XY plane (Z stays unchanged)
        reflected_points: np.ndarray = points.points.copy()
        reflected_points[:, 0] = 2 * centroid[0] - reflected_points[:, 0]  # Reflect X
        reflected_points[:, 1] = 2 * centroid[1] - reflected_points[:, 1]  # Reflect Y

        return Points(reflected_points)
