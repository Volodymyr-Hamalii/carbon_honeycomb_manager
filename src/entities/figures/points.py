from dataclasses import dataclass, replace
from functools import cached_property
from typing import TypeVar

import numpy as np
import pandas as pd

from src.entities.params import CoordinateLimits
from src.interfaces import IPoints, PCoordinateLimits


T = TypeVar("T", bound="Points")


@dataclass(frozen=True)
class Points(IPoints):
    """ Template for any class with points array as a property. """
    points: np.ndarray

    def __post_init__(self) -> None:
        """Validate and ensure points array has correct shape (N, 3)."""
        points = self.points

        # Handle empty arrays
        if points.size == 0:
            if points.ndim != 2 or points.shape[1] != 3:
                object.__setattr__(self, 'points', np.array([]).reshape(0, 3))
            return

        # Validate and fix shape
        if points.ndim == 1:
            if points.size % 3 == 0:
                # Reshape from 1D to 2D: (N*3,) -> (N, 3)
                reshaped = points.reshape(-1, 3)
                object.__setattr__(self, 'points', reshaped)
            else:
                raise ValueError(
                    f"Cannot create Points from 1D array of size {points.size}. "
                    f"Size must be divisible by 3 for (N, 3) shape."
                )
        elif points.ndim != 2 or points.shape[1] != 3:
            raise ValueError(
                f"Points array must have shape (N, 3), got {points.shape}"
            )

    def __len__(self) -> int:
        return len(self.points)

    @cached_property
    def coordinate_limits(self) -> PCoordinateLimits:
        """ Returns CoordinateLimits of self.points. """

        if len(self.points) == 0:
            return CoordinateLimits()

        x_coords: np.ndarray = self.points[:, 0]
        y_coords: np.ndarray = self.points[:, 1]
        z_coords: np.ndarray = self.points[:, 2]

        return CoordinateLimits(
            x_min=np.min(x_coords),
            x_max=np.max(x_coords),

            y_min=np.min(y_coords),
            y_max=np.max(y_coords),

            z_min=np.min(z_coords),
            z_max=np.max(z_coords),
        )

    @cached_property
    def sorted_points(self) -> np.ndarray:
        """ Sorted self.points by coordinates. """
        points: np.ndarray = self.points
        return points[np.lexsort((points[:, 2], points[:, 1], points[:, 0]))]

    @cached_property
    def center(self) -> np.ndarray:
        """
        Given a set of points (N, 3) in 3D space,
        returns the coordinates of the center (centroid).
        """
        # Ensure points is a 2D array of shape (N, 3)
        if len(self.points.shape) != 2 or self.points.shape[1] != 3:
            raise ValueError("self.points must be of shape (N, 3).")

        # Compute the centroid as the mean of the coordinates
        return self.points.mean(axis=0)

    def to_df(self, columns: list[str] = ["i", "x", "y", "z"]) -> pd.DataFrame:
        """ Convert point coordinates to pandas DataFrame. """
        data: dict = {
            columns[0]: np.arange(len(self.points)),
            columns[1]: self.points[:, 0],
            columns[2]: self.points[:, 1],
            columns[3]: self.points[:, 2],
        }
        return pd.DataFrame(data)

    def copy(self: T) -> T:
        """ Returns a new Points instance. """
        return replace(self, points=self.points.copy())

    def sort(self: T, axis: int = 0) -> T:
        """Sorts self.points by the specified axis."""
        # Note: (array,) creates a tuple; (array) is just parentheses
        sort_indices = np.lexsort((self.points[:, axis],))
        return replace(self, points=self.points[sort_indices])
