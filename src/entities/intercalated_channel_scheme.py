"""Immutable data prepared for the intercalated-channel 2D scheme."""

from dataclasses import dataclass
from typing import Literal


Coordinate2D = tuple[float, float]
Coordinate3D = tuple[float, float, float]
PeriodicitySource = Literal["geometry-confirmed", "filename-derived", "unknown"]
DimensionKind = Literal["coordinate_level", "boundary_gap"]
DimensionOrientation = Literal["x", "y"]


@dataclass(frozen=True)
class IntercalatedSchemeAtom:
    """Describe one intercalated atom and its optional local measurements."""

    source_index: int
    atom_id: str
    coordinates: Coordinate3D
    layer_index: int
    template_index: int
    template_label: str
    is_representative: bool
    is_near_wall: bool | None = None
    min_distance_to_plane: float | None = None
    nearest_wall_projection: Coordinate3D | None = None
    min_distance_to_carbon: float | None = None
    nearest_carbon_coordinates: Coordinate3D | None = None
    min_distance_to_inter: float | None = None
    nearest_inter_source_index: int | None = None
    nearest_inter_atom_id: str | None = None
    nearest_inter_base_coordinates: Coordinate3D | None = None
    nearest_inter_coordinates: Coordinate3D | None = None
    nearest_inter_periodic_shift: int = 0
    nearest_edge_vertex_index: int | None = None
    nearest_edge_vertex_coordinates: Coordinate2D | None = None
    distance_to_edge_vertex_xy: float | None = None


@dataclass(frozen=True)
class SchemeDimensionSegment:
    """Describe one deterministic xOy dimension segment."""

    orientation: DimensionOrientation
    kind: DimensionKind
    start: Coordinate2D
    end: Coordinate2D
    value: float
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class IntercalatedChannelSchemeData:
    """Contain all read-only data needed to render both 2D schemes."""

    file_name: str
    element_symbol: str
    atom_diameter: float
    equilibrium_inter_carbon_distance: float
    carbon_projections: tuple[tuple[float, float, int], ...]
    channel_boundary: tuple[Coordinate2D, ...]
    atoms: tuple[IntercalatedSchemeAtom, ...]
    representative_indexes: tuple[int, ...]
    dimension_segments: tuple[SchemeDimensionSegment, ...]
    stacking_type: str | None
    repeat_length: float | None
    periodicity_source: PeriodicitySource
    warnings: tuple[str, ...]
