"""Render prepared intercalated-channel scheme data."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from matplotlib import colormaps
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle

from src.entities import (
    Coordinate2D,
    IntercalatedChannelSchemeData,
    IntercalatedSchemeAtom,
    SchemeDimensionSegment,
)
from src.interfaces import IIntercalatedChannelSchemeRenderer

from .visualization_params import VisualizationParams


class IntercalatedChannelSchemeRenderer(IIntercalatedChannelSchemeRenderer):
    """Render nearest-distance and xOy-geometry panels into one figure."""

    _PERIODIC_COLORS: tuple[str, ...] = (
        VisualizationParams.intercalated_atoms_1_layer.color_atoms,
        VisualizationParams.intercalated_atoms_2_layer.color_atoms,
        VisualizationParams.intercalated_atoms_3_layer.color_atoms,
        VisualizationParams.intercalated_atoms_4_layer.color_atoms,
    )

    def render(self, data: IntercalatedChannelSchemeData) -> Figure:
        """Render both 2D schemes into one Matplotlib figure."""
        figure: Figure = Figure(figsize=(16, 8), dpi=100, constrained_layout=True)
        distance_axis: Axes = figure.add_subplot(1, 2, 1)
        geometry_axis: Axes = figure.add_subplot(1, 2, 2)
        colors: dict[int, Any] = self._build_atom_colors(data)

        self._draw_channel(distance_axis, data)
        self._draw_channel(geometry_axis, data)
        self._draw_distance_panel(distance_axis, data, colors)
        self._draw_geometry_panel(geometry_axis, data, colors)
        self._configure_axis(distance_axis, "Nearest 3D distances")
        self._configure_axis(geometry_axis, "xOy geometry")

        warning_text: str = " | ".join(data.warnings)
        metadata: str = data.periodicity_source
        if data.stacking_type is not None:
            metadata += f"; {data.stacking_type}"
        if data.repeat_length is not None:
            metadata += f"; repeat={data.repeat_length:.2f} Å"
        subtitle: str = metadata if not warning_text else f"{metadata}\n{warning_text}"
        figure.suptitle(
            f"2D intercalated channel scheme — {data.file_name}\n{subtitle}",
            fontsize=12,
        )
        return figure

    @staticmethod
    def _draw_channel(axis: Axes, data: IntercalatedChannelSchemeData) -> None:
        """Draw carbon projections and the ordered closed channel contour."""
        carbon_color: str = VisualizationParams.carbon.color_atoms
        bond_color: str = VisualizationParams.carbon.color_bonds
        if data.carbon_projections:
            x_coordinates: list[float] = [point[0] for point in data.carbon_projections]
            y_coordinates: list[float] = [point[1] for point in data.carbon_projections]
            multiplicities: list[int] = [point[2] for point in data.carbon_projections]
            axis.scatter(
                x_coordinates,
                y_coordinates,
                s=[max(12.0, VisualizationParams.carbon.size / count) for count in multiplicities],
                c=carbon_color,
                alpha=0.55,
                label="Carbon projections",
                zorder=2,
            )
        closed_boundary: tuple[Coordinate2D, ...] = data.channel_boundary + (
            data.channel_boundary[0],
        )
        axis.plot(
            [point[0] for point in closed_boundary],
            [point[1] for point in closed_boundary],
            color=bond_color,
            linewidth=1.4,
            label="Channel boundary",
            zorder=1,
        )

    def _draw_distance_panel(
        self,
        axis: Axes,
        data: IntercalatedChannelSchemeData,
        colors: dict[int, Any],
    ) -> None:
        """Draw all projections and representative local 3D-distance annotations."""
        for atom in data.atoms:
            self._draw_atom(axis, atom, data.atom_diameter, colors[atom.source_index])

        legend_flags: set[str] = set()
        for atom in data.atoms:
            if not atom.is_representative:
                continue
            point: Coordinate2D = (atom.coordinates[0], atom.coordinates[1])
            if atom.is_near_wall:
                self._draw_measurement_line(
                    axis,
                    point,
                    self._xy(atom.nearest_wall_projection),
                    VisualizationParams.carbon.color_bonds,
                    "-",
                    "P: perpendicular 3D distance",
                    legend_flags,
                )
                self._draw_measurement_line(
                    axis,
                    point,
                    self._xy(atom.nearest_carbon_coordinates),
                    VisualizationParams.carbon.color_atoms,
                    ":",
                    "C: full 3D distance",
                    legend_flags,
                )
            self._draw_measurement_line(
                axis,
                point,
                self._xy(atom.nearest_inter_coordinates),
                VisualizationParams.intercalated_atoms_1_layer.color_bonds,
                "--",
                "I: full 3D distance",
                legend_flags,
            )
            annotation: str = self._distance_label(atom)
            offset: tuple[int, int] = self._label_offset(atom.source_index, point, data.channel_boundary)
            axis.annotate(
                annotation,
                xy=point,
                xytext=offset,
                textcoords="offset points",
                fontsize=7,
                arrowprops={"arrowstyle": "-", "linewidth": 0.5},
                zorder=6,
            )

        axis.legend(loc="best", fontsize=7)

    def _draw_geometry_panel(
        self,
        axis: Axes,
        data: IntercalatedChannelSchemeData,
        colors: dict[int, Any],
    ) -> None:
        """Draw representative atoms, edge distances, and x/y dimensions."""
        axis.scatter(
            [point[0] for point in data.channel_boundary],
            [point[1] for point in data.channel_boundary],
            marker="s",
            s=28,
            c=VisualizationParams.intercalated_atoms_4_layer.color_bonds,
            label="Projected channel edges",
            zorder=3,
        )
        for atom in data.atoms:
            if not atom.is_representative:
                continue
            self._draw_atom(axis, atom, data.atom_diameter, colors[atom.source_index])
            point: Coordinate2D = (atom.coordinates[0], atom.coordinates[1])
            vertex: Coordinate2D | None = atom.nearest_edge_vertex_coordinates
            if vertex is not None and atom.distance_to_edge_vertex_xy is not None:
                axis.plot(
                    (point[0], vertex[0]),
                    (point[1], vertex[1]),
                    color=VisualizationParams.intercalated_atoms_4_layer.color_bonds,
                    linestyle=":",
                    linewidth=0.8,
                    zorder=2,
                )
                midpoint: Coordinate2D = (
                    (point[0] + vertex[0]) / 2.0,
                    (point[1] + vertex[1]) / 2.0,
                )
                axis.annotate(
                    f"E_xy={atom.distance_to_edge_vertex_xy:.2f}",
                    xy=midpoint,
                    fontsize=6,
                    zorder=5,
                )
            axis.annotate(
                f"#{atom.source_index}",
                xy=point,
                xytext=self._label_offset(atom.source_index, point, data.channel_boundary),
                textcoords="offset points",
                fontsize=7,
                arrowprops={"arrowstyle": "-", "linewidth": 0.4},
                zorder=6,
            )

        for segment in data.dimension_segments:
            self._draw_dimension(axis, segment)
        axis.legend(loc="best", fontsize=7)

    @staticmethod
    def _draw_atom(
        axis: Axes,
        atom: IntercalatedSchemeAtom,
        atom_diameter: float,
        color: Any,
    ) -> None:
        """Draw an element-scaled transparent atom circle and visible center."""
        circle = Circle(
            (atom.coordinates[0], atom.coordinates[1]),
            radius=atom_diameter / 2.0,
            facecolor=color,
            edgecolor=color,
            alpha=0.24,
            linewidth=1.2,
            zorder=3,
        )
        axis.add_patch(circle)
        axis.scatter(
            [atom.coordinates[0]],
            [atom.coordinates[1]],
            s=22,
            c=[color],
            edgecolors="none",
            zorder=4,
        )

    @staticmethod
    def _draw_measurement_line(
        axis: Axes,
        start: Coordinate2D,
        end: Coordinate2D | None,
        color: str,
        line_style: str,
        label: str,
        legend_flags: set[str],
    ) -> None:
        """Draw a projected measurement line with one legend entry per kind."""
        if end is None:
            return
        legend_label: str | None = None if label in legend_flags else label
        legend_flags.add(label)
        axis.plot(
            (start[0], end[0]),
            (start[1], end[1]),
            color=color,
            linestyle=line_style,
            linewidth=0.9,
            label=legend_label,
            zorder=2,
        )

    @staticmethod
    def _draw_dimension(axis: Axes, segment: SchemeDimensionSegment) -> None:
        """Draw one coordinate-level or boundary-gap measurement."""
        color: str = (
            VisualizationParams.carbon.color_bonds
            if segment.kind == "coordinate_level"
            else VisualizationParams.intercalated_atoms_3_layer.color_bonds
        )
        line_style: str = "-" if segment.kind == "coordinate_level" else "--"
        axis.annotate(
            "",
            xy=segment.end,
            xytext=segment.start,
            arrowprops={
                "arrowstyle": "|-|",
                "color": color,
                "linestyle": line_style,
                "linewidth": 0.8,
            },
            zorder=1,
        )
        midpoint: Coordinate2D = (
            (segment.start[0] + segment.end[0]) / 2.0,
            (segment.start[1] + segment.end[1]) / 2.0,
        )
        prefix: str = "ΔX" if segment.orientation == "x" else "ΔY"
        rotation: float = 45.0 if (
            segment.kind == "coordinate_level"
            and segment.orientation == "x"
            and segment.value < 1.5
        ) else 0.0
        axis.annotate(
            f"{prefix}={segment.value:.2f}",
            xy=midpoint,
            fontsize=6,
            ha="center",
            va="bottom",
            color=color,
            rotation=rotation,
            zorder=5,
        )

    @staticmethod
    def _configure_axis(axis: Axes, title: str) -> None:
        """Apply common readable 2D-axis settings."""
        axis.set_title(title)
        axis.set_xlabel("X (Å)")
        axis.set_ylabel("Y (Å)")
        axis.set_aspect("equal", adjustable="datalim")
        axis.grid(True, alpha=0.25)
        axis.relim()
        axis.autoscale_view()
        axis.margins(0.08)

    def _build_atom_colors(
        self, data: IntercalatedChannelSchemeData
    ) -> dict[int, Any]:
        """Assign repeat-template or fallback z-layer colors deterministically."""
        if data.periodicity_source != "unknown":
            return {
                atom.source_index: self._PERIODIC_COLORS[
                    atom.template_index % len(self._PERIODIC_COLORS)
                ]
                for atom in data.atoms
            }
        number_of_layers: int = max(atom.layer_index for atom in data.atoms) + 1
        color_map = colormaps["tab20"].resampled(number_of_layers)
        return {
            atom.source_index: color_map(atom.layer_index)
            for atom in data.atoms
        }

    @staticmethod
    def _distance_label(atom: IntercalatedSchemeAtom) -> str:
        """Format one representative atom label to two decimals."""
        inter_value: str = (
            "—" if atom.min_distance_to_inter is None else f"{atom.min_distance_to_inter:.2f}"
        )
        periodic_suffix: str = ""
        if atom.nearest_inter_periodic_shift:
            periodic_suffix = f" ({atom.nearest_inter_periodic_shift:+d} cell)"
        if atom.is_near_wall:
            plane_value: str = (
                "—" if atom.min_distance_to_plane is None else f"{atom.min_distance_to_plane:.2f}"
            )
            carbon_value: str = (
                "—" if atom.min_distance_to_carbon is None else f"{atom.min_distance_to_carbon:.2f}"
            )
            return (
                f"#{atom.source_index}; P={plane_value}; C={carbon_value}; "
                f"I={inter_value}{periodic_suffix}"
            )
        return f"#{atom.source_index}; I={inter_value}{periodic_suffix}"

    @staticmethod
    def _label_offset(
        source_index: int,
        point: Coordinate2D,
        boundary: Sequence[Coordinate2D],
    ) -> tuple[int, int]:
        """Choose a deterministic offset from quadrant and source index."""
        center_x: float = sum(vertex[0] for vertex in boundary) / len(boundary)
        center_y: float = sum(vertex[1] for vertex in boundary) / len(boundary)
        x_sign: int = 1 if point[0] >= center_x else -1
        y_sign: int = 1 if point[1] >= center_y else -1
        magnitude: int = 10 + 4 * (source_index % 3)
        return x_sign * magnitude, y_sign * magnitude

    @staticmethod
    def _xy(coordinates: tuple[float, float, float] | None) -> Coordinate2D | None:
        """Project an optional 3D coordinate to xOy."""
        if coordinates is None:
            return None
        return coordinates[0], coordinates[1]
