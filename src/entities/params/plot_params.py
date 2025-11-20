from dataclasses import dataclass, field
from typing import Any
import numpy as np
from numpy.typing import NDArray

from src.interfaces import PCoordinateLimits


@dataclass
class PlotParams:
    """Parameters for plot customization and state management."""

    # Plot visualization parameters
    camera_elevation: float = 62.0
    camera_azimuth: float = -100.0
    camera_roll: float = -3.0
    plot_scale: float = 0.0

    to_build_bonds: bool = True
    to_show_coordinates: bool = False
    to_show_indexes: bool = False
    to_set_equal_scale: bool = True
    num_of_min_distances: int = 2
    skip_first_distances: int = 0

    # Coordinate limits
    x_min: float = -float("inf")
    x_max: float = float("inf")
    y_min: float = -float("inf")
    y_max: float = float("inf")
    z_min: float = -float("inf")
    z_max: float = float("inf")

    # Plot window settings
    title: str = "Structure Plot"
    figsize: tuple[float, float] = (12, 9)

    # Interactive features
    is_interactive_mode: bool = False
    to_build_edge_vertical_lines: bool = False
    to_show_dists_to_plane: bool = False
    to_show_dists_to_edges: bool = False
    to_show_channel_angles: bool = False
    to_show_plane_lengths: bool = False

    # New visualization features
    to_show_grid: bool = True
    to_show_legend: bool = True
    to_show_title: bool = True
    num_of_inter_atoms_layers: int = 1
    plot_intercalated_as_polygon_balls: bool = False

    # Auto-scaling behavior (always fit to data, never store scale)
    auto_scale_to_data: bool = True

    @property
    def coordinate_limits(self) -> PCoordinateLimits:
        """Get coordinate limits as protocol object."""
        from src.entities.params.coordinate_limits import CoordinateLimits
        return CoordinateLimits(
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max,
            z_min=self.z_min,
            z_max=self.z_max,
        )

    def set_coordinate_limits(self, limits: PCoordinateLimits) -> None:
        """Set coordinate limits from protocol object."""
        self.x_min = limits.x_min
        self.x_max = limits.x_max
        self.y_min = limits.y_min
        self.y_max = limits.y_max
        self.z_min = limits.z_min
        self.z_max = limits.z_max

    def set_camera_view(self, elevation: float, azimuth: float) -> None:
        """Set camera viewing angles."""
        self.camera_elevation = elevation
        self.camera_azimuth = azimuth

    def set_plot_scale(self, scale: float) -> None:
        """Set plot scale factor."""
        self.plot_scale = scale

    def has_coordinate_limits(self) -> bool:
        """Check if coordinate limits are set (not infinite)."""
        return not (
            self.x_min == -float("inf") and self.x_max == float("inf") and
            self.y_min == -float("inf") and self.y_max == float("inf") and
            self.z_min == -float("inf") and self.z_max == float("inf")
        )

    def copy(self) -> "PlotParams":
        """Create a copy of the plot parameters."""
        return PlotParams(
            camera_elevation=self.camera_elevation,
            camera_azimuth=self.camera_azimuth,
            camera_roll=self.camera_roll,
            plot_scale=self.plot_scale,
            to_build_bonds=self.to_build_bonds,
            to_show_coordinates=self.to_show_coordinates,
            to_show_indexes=self.to_show_indexes,
            to_set_equal_scale=self.to_set_equal_scale,
            num_of_min_distances=self.num_of_min_distances,
            skip_first_distances=self.skip_first_distances,
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max,
            z_min=self.z_min,
            z_max=self.z_max,
            title=self.title,
            figsize=self.figsize,
            is_interactive_mode=self.is_interactive_mode,
            to_build_edge_vertical_lines=self.to_build_edge_vertical_lines,
            to_show_dists_to_plane=self.to_show_dists_to_plane,
            to_show_dists_to_edges=self.to_show_dists_to_edges,
            to_show_channel_angles=self.to_show_channel_angles,
            to_show_plane_lengths=self.to_show_plane_lengths,
            to_show_grid=self.to_show_grid,
            to_show_legend=self.to_show_legend,
            to_show_title=self.to_show_title,
            num_of_inter_atoms_layers=self.num_of_inter_atoms_layers,
            plot_intercalated_as_polygon_balls=self.plot_intercalated_as_polygon_balls,
            auto_scale_to_data=self.auto_scale_to_data,
        )
