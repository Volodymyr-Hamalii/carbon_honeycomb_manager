from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints
from src.interfaces.projects.carbon_honeycomb_actions.channel.planes import ICarbonHoneycombPlane


class IInterAtomsEditor(ABC):
    """
    Interface for the primitive edit operations on a set of intercalated atoms.

    Every method is pure: it returns a new set of points and never mutates the input.
    """

    @classmethod
    @abstractmethod
    def add_atoms(
            cls,
            inter_atoms: IPoints,
            new_atoms: NDArray[np.float64],
    ) -> IPoints:
        ...

    @classmethod
    @abstractmethod
    def delete_atoms(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
    ) -> IPoints:
        ...

    @classmethod
    @abstractmethod
    def move_atoms_on_vector(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
            vector: NDArray[np.float64],
    ) -> IPoints:
        ...

    @classmethod
    @abstractmethod
    def move_atoms_to_channel_center(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
            channel_center: NDArray[np.float64],
            distance: float,
    ) -> IPoints:
        ...

    @classmethod
    @abstractmethod
    def move_atoms_along_plane_normal(
            cls,
            inter_atoms: IPoints,
            indexes: Sequence[int],
            plane: ICarbonHoneycombPlane,
            channel_center: NDArray[np.float64],
            distance: float,
    ) -> IPoints:
        ...

    @classmethod
    @abstractmethod
    def shift_along_z(
            cls,
            inter_atoms: IPoints,
            shift: float,
    ) -> IPoints:
        ...

    @classmethod
    @abstractmethod
    def translate_along_z(
            cls,
            inter_atoms: IPoints,
            z_period: float,
            num_of_periods: int,
    ) -> IPoints:
        ...
