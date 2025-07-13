import numpy as np

from src.interfaces import IPoints


class IntercalatedCoordinatesUtils:
    @staticmethod
    def align_inner_points_along_channel_oz(intercaleted_points: IPoints, channel_points: IPoints) -> None:
        """ Align the points in the middle relative to the Oz channel. """

        min_channel, max_channel = np.min(channel_points.points[:, 2]), np.max(channel_points.points[:, 2])
        min_inner, max_inner = np.min(intercaleted_points.points[:, 2]), np.max(intercaleted_points.points[:, 2])

        mid_channel: np.float64 = (max_channel + min_channel) / 2
        mid_inner: np.float64 = (max_inner + min_inner) / 2

        move_z_to: np.float64 = mid_channel - mid_inner
        intercaleted_points.points[:, 2] += move_z_to

    @staticmethod
    def intercaleted_points_are_inside_channel(
        intercaleted_points: IPoints, channel_points: IPoints
    ) -> bool:
        """ Check if the intercaleted_points coordinates between max and min channel_points coordinates. """

        # TODO: check by channel planes
        if (np.min(intercaleted_points.points[:, 2]) < np.min(channel_points.points[:, 2])) or (
                np.max(intercaleted_points.points[:, 2]) > np.max(channel_points.points[:, 2])):
            # False when intercaleted_points are out of the channel
            return False
        return True
