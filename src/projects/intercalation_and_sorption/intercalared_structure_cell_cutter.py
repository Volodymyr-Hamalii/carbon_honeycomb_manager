"""Cut unit cell from intercalated structure."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from src.interfaces import IPoints, ICarbonHoneycombChannel
from src.entities import Points
from src.services import Logger
from src.services.coordinate_operations import PointsFilter
from src.projects.carbon_honeycomb_actions import CarbonHoneycombActions
from src.projects.intercalation_and_sorption.build_intercalated_structure.semi_manual import InterAtomsTranslator
from src.projects.intercalation_and_sorption.cell_building import (
    CellParams,
    CellParamsBuilder,
    CellZCutter,
    ZCellResult,
)


logger = Logger("IntercalatedStructureCellCutter")


@dataclass(frozen=True)
class CellCutResult:
    """Elementary cell atoms, its parameters and the details of the Oz cut."""

    carbon: IPoints
    intercalated: IPoints
    cell_params: CellParams
    z_cell: ZCellResult


class IntercalatedStructureCellCutter:
    """Cut unit cell from intercalated structure using prism filtering and the minimal Oz height."""

    # Z filter bound meaning "no limit" for the prism-only filtering.
    _NO_Z_LIMIT: float = 1e9

    # Clearance coefficients for splitting the carbon structure into channels, tried in this order.
    _CLEARANCE_COEFFICIENTS: tuple[float, ...] = (2, 1.25)

    @classmethod
    def cut_unit_cell(
        cls,
        coordinates_carbon: IPoints,
        coordinates_intercalated: IPoints,
    ) -> tuple[IPoints, IPoints]:
        """
        Cut unit cell from intercalated structure.

        Returns:
            Tuple of (filtered_carbon, filtered_intercalated)
        """
        result: CellCutResult = cls.cut_cell(coordinates_carbon, coordinates_intercalated)

        return result.carbon, result.intercalated

    @classmethod
    def cut_cell(
        cls,
        coordinates_carbon: IPoints,
        coordinates_intercalated: IPoints,
    ) -> CellCutResult:
        """
        Cut the minimal elementary cell: the xy prism over 4 channel centers and the minimal height along Oz.

        Returns:
            Cell atoms together with the cell height and the parameters for `cell_params.txt`.
        """
        logger.info("Starting unit cell cutting process")

        # Step 1: Find 4 channel centers
        carbon_channels: list[ICarbonHoneycombChannel] = cls._split_into_channels(coordinates_carbon)
        channel_centers = cls._find_four_channel_centers(coordinates_carbon, carbon_channels)
        logger.info(f"Found 4 channel centers:")
        for i, center in enumerate(channel_centers):
            logger.info(f"  Center {i}: {center.tolist()}")

        # Order centers to form a proper quadrilateral
        ordered_centers = cls._order_centers_as_quadrilateral(channel_centers)
        logger.info(f"Ordered centers for quadrilateral:")
        for i, center in enumerate(ordered_centers):
            logger.info(f"  Ordered center {i}: {center.tolist()}")

        # Step 2: Calculate plane parameters for quadrilateral prism
        plane_params = cls._calculate_prism_planes(ordered_centers)
        logger.info(f"Calculated {len(plane_params)} plane parameters:")
        for i, (A, B, C, D) in enumerate(plane_params):
            logger.info(f"  Plane {i}: A={A:.6f}, B={B:.6f}, C={C:.6f}, D={D:.6f}")

        # Step 3: Filter by the xy prism only; the Oz cut is done below
        carbon_z_min = np.min(coordinates_carbon.points[:, 2])
        carbon_z_max = np.max(coordinates_carbon.points[:, 2])
        logger.info(f"Carbon Z limits: {carbon_z_min} to {carbon_z_max}")

        # Calculate centroid of the prism from the 4 centers
        prism_centroid = np.mean(ordered_centers, axis=0)
        logger.info(f"Prism centroid: {prism_centroid.tolist()}")

        # Step 4: Filter carbon atoms inside prism
        carbon_in_prism: IPoints = cls._filter_points_inside_prism(
            coordinates_carbon, plane_params, carbon_z_min, carbon_z_max, prism_centroid
        )
        logger.info(f"Carbon atoms in prism: {len(carbon_in_prism.points)} atoms")

        # Step 5: Filter intercalated atoms inside prism (not clipped by the carbon height)
        inter_in_prism: IPoints = cls._filter_points_inside_prism(
            coordinates_intercalated, plane_params, -cls._NO_Z_LIMIT, cls._NO_Z_LIMIT, prism_centroid
        )
        logger.info(f"Intercalated atoms in prism: {len(inter_in_prism.points)} atoms")

        # Validate we have atoms
        if len(carbon_in_prism.points) == 0:
            raise ValueError(
                "No carbon atoms found in prism. Check if direction parameter is correct."
            )

        if len(inter_in_prism.points) == 0:
            raise ValueError("No intercalated atoms found in prism.")

        # Step 6: Cut along Oz to the minimal repeating height
        z_cell: ZCellResult = CellZCutter.build_cell(
            carbon_all=coordinates_carbon.points,
            carbon_in_prism=carbon_in_prism.points,
            inter_in_prism=inter_in_prism.points,
        )
        logger.info(
            f"Cell height c={z_cell.cell_height:.6f} ({z_cell.num_of_periods} x {z_cell.carbon_z_period:.6f}), "
            f"verified={z_cell.verified}"
        )

        # Step 7: Cell parameters from one full channel
        cell_params: CellParams = CellParamsBuilder.build(carbon_channels[0], z_cell.cell_height)

        return CellCutResult(
            carbon=Points(z_cell.carbon),
            intercalated=Points(z_cell.intercalated),
            cell_params=cell_params,
            z_cell=z_cell,
        )

    @classmethod
    def _split_into_channels(cls, coordinates_carbon: IPoints) -> list[ICarbonHoneycombChannel]:
        """Split carbon into channels, trying the clearance coefficients until 2 full channels are found."""
        carbon_channels: list[ICarbonHoneycombChannel] = []

        for clearance_dist_coefficient in cls._CLEARANCE_COEFFICIENTS:
            carbon_channels = CarbonHoneycombActions.split_init_structure_into_separate_channels(
                coordinates_carbon,
                clearance_dist_coefficient=clearance_dist_coefficient,
            )
            if len(carbon_channels) >= 2:
                break

            logger.warning(
                f"Found {len(carbon_channels)} channels with clearance coefficient {clearance_dist_coefficient}"
            )

        return carbon_channels

    @classmethod
    def _find_four_channel_centers(
        cls,
        coordinates_carbon: IPoints,
        carbon_channels: list[ICarbonHoneycombChannel],
    ) -> list[NDArray[np.float64]]:
        """
        Find centers of 4 carbon channels (2 full + 2 edge).

        Returns:
            List of 4 center points as numpy arrays
        """
        if len(carbon_channels) < 2:
            raise ValueError(f"Expected at least 2 full channels, found {len(carbon_channels)}")

        # Calculate centers of first 2 full channels using the channel_center property
        full_channel_centers: list[NDArray[np.float64]] = []
        for channel in carbon_channels[:2]:
            center = channel.channel_center
            full_channel_centers.append(center)

        # Get 2 edge channel centers
        edge_channel_centers: list[NDArray[np.float64]] = (
            InterAtomsTranslator.get_centers_of_edge_carbon_channels(coordinates_carbon)
        )

        if len(edge_channel_centers) != 2:
            raise ValueError(
                f"Expected 2 edge channel centers, found {len(edge_channel_centers)}"
            )

        # Return all 4 centers
        return full_channel_centers + edge_channel_centers

    @classmethod
    def _order_centers_as_quadrilateral(
        cls,
        centers: list[NDArray[np.float64]]
    ) -> list[NDArray[np.float64]]:
        """
        Order 4 centers to form a proper quadrilateral (no self-intersection).

        Uses angle-based sorting around the centroid in the XY plane.

        Returns:
            Ordered list of centers
        """
        if len(centers) != 4:
            raise ValueError(f"Expected 4 centers, got {len(centers)}")

        # Calculate centroid (only using X and Y coordinates)
        centroid_xy = np.mean([center[:2] for center in centers], axis=0)

        # Calculate angle of each center from centroid
        def angle_from_centroid(center: NDArray[np.float64]) -> float:
            dx = center[0] - centroid_xy[0]
            dy = center[1] - centroid_xy[1]
            return np.arctan2(dy, dx)

        # Sort centers by angle
        sorted_centers = sorted(centers, key=angle_from_centroid)

        return sorted_centers

    @classmethod
    def _calculate_prism_planes(
        cls,
        centers: list[NDArray[np.float64]]
    ) -> list[tuple[float, float, float, float]]:
        """
        Calculate plane parameters (A, B, C, D) for quadrilateral prism sides.

        Each plane is defined by two adjacent centers and is perpendicular to XY plane.
        Plane equation: Ax + By + Cz + D = 0

        Returns:
            List of (A, B, C, D) tuples for each plane
        """
        if len(centers) != 4:
            raise ValueError(f"Expected 4 centers, got {len(centers)}")

        planes: list[tuple[float, float, float, float]] = []

        # Create planes between adjacent centers (forms a quadrilateral)
        for i in range(4):
            p1 = centers[i]
            p2 = centers[(i + 1) % 4]

            # For vertical planes (parallel to Z axis), we only need X and Y components
            # Normal vector is perpendicular to the line segment in XY plane
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]

            # Normal vector perpendicular to (dx, dy) in XY plane
            # Rotate 90 degrees: (dx, dy) -> (-dy, dx)
            A = -dy
            B = dx
            C = 0.0  # Perpendicular to Z axis

            # D = -(Ax + By + Cz) using p1
            D = -(A * p1[0] + B * p1[1] + C * p1[2])

            # Normalize the plane equation
            norm = np.sqrt(A**2 + B**2 + C**2)
            if norm > 0:
                A, B, C, D = A / norm, B / norm, C / norm, D / norm

            planes.append((float(A), float(B), float(C), float(D)))

        return planes

    @classmethod
    def _get_z_limits(cls, centers: list[NDArray[np.float64]]) -> tuple[float, float]:
        """Get min and max Z coordinates from channel centers."""
        z_coords = [center[2] for center in centers]
        return float(np.min(z_coords)), float(np.max(z_coords))

    @classmethod
    def _filter_points_inside_prism(
        cls,
        points: IPoints,
        plane_params: list[tuple[float, float, float, float]],
        z_min: float | np.floating,
        z_max: float | np.floating,
        prism_centroid: NDArray[np.float64],
    ) -> IPoints:
        """
        Filter points that are inside the quadrilateral prism.

        A point is inside if it's on the correct side of all 4 planes and within Z limits.

        Args:
            points: Points to filter
            plane_params: List of (A, B, C, D) for each plane
            z_min: Minimum Z coordinate
            z_max: Maximum Z coordinate
            prism_centroid: Center point of the prism (used to determine plane directions)
        """
        if len(points.points) == 0:
            return points

        # Start with all points
        filtered = points

        # Filter by Z limits first
        filtered = PointsFilter.filter_by_min_max_z(filtered, z_min, z_max)

        if len(filtered.points) == 0:
            return filtered

        # Use the provided prism centroid to determine which side of each plane is "inside"
        centroid = prism_centroid

        # For each plane, determine which direction points inward
        # by checking which side the centroid is on
        plane_directions: list[bool] = []
        for A, B, C, D in plane_params:
            # Calculate signed distance from centroid to plane
            signed_dist = A * centroid[0] + B * centroid[1] + C * centroid[2] + D
            # If centroid has positive distance, we want direction=True
            # If centroid has negative distance, we want direction=False
            plane_directions.append(signed_dist >= 0)

        logger.info(f"Plane directions for filtering: {plane_directions}")

        # Apply filtering with determined directions
        temp_filtered = filtered
        for i, (A, B, C, D) in enumerate(plane_params):
            direction = plane_directions[i]
            before_count = len(temp_filtered.points)

            temp_filtered = PointsFilter.filter_coordinates_related_to_plane(
                temp_filtered,
                A=A, B=B, C=C, D=D,
                direction=direction,
                min_distance=-0.1,  # small negative distance to include points on the plane
            )

            after_count = len(temp_filtered.points)
            logger.info(f"Plane {i}: direction={direction}, filtered {before_count} -> {after_count} points")

            if len(temp_filtered.points) == 0:
                logger.warning(f"No points remaining after filtering with plane {i}")
                break

        if len(temp_filtered.points) > 0:
            logger.info(f"Successfully filtered {len(temp_filtered.points)} points")
            return temp_filtered

        # If the centroid-based approach didn't work, try both directions for all planes
        logger.warning("Centroid-based filtering failed, trying brute force...")
        for direction in [True, False]:
            temp_filtered = filtered

            # Apply each plane filter
            for A, B, C, D in plane_params:
                temp_filtered = PointsFilter.filter_coordinates_related_to_plane(
                    temp_filtered,
                    A=A, B=B, C=C, D=D,
                    direction=direction,
                    min_distance=0.0
                )

                if len(temp_filtered.points) == 0:
                    break

            # If we got points, use this result
            if len(temp_filtered.points) > 0:
                logger.info(f"Successfully filtered with uniform direction={direction}")
                return temp_filtered

        # If both approaches failed, return empty Points
        logger.warning("No points found inside prism with any filtering approach")
        return Points(np.array([]).reshape(0, 3))
