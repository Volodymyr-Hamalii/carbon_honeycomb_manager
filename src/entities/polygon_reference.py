"""Typed records used by polygon-reference geometry workflows."""

from dataclasses import dataclass
from typing import Any, Literal


Coordinate = tuple[float, float, float]
PolygonSiteType = Literal["center", "vertex", "edge_midpoint"]


@dataclass(frozen=True)
class PolygonRing:
    """Represent one canonical five- or six-member carbon ring."""

    ring_id: str
    center: Coordinate
    vertex_ids: tuple[str, ...]
    carbon_atom_indexes: tuple[int, ...]
    wall_index: int
    inward_normal: Coordinate

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""
        return {
            "ring_id": self.ring_id,
            "center": list(self.center),
            "vertex_ids": list(self.vertex_ids),
            "carbon_atom_indexes": list(self.carbon_atom_indexes),
            "wall_id": f"wall-{self.wall_index}",
            "wall_index": self.wall_index,
            "inward_normal": list(self.inward_normal),
        }


@dataclass(frozen=True)
class PolygonWallAssociation:
    """Associate a physical reference site with one channel wall."""

    wall_index: int
    inward_normal: Coordinate

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""
        return {
            "wall_id": f"wall-{self.wall_index}",
            "wall_index": self.wall_index,
            "inward_normal": list(self.inward_normal),
        }


@dataclass(frozen=True)
class PolygonReferenceSite:
    """Represent one unique polygon-related source site."""

    site_id: str
    site_type: PolygonSiteType
    coordinates: Coordinate
    associations: tuple[PolygonWallAssociation, ...]
    carbon_atom_indexes: tuple[int, ...]
    carbon_atom_ids: tuple[str, ...]
    ring_id: str | None = None
    ring_vertex_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation with provenance."""
        return {
            "site_id": self.site_id,
            "site_type": self.site_type,
            "coordinates": list(self.coordinates),
            "associations": [association.to_dict() for association in self.associations],
            "carbon_atom_indexes": list(self.carbon_atom_indexes),
            "carbon_atom_ids": list(self.carbon_atom_ids),
            "ring_id": self.ring_id,
            "ring_vertex_ids": list(self.ring_vertex_ids),
        }


@dataclass(frozen=True)
class GeneratedPolygonCandidate:
    """Represent a pure candidate generated from a site and inward normal."""

    atom_id: str
    coordinates: Coordinate
    site_id: str
    site_type: PolygonSiteType
    wall_index: int
    inward_normal: Coordinate

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""
        return {
            "atom_id": self.atom_id,
            "coordinates": list(self.coordinates),
            "site_id": self.site_id,
            "site_type": self.site_type,
            "wall_index": self.wall_index,
            "wall_id": f"wall-{self.wall_index}",
            "inward_normal": list(self.inward_normal),
        }


@dataclass(frozen=True)
class PolygonSiteMeasurement:
    """Contain the polygon-reference measurements for one intercalated atom."""

    values: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a copy suitable for JSON or a DataFrame row."""
        return dict(self.values)


@dataclass(frozen=True)
class PolygonSiteMeasurementReport:
    """Contain per-atom polygon measurements and their compact summary."""

    rows: tuple[PolygonSiteMeasurement, ...]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly report."""
        return {"rows": [row.to_dict() for row in self.rows], "summary": dict(self.summary)}
