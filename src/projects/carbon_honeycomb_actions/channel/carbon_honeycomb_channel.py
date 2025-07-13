from dataclasses import dataclass
from functools import cached_property
import numpy as np

from src.interfaces import ICarbonHoneycombPlane, ICarbonHoneycombChannel
from src.entities import Points

from .carbon_honeycomb_channel_actions import CarbonHoneycombChannelActions


@dataclass(frozen=True)
class CarbonHoneycombChannel(ICarbonHoneycombChannel, Points):
    @cached_property
    def planes(self) -> list[ICarbonHoneycombPlane]:
        """
        A list of CarbonHoneycombPlane objects
        representing planes in the honeycomb channel.
        """
        return CarbonHoneycombChannelActions.build_planes(self.points)

    @cached_property
    def channel_center(self) -> np.ndarray:
        """ Coordinates of the channel center. """
        return self.points.mean(axis=0)

    @cached_property
    def ave_dist_between_closest_atoms(self) -> np.floating:
        """ Calculate the average distance between hexagon centers in all planes. """
        return CarbonHoneycombChannelActions.calculate_ave_dist_between_closest_atoms(self.points)

    @cached_property
    def ave_dist_between_closest_hexagon_centers(self) -> np.floating:
        """ Calculate the average distance between hexagon centers in all planes. """
        return CarbonHoneycombChannelActions.calculate_ave_dist_between_closest_hexagon_centers(self.planes)
