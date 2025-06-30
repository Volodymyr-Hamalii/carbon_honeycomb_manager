from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from src.interfaces.entities.figures.i_points import IPoints
from src.interfaces.entities.figures.carbon_honeycomb_components.i_ch_channel import ICHChannel
from src.interfaces.services.coordinate_operations.points_operations.i_points_organizer import IPointsOrganizer
from src.interfaces.services.coordinate_operations.i_distance_measurer import IDistanceMeasurer
from src.interfaces.services.structure_visualizer.i_structure_visualizer import IStructureVisualizer


class ICarbonHoneycombActions(ABC):
    """Interface for carbon honeycomb actions."""

    @staticmethod
    @abstractmethod
    def _filter_honeycomb_planes_groups(
            honeycomb_planes_groups: list[dict[tuple[np.float32, np.float32], NDArray[np.float64]]],
    ) -> list[dict[tuple[np.float32, np.float32], NDArray[np.float64]]]:
        ...

    @staticmethod
    @abstractmethod
    def _build_honeycomb_channels(
            honeycomb_planes_groups: list[dict[tuple[np.float32, np.float32], NDArray[np.float64]]],
            plane_groups_indexes: list[list[int]],
    ) -> list[ICHChannel]:
        ...

    @classmethod
    @abstractmethod
    def split_init_structure_into_separate_channels(
            cls,
            coordinates_carbon: IPoints,
            clearance_dist_coefficient: float,
    ) -> list[ICHChannel]:
        ...
