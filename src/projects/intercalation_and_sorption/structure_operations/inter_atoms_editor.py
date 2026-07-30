"""Primitive edit operations on a set of intercalated atoms."""

from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from src.interfaces import (
    ICarbonHoneycombPlane,
    IInterAtomsEditor,
    IPoints,
)
from src.entities import Points
from src.services import Logger, PointsMover


logger = Logger("InterAtomsEditor")


class InterAtomsEditor(IInterAtomsEditor):
    """
    Primitive edit operations on a set of intercalated atoms.

    Every method is pure: it returns a new `Points` instance and never mutates the input.
    Atom indexes always refer to the order of `inter_atoms.points` as it is passed in (which is the
    order of the `i` column of the xlsx files).
    """

    ROUND_DECIMALS: int = 3

    @classmethod
    def add_atoms(
            cls,
            inter_atoms: IPoints,
            new_atoms: NDArray[np.float64],
    ) -> IPoints:
        """Append atoms with the given explicit coordinates to the end of the set."""
        new_atoms_array: NDArray[np.float64] = np.asarray(new_atoms, dtype=np.float64).reshape(-1, 3)

        if len(inter_atoms.points) == 0:
            return cls._build_points(new_atoms_array)

        return cls._build_points(np.vstack([inter_atoms.points, new_atoms_array]))

    @classmethod
    def delete_atoms(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
    ) -> IPoints:
        """Remove the atoms with the given indexes."""
        cls._validate_indexes(inter_atoms, indexes)
        mask: NDArray[np.bool_] = np.ones(len(inter_atoms.points), dtype=bool)
        mask[list(indexes)] = False
        return cls._build_points(inter_atoms.points[mask])

    @classmethod
    def move_atoms_on_vector(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
            vector: NDArray[np.float64],
    ) -> IPoints:
        """Move the atoms with the given indexes on the given vector."""
        cls._validate_indexes(inter_atoms, indexes)
        vector_array: NDArray[np.float64] = np.asarray(vector, dtype=np.float64).reshape(3)

        selected: IPoints = Points(points=inter_atoms.points[list(indexes)])
        moved: IPoints = PointsMover.move_on_vector(points=selected, vector=vector_array)

        return cls._replace_atoms(inter_atoms, indexes, moved.points)

    @classmethod
    def move_atoms_to_channel_center(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
            channel_center: NDArray[np.float64],
            distance: float,
    ) -> IPoints:
        """
        Move the atoms with the given indexes towards the channel axis by `distance`.

        A negative `distance` moves them away from the axis. The z coordinate is kept: the channel
        axis is parallel to Oz, so only the xOy projection of the direction is used.
        """
        cls._validate_indexes(inter_atoms, indexes)
        center: NDArray[np.float64] = np.asarray(channel_center, dtype=np.float64).reshape(3)

        moved_atoms: list[NDArray[np.float64]] = []
        for index in indexes:
            atom: NDArray[np.float64] = inter_atoms.points[index]
            direction: NDArray[np.float64] = np.array([center[0] - atom[0], center[1] - atom[1], 0.0])
            norm: np.floating = np.linalg.norm(direction)

            if norm == 0:
                logger.warning(f"Atom {index} lies on the channel axis; it is not moved.")
                moved_atoms.append(atom.copy())
                continue

            moved_atoms.append(atom + direction / norm * distance)

        return cls._replace_atoms(inter_atoms, indexes, np.array(moved_atoms))

    @classmethod
    def move_atoms_along_plane_normal(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
            plane: ICarbonHoneycombPlane,
            channel_center: NDArray[np.float64],
            distance: float,
    ) -> IPoints:
        """
        Move the atoms with the given indexes along the normal of the given channel wall plane.

        A positive `distance` moves them away from the wall (towards the channel center), a negative
        one moves them towards the wall.
        """
        cls._validate_indexes(inter_atoms, indexes)
        center: NDArray[np.float64] = np.asarray(channel_center, dtype=np.float64).reshape(3)

        a, b, c, d = plane.plane_params
        normal: NDArray[np.float64] = np.array([a, b, c], dtype=np.float64)
        norm: np.floating = np.linalg.norm(normal)

        if norm == 0:
            raise ValueError("Plane normal vector is zero; cannot move atoms along it.")

        normal = normal / norm

        # Orient the normal towards the channel center so that a positive distance always means
        # "away from the wall" regardless of how the plane equation was built.
        signed_center_distance: float = float(np.dot(normal, center) + d / norm)
        if signed_center_distance < 0:
            normal = -normal

        moved: NDArray[np.float64] = inter_atoms.points[list(indexes)] + normal * distance

        return cls._replace_atoms(inter_atoms, indexes, moved)

    @classmethod
    def shift_along_z(
            cls,
            inter_atoms: IPoints,
            shift: float,
    ) -> IPoints:
        """Shift the whole set along the Oz axis."""
        return cls._build_points(inter_atoms.points + np.array([0.0, 0.0, shift]))

    @classmethod
    def translate_along_z(
            cls,
            inter_atoms: IPoints,
            z_period: float,
            num_of_periods: int,
    ) -> IPoints:
        """
        Replicate the set along the Oz axis.

        Returns the original atoms plus `num_of_periods` copies shifted by `z_period`,
        `2 * z_period`, ... Duplicated coordinates are removed.
        """
        if z_period <= 0:
            raise ValueError(f"z_period must be positive, got {z_period}.")

        if num_of_periods < 0:
            raise ValueError(f"num_of_periods must not be negative, got {num_of_periods}.")

        copies: list[NDArray[np.float64]] = [
            inter_atoms.points + np.array([0.0, 0.0, z_period * i])
            for i in range(num_of_periods + 1)
        ]

        translated: NDArray[np.float64] = np.unique(
            np.round(np.vstack(copies), cls.ROUND_DECIMALS), axis=0
        )

        return cls._build_points(translated)

    @classmethod
    def _build_points(cls, points: NDArray[np.float64]) -> IPoints:
        """Round the coordinates and sort them by z, y, x (the order used in the xlsx files)."""
        if len(points) == 0:
            return Points(points=np.array([]).reshape(0, 3))

        rounded: NDArray[np.float64] = np.round(np.asarray(points, dtype=np.float64), cls.ROUND_DECIMALS)
        sorted_points: NDArray[np.float64] = rounded[
            np.lexsort((rounded[:, 0], rounded[:, 1], rounded[:, 2]))
        ]
        return Points(points=sorted_points)

    @classmethod
    def _replace_atoms(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
            new_coordinates: NDArray[np.float64],
    ) -> IPoints:
        """Return a copy of the set with the atoms at `indexes` replaced by `new_coordinates`."""
        points: NDArray[np.float64] = inter_atoms.points.copy()
        points[list(indexes)] = np.asarray(new_coordinates, dtype=np.float64).reshape(len(indexes), 3)
        return cls._build_points(points)

    @staticmethod
    def _validate_indexes(inter_atoms: IPoints, indexes: Sequence[int]) -> None:
        """Raise if any index is out of range or duplicated."""
        num_of_atoms: int = len(inter_atoms.points)

        if len(set(indexes)) != len(indexes):
            raise ValueError(f"Duplicated atom indexes provided: {list(indexes)}.")

        out_of_range: list[int] = [i for i in indexes if i < 0 or i >= num_of_atoms]
        if out_of_range:
            raise IndexError(
                f"Atom indexes {out_of_range} are out of range: the set holds {num_of_atoms} atoms."
            )
