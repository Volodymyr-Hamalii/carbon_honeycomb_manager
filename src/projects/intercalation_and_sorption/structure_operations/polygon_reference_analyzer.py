"""Polygon-reference geometry for intercalated carbon structures."""

from collections import OrderedDict
from hashlib import sha1
from typing import Any

import numpy as np
from numpy.typing import NDArray

from src.entities import (
    GeneratedPolygonCandidate,
    PolygonReferenceSite,
    PolygonRing,
    PolygonSiteMeasurement,
    PolygonSiteMeasurementReport,
    PolygonSiteType,
    PolygonWallAssociation,
)
from src.interfaces import ICarbonHoneycombChannel, IPoints, IPolygonReferenceAnalyzer


class PolygonReferenceAnalyzer(IPolygonReferenceAnalyzer):
    """Extract and measure deterministic polygon-related reference sites."""

    BOND_MAX_DISTANCE: float = 1.65
    PLANE_MEMBERSHIP_TOLERANCE: float = 0.2
    ZERO_TOLERANCE: float = 1e-9
    _CACHE_LIMIT: int = 16
    _sites_cache: OrderedDict[int, tuple[ICarbonHoneycombChannel, tuple[PolygonReferenceSite, ...]]] = OrderedDict()

    @classmethod
    def get_reference_sites(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        site_types: tuple[PolygonSiteType, ...] | None = None,
        wall_indexes: tuple[int, ...] | None = None,
    ) -> tuple[PolygonReferenceSite, ...]:
        """Return unique reference sites, optionally filtered by type and wall."""
        if wall_indexes is not None:
            invalid_walls: list[int] = [
                wall_index for wall_index in wall_indexes
                if wall_index < 0 or wall_index >= len(carbon_channel.planes)
            ]
            if invalid_walls:
                raise IndexError(
                    f"Wall indexes {invalid_walls} are out of range for "
                    f"{len(carbon_channel.planes)} walls."
                )
        cache_key: int = id(carbon_channel)
        cached = cls._sites_cache.get(cache_key)
        if cached is None or cached[0] is not carbon_channel:
            sites: tuple[PolygonReferenceSite, ...] = cls._extract_sites(carbon_channel)
            cls._sites_cache[cache_key] = (carbon_channel, sites)
            cls._sites_cache.move_to_end(cache_key)
            while len(cls._sites_cache) > cls._CACHE_LIMIT:
                cls._sites_cache.popitem(last=False)
        else:
            sites = cached[1]

        if site_types is None and wall_indexes is None:
            return sites

        allowed_types: set[PolygonSiteType] | None = None if site_types is None else set(site_types)
        allowed_walls: set[int] | None = None if wall_indexes is None else set(wall_indexes)
        return tuple(
            site for site in sites
            if (allowed_types is None or site.site_type in allowed_types)
            and (
                allowed_walls is None
                or any(association.wall_index in allowed_walls for association in site.associations)
            )
        )

    @classmethod
    def get_rings(
        cls, carbon_channel: ICarbonHoneycombChannel
    ) -> tuple[PolygonRing, ...]:
        """Return canonical rings derived from cached center sites."""
        rings: list[PolygonRing] = []
        for site in cls.get_reference_sites(carbon_channel, site_types=("center",)):
            association: PolygonWallAssociation = site.associations[0]
            if site.ring_id is None:
                continue
            rings.append(PolygonRing(
                ring_id=site.ring_id,
                center=site.coordinates,
                vertex_ids=site.ring_vertex_ids,
                carbon_atom_indexes=site.carbon_atom_indexes,
                wall_index=association.wall_index,
                inward_normal=association.inward_normal,
            ))
        return tuple(rings)

    @classmethod
    def generate_candidates(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        center_target: float,
        face_target: float,
        site_types: tuple[PolygonSiteType, ...] | None = None,
        wall_indexes: tuple[int, ...] | None = None,
    ) -> tuple[GeneratedPolygonCandidate, ...]:
        """Generate one unmerged candidate per site-wall association."""
        if center_target < 0.0 or face_target < 0.0:
            raise ValueError("Polygon-site target distances must be non-negative.")
        candidates: list[GeneratedPolygonCandidate] = []
        for site in cls.get_reference_sites(carbon_channel, site_types, wall_indexes):
            target: float = center_target if site.site_type == "center" else face_target
            for association in site.associations:
                if wall_indexes is not None and association.wall_index not in wall_indexes:
                    continue
                point: NDArray[np.float64] = np.asarray(site.coordinates, dtype=np.float64)
                normal: NDArray[np.float64] = np.asarray(association.inward_normal, dtype=np.float64)
                coordinates: NDArray[np.float64] = point + normal * target
                atom_id: str = f"candidate-{site.site_id}-w{association.wall_index}"
                candidates.append(GeneratedPolygonCandidate(
                    atom_id=atom_id,
                    coordinates=cls._coordinate(coordinates),
                    site_id=site.site_id,
                    site_type=site.site_type,
                    wall_index=association.wall_index,
                    inward_normal=association.inward_normal,
                ))
        return tuple(candidates)

    @classmethod
    def measure(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        inter_atoms: IPoints,
        center_target: float,
        face_target: float,
        near_wall_max_dist_to_plane: float,
        alignment_tolerance: float,
        corridor_lower_percent: float = -8.0,
        corridor_upper_percent: float = 10.0,
        reference_wall_indexes: tuple[int, ...] | None = None,
    ) -> PolygonSiteMeasurementReport:
        """Measure normal and in-plane distances without making acceptance decisions."""
        if center_target <= 0.0 or face_target <= 0.0:
            raise ValueError("Polygon-site target distances must be positive.")
        if near_wall_max_dist_to_plane < 0.0 or alignment_tolerance < 0.0:
            raise ValueError("Near-wall and alignment tolerances must be non-negative.")
        if corridor_lower_percent > corridor_upper_percent:
            raise ValueError("The lower corridor percent cannot exceed the upper percent.")
        if reference_wall_indexes is not None:
            if len(reference_wall_indexes) != len(inter_atoms.points):
                raise ValueError(
                    "reference_wall_indexes must align one-to-one with intercalated atoms."
                )
            invalid_walls: list[int] = [
                wall_index for wall_index in reference_wall_indexes
                if wall_index < 0 or wall_index >= len(carbon_channel.planes)
            ]
            if invalid_walls:
                raise IndexError(
                    f"Reference wall indexes {invalid_walls} are out of range for "
                    f"{len(carbon_channel.planes)} walls."
                )
        sites: tuple[PolygonReferenceSite, ...] = cls.get_reference_sites(carbon_channel)
        by_wall: dict[int, dict[PolygonSiteType, list[PolygonReferenceSite]]] = {}
        for wall_index in range(len(carbon_channel.planes)):
            by_wall[wall_index] = {"center": [], "vertex": [], "edge_midpoint": []}
        for site in sites:
            for association in site.associations:
                by_wall[association.wall_index][site.site_type].append(site)

        atom_ids: tuple[str, ...] = inter_atoms.atom_ids or tuple(
            f"atom-{index + 1:04d}" for index in range(len(inter_atoms.points))
        )
        rows: list[PolygonSiteMeasurement] = []
        violation_ids: list[str] = []
        deviations: list[float] = []
        alignment_counts: dict[str, int] = {"center": 0, "vertex": 0, "edge_midpoint": 0, "interpolated": 0}

        wall_geometry: list[tuple[NDArray[np.float64], float, NDArray[np.float64]]] = []
        for wall_index in range(len(carbon_channel.planes)):
            normal, offset = cls._normalized_plane(carbon_channel, wall_index)
            inward = cls._inward_normal(carbon_channel, wall_index)
            wall_geometry.append((normal, offset, inward))

        for atom_index, (atom_id, raw_point) in enumerate(zip(atom_ids, inter_atoms.points)):
            point: NDArray[np.float64] = np.asarray(raw_point, dtype=np.float64)
            distances: list[float] = [abs(float(np.dot(normal, point) + offset)) for normal, offset, _ in wall_geometry]
            nearest_wall_index: int = int(np.argmin(distances))
            wall_index: int = (
                nearest_wall_index
                if reference_wall_indexes is None
                else reference_wall_indexes[atom_index]
            )
            normal, offset, inward = wall_geometry[wall_index]
            signed: float = float(np.dot(normal, point) + offset)
            projection: NDArray[np.float64] = point - signed * normal
            actual: float = distances[wall_index]
            is_near_wall: bool = actual <= near_wall_max_dist_to_plane

            nearest: dict[PolygonSiteType, tuple[PolygonReferenceSite | None, float]] = {}
            for site_type in ("center", "vertex", "edge_midpoint"):
                nearest[site_type] = cls._nearest_in_plane(
                    projection, by_wall[wall_index][site_type], wall_index, inward
                )
            center_site, d_center = nearest["center"]
            vertex_site, d_vertex = nearest["vertex"]
            edge_site, d_edge = nearest["edge_midpoint"]
            d_face: float = min(d_vertex, d_edge)

            target: float | None = None
            deviation: float | None = None
            deviation_percent: float | None = None
            recommended_shift: float | None = None
            corridor_status: str = "exempt_central"
            alignment_type: str = "central_exempt"
            exemption_reason: str | None = "central atom: polygon-site rule does not apply"
            if is_near_wall:
                exemption_reason = None
                target = cls._interpolated_target(d_center, d_face, center_target, face_target)
                deviation = actual - target
                deviation_percent = deviation / target * 100.0
                recommended_shift = target - actual
                corridor_status = (
                    "within"
                    if corridor_lower_percent <= deviation_percent <= corridor_upper_percent
                    else "violation"
                )
                if corridor_status == "violation":
                    violation_ids.append(atom_id)
                deviations.append(deviation)
                if d_center <= alignment_tolerance:
                    alignment_type = "center"
                elif d_vertex <= alignment_tolerance and d_vertex <= d_edge:
                    alignment_type = "vertex"
                elif d_edge <= alignment_tolerance:
                    alignment_type = "edge_midpoint"
                else:
                    alignment_type = "interpolated"
                alignment_counts[alignment_type] += 1

            values: dict[str, Any] = {
                "atom_id": atom_id,
                "coordinates": cls._coordinate(point),
                "is_near_wall": is_near_wall,
                "nearest_wall_index": nearest_wall_index,
                "nearest_wall_id": f"wall-{nearest_wall_index}",
                "reference_wall_index": wall_index,
                "reference_wall_id": f"wall-{wall_index}",
                "wall_selection_mode": (
                    "nearest" if reference_wall_indexes is None else "explicit_reference"
                ),
                "projection_coordinates": cls._coordinate(projection),
                "nearest_center_site_id": None if center_site is None else center_site.site_id,
                "nearest_center_coordinates": None if center_site is None else center_site.coordinates,
                "nearest_vertex_site_id": None if vertex_site is None else vertex_site.site_id,
                "nearest_vertex_coordinates": None if vertex_site is None else vertex_site.coordinates,
                "nearest_edge_midpoint_site_id": None if edge_site is None else edge_site.site_id,
                "nearest_edge_midpoint_coordinates": None if edge_site is None else edge_site.coordinates,
                "d_center": cls._finite_or_none(d_center),
                "d_vertex": cls._finite_or_none(d_vertex),
                "d_edge_midpoint": cls._finite_or_none(d_edge),
                "d_face": cls._finite_or_none(d_face),
                "actual_normal_distance": actual,
                "target_normal_distance": target,
                "normal_deviation": deviation,
                "deviation_percent": deviation_percent,
                "recommended_inward_shift": recommended_shift,
                "alignment_status": alignment_type != "interpolated" if is_near_wall else None,
                "alignment_type": alignment_type,
                "corridor_status": corridor_status,
                "exemption_reason": exemption_reason,
            }
            rows.append(PolygonSiteMeasurement(values))

        summary: dict[str, Any] = {
            "total_atoms": len(rows),
            "near_wall_atoms": len(deviations),
            "central_exempt_atoms": len(rows) - len(deviations),
            "corridor_violation_count": len(violation_ids),
            "corridor_violation_atom_ids": violation_ids,
            "alignment_counts": alignment_counts,
            "explicit_reference_wall_atoms": (
                0 if reference_wall_indexes is None else len(reference_wall_indexes)
            ),
            "normal_deviation_min": None if not deviations else min(deviations),
            "normal_deviation_mean": None if not deviations else float(np.mean(deviations)),
            "normal_deviation_max": None if not deviations else max(deviations),
        }
        return PolygonSiteMeasurementReport(tuple(rows), summary)

    @classmethod
    def _extract_sites(cls, carbon_channel: ICarbonHoneycombChannel) -> tuple[PolygonReferenceSite, ...]:
        points, source_indexes = cls._unique_points(carbon_channel.points)
        atom_ids: tuple[str, ...] = tuple(cls._stable_id("carbon", point) for point in points)
        memberships: list[tuple[PolygonWallAssociation, ...]] = [
            cls._point_associations(carbon_channel, point) for point in points
        ]
        sites: list[PolygonReferenceSite] = []
        for index, point in enumerate(points):
            sites.append(PolygonReferenceSite(
                site_id=cls._stable_id("vertex", point),
                site_type="vertex",
                coordinates=cls._coordinate(point),
                associations=memberships[index],
                carbon_atom_indexes=source_indexes[index],
                carbon_atom_ids=(atom_ids[index],),
            ))

        edges: tuple[tuple[int, int], ...] = cls._build_edges(points)
        for first, second in edges:
            midpoint: NDArray[np.float64] = (points[first] + points[second]) / 2.0
            common_walls: set[int] = {
                item.wall_index for item in memberships[first]
            } & {item.wall_index for item in memberships[second]}
            associations: tuple[PolygonWallAssociation, ...] = cls._associations_for_walls(
                carbon_channel, midpoint, common_walls
            )
            sites.append(PolygonReferenceSite(
                site_id=cls._stable_id("edge", midpoint, (atom_ids[first], atom_ids[second])),
                site_type="edge_midpoint",
                coordinates=cls._coordinate(midpoint),
                associations=associations,
                carbon_atom_indexes=tuple(sorted(source_indexes[first] + source_indexes[second])),
                carbon_atom_ids=tuple(sorted((atom_ids[first], atom_ids[second]))),
            ))

        for cycle in cls._find_chordless_rings(len(points), edges):
            ring_points: NDArray[np.float64] = points[list(cycle)]
            centroid: NDArray[np.float64] = np.mean(ring_points, axis=0)
            ring_vertex_ids: tuple[str, ...] = tuple(sorted(atom_ids[index] for index in cycle))
            ring_id: str = cls._stable_id("ring", centroid, ring_vertex_ids)
            normal: NDArray[np.float64] = cls._best_fit_inward_normal(
                ring_points, centroid, np.asarray(carbon_channel.channel_center, dtype=np.float64)
            )
            wall_index: int = cls._nearest_wall_index(carbon_channel, centroid)
            sites.append(PolygonReferenceSite(
                site_id=f"center-{ring_id}",
                site_type="center",
                coordinates=cls._coordinate(centroid),
                associations=(PolygonWallAssociation(wall_index, cls._coordinate(normal)),),
                carbon_atom_indexes=tuple(sorted(index for vertex in cycle for index in source_indexes[vertex])),
                carbon_atom_ids=ring_vertex_ids,
                ring_id=ring_id,
                ring_vertex_ids=ring_vertex_ids,
            ))
        return tuple(sorted(sites, key=lambda site: (site.site_type, site.site_id)))

    @classmethod
    def _unique_points(
        cls, points: NDArray[np.float64]
    ) -> tuple[NDArray[np.float64], tuple[tuple[int, ...], ...]]:
        grouped: dict[tuple[float, float, float], list[int]] = {}
        for index, point in enumerate(points):
            key: tuple[float, float, float] = cls._coordinate(np.round(point, 6))
            grouped.setdefault(key, []).append(index)
        keys: list[tuple[float, float, float]] = sorted(grouped)
        return np.asarray(keys, dtype=np.float64), tuple(tuple(grouped[key]) for key in keys)

    @classmethod
    def _build_edges(cls, points: NDArray[np.float64]) -> tuple[tuple[int, int], ...]:
        edges: list[tuple[int, int]] = []
        for first in range(len(points)):
            distances: NDArray[np.float64] = np.linalg.norm(points[first + 1:] - points[first], axis=1)
            edges.extend(
                (first, first + 1 + offset)
                for offset in np.flatnonzero((distances > cls.ZERO_TOLERANCE) & (distances < cls.BOND_MAX_DISTANCE))
            )
        return tuple(edges)

    @classmethod
    def _find_chordless_rings(
        cls, vertex_count: int, edges: tuple[tuple[int, int], ...]
    ) -> tuple[tuple[int, ...], ...]:
        adjacency: list[set[int]] = [set() for _ in range(vertex_count)]
        for first, second in edges:
            adjacency[first].add(second)
            adjacency[second].add(first)
        cycles: set[tuple[int, ...]] = set()
        for start in range(vertex_count):
            stack: list[tuple[int, tuple[int, ...]]] = [(start, (start,))]
            while stack:
                current, path = stack.pop()
                for neighbor in adjacency[current]:
                    if neighbor == start and len(path) in (5, 6):
                        canonical: tuple[int, ...] = cls._canonical_cycle(path)
                        induced_edges: int = sum(
                            1 for index, first in enumerate(canonical)
                            for second in canonical[index + 1:] if second in adjacency[first]
                        )
                        if induced_edges == len(canonical):
                            cycles.add(canonical)
                    elif neighbor > start and neighbor not in path and len(path) < 6:
                        stack.append((neighbor, path + (neighbor,)))
        return tuple(sorted(cycles))

    @staticmethod
    def _canonical_cycle(cycle: tuple[int, ...]) -> tuple[int, ...]:
        rotations: list[tuple[int, ...]] = []
        for values in (cycle, tuple(reversed(cycle))):
            rotations.extend(values[index:] + values[:index] for index in range(len(values)))
        return min(rotations)

    @classmethod
    def _point_associations(
        cls, carbon_channel: ICarbonHoneycombChannel, point: NDArray[np.float64]
    ) -> tuple[PolygonWallAssociation, ...]:
        walls: set[int] = set()
        for wall_index in range(len(carbon_channel.planes)):
            normal, offset = cls._normalized_plane(carbon_channel, wall_index)
            if abs(float(np.dot(normal, point) + offset)) <= cls.PLANE_MEMBERSHIP_TOLERANCE:
                walls.add(wall_index)
        return cls._associations_for_walls(carbon_channel, point, walls)

    @classmethod
    def _associations_for_walls(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        point: NDArray[np.float64],
        walls: set[int],
    ) -> tuple[PolygonWallAssociation, ...]:
        if not walls:
            walls = {cls._nearest_wall_index(carbon_channel, point)}
        return tuple(
            PolygonWallAssociation(wall, cls._coordinate(cls._inward_normal(carbon_channel, wall)))
            for wall in sorted(walls)
        )

    @classmethod
    def _nearest_wall_index(
        cls, carbon_channel: ICarbonHoneycombChannel, point: NDArray[np.float64]
    ) -> int:
        distances: list[float] = []
        for wall_index in range(len(carbon_channel.planes)):
            normal, offset = cls._normalized_plane(carbon_channel, wall_index)
            distances.append(abs(float(np.dot(normal, point) + offset)))
        return int(np.argmin(distances))

    @staticmethod
    def _normalized_plane(
        carbon_channel: ICarbonHoneycombChannel, wall_index: int
    ) -> tuple[NDArray[np.float64], float]:
        a, b, c, d = carbon_channel.planes[wall_index].plane_params
        raw: NDArray[np.float64] = np.asarray((a, b, c), dtype=np.float64)
        magnitude: float = float(np.linalg.norm(raw))
        if magnitude <= 1e-12:
            raise ValueError(f"Wall {wall_index} has an invalid plane normal.")
        return raw / magnitude, float(d) / magnitude

    @classmethod
    def _inward_normal(
        cls, carbon_channel: ICarbonHoneycombChannel, wall_index: int
    ) -> NDArray[np.float64]:
        normal, _ = cls._normalized_plane(carbon_channel, wall_index)
        plane_center: NDArray[np.float64] = np.asarray(carbon_channel.planes[wall_index].center, dtype=np.float64)
        toward_center: NDArray[np.float64] = np.asarray(carbon_channel.channel_center, dtype=np.float64) - plane_center
        return normal if float(np.dot(normal, toward_center)) >= 0.0 else -normal

    @staticmethod
    def _best_fit_inward_normal(
        points: NDArray[np.float64], centroid: NDArray[np.float64], channel_center: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        _, _, vh = np.linalg.svd(points - centroid, full_matrices=False)
        normal: NDArray[np.float64] = vh[-1]
        if float(np.dot(normal, channel_center - centroid)) < 0.0:
            normal = -normal
        return normal / np.linalg.norm(normal)

    @classmethod
    def _nearest_in_plane(
        cls,
        projection: NDArray[np.float64],
        sites: list[PolygonReferenceSite],
        wall_index: int,
        fallback_normal: NDArray[np.float64],
    ) -> tuple[PolygonReferenceSite | None, float]:
        if not sites:
            return None, float("inf")
        distances: list[float] = []
        for site in sites:
            association = next(
                (
                    item for item in site.associations
                    if item.wall_index == wall_index
                ),
                None,
            )
            normal: NDArray[np.float64] = (
                fallback_normal
                if association is None
                else np.asarray(association.inward_normal, dtype=np.float64)
            )
            delta: NDArray[np.float64] = projection - np.asarray(site.coordinates, dtype=np.float64)
            in_plane: NDArray[np.float64] = delta - np.dot(delta, normal) * normal
            distances.append(float(np.linalg.norm(in_plane)))
        index: int = int(np.argmin(distances))
        return sites[index], distances[index]

    @classmethod
    def _interpolated_target(
        cls, d_center: float, d_face: float, center_target: float, face_target: float
    ) -> float:
        if d_center <= cls.ZERO_TOLERANCE:
            return center_target
        if d_face <= cls.ZERO_TOLERANCE:
            return face_target
        if not np.isfinite(d_center):
            return face_target
        if not np.isfinite(d_face):
            return center_target
        weight_center: float = d_face / (d_center + d_face)
        return weight_center * center_target + (1.0 - weight_center) * face_target

    @staticmethod
    def _coordinate(point: NDArray[np.float64]) -> tuple[float, float, float]:
        return (float(point[0]), float(point[1]), float(point[2]))

    @staticmethod
    def _finite_or_none(value: float) -> float | None:
        return value if np.isfinite(value) else None

    @classmethod
    def _stable_id(
        cls,
        prefix: str,
        point: NDArray[np.float64],
        provenance: tuple[str, ...] = (),
    ) -> str:
        coordinate_key: str = ",".join(f"{value:.6f}" for value in point)
        digest: str = sha1(f"{coordinate_key}|{'|'.join(sorted(provenance))}".encode()).hexdigest()[:12]
        return f"{prefix}-{digest}"
