"""Build deterministic data for two-dimensional intercalated-channel schemes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import atan2
from pathlib import Path
import re
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment

from src.entities import (
    Coordinate2D,
    Coordinate3D,
    IntercalatedChannelSchemeData,
    IntercalatedSchemeAtom,
    DimensionOrientation,
    PeriodicitySource,
    SchemeDimensionSegment,
)
from src.interfaces import (
    ICarbonHoneycombChannel,
    IIntercalatedChannelSchemeBuilder,
    IPoints,
)
from src.services import Constants, ConstantsAtomParams
from src.projects.intercalation_and_sorption.structure_operations.inter_atoms_file_manager import (
    InterAtomsFileManager,
)


@dataclass(frozen=True)
class _Layer:
    """Represent a z layer while preserving source-row indexes."""

    z: float
    source_indexes: tuple[int, ...]
    xy: tuple[Coordinate2D, ...]


@dataclass(frozen=True)
class _NearestInter:
    """Represent one nearest intercalated-neighbour result."""

    distance: float
    source_index: int
    base_coordinates: Coordinate3D
    shifted_coordinates: Coordinate3D
    periodic_shift: int


class IntercalatedChannelSchemeBuilder(IIntercalatedChannelSchemeBuilder):
    """Prepare immutable geometry and measurement data for the scheme renderer."""

    LAYER_Z_TOLERANCE: float = 1e-3
    LAYER_XY_MATCH_TOLERANCE: float = 0.1
    DIMENSION_TOLERANCE: float = 1e-3
    POINT_IN_CHANNEL_TOLERANCE: float = 0.1
    MAX_PERIOD_LAYERS: int = 4
    REPEAT_SPACING_TOLERANCE: float = 0.1
    _STACKING_BY_PERIOD: dict[int, str] = {
        1: "AA",
        2: "ABAB",
        3: "ABCABC",
        4: "ABCDABCD",
    }
    _SERVICE_FILE_NAMES: frozenset[str] = frozenset({
        Constants.file_names.PLANE_COORDINATES_CSV_FILE.lower(),
        Constants.file_names.OPPOSITE_CENTERS_COORDINATES_CSV_FILE.lower(),
        Constants.file_names.OPPOSITE_FACES_COORDINATES_CSV_FILE.lower(),
        Constants.file_names.CHANNEL_COORDINATES_CSV_FILE.lower(),
        Constants.file_names.FULL_CHANNEL_COORDINATES_CSV_FILE.lower(),
        Constants.file_names.ALL_CHANNELS_COORDINATES_CSV_FILE.lower(),
        Constants.file_names.CHANNEL_DETAILS_XLSX_FILE.lower(),
        Constants.file_names.C_ALL_CHANNELS_COORDINATES_DAT_FILE.lower(),
        Constants.file_names.INIT_DAT_FILE.lower(),
    })

    def build(
        self,
        carbon_channel: ICarbonHoneycombChannel,
        inter_atoms: IPoints,
        atom_params: ConstantsAtomParams,
        file_name: str,
    ) -> IntercalatedChannelSchemeData:
        """Build data for both 2D intercalated-channel schemes."""
        coordinates: NDArray[np.float64] = np.asarray(inter_atoms.points, dtype=np.float64)
        self._validate_input(coordinates, file_name)

        boundary: tuple[Coordinate2D, ...] = self._build_channel_boundary(carbon_channel)
        self._validate_one_channel(coordinates, boundary)
        layers: tuple[_Layer, ...] = self._build_layers(coordinates)
        template_indexes: tuple[int, ...] = self._assign_template_indexes(layers)
        filename_period: int | None = self._filename_period(file_name)
        period, periodicity_source, warnings = self._detect_period(
            layers, filename_period
        )
        representative_layer_count: int = period if period is not None else len(layers)
        representative_indexes: tuple[int, ...] = tuple(
            source_index
            for layer in layers[:representative_layer_count]
            for source_index in layer.source_indexes
        )
        repeat_length: float | None = self._calculate_repeat_length(
            layers, period, periodicity_source
        )
        if period is not None and repeat_length is None:
            warnings.append("Repeat length could not be established; finite neighbours are used.")

        equilibrium_distance: float = (
            float(carbon_channel.ave_dist_between_closest_atoms)
            + float(atom_params.DIST_BETWEEN_ATOMS)
        ) / 2.0
        if not np.isfinite(equilibrium_distance):
            raise ValueError("Failed to calculate the structure-aware intercalation distance.")

        atom_ids: tuple[str, ...] = inter_atoms.atom_ids or tuple(
            f"atom-{index + 1:04d}" for index in range(len(coordinates))
        )
        layer_by_source: dict[int, int] = {
            source_index: layer_index
            for layer_index, layer in enumerate(layers)
            for source_index in layer.source_indexes
        }
        representative_set: set[int] = set(representative_indexes)
        atoms: list[IntercalatedSchemeAtom] = []
        for source_index, point in enumerate(coordinates):
            layer_index: int = layer_by_source[source_index]
            template_index: int = template_indexes[layer_index]
            atoms.append(
                IntercalatedSchemeAtom(
                    source_index=source_index,
                    atom_id=atom_ids[source_index],
                    coordinates=self._coordinate3d(point),
                    layer_index=layer_index,
                    template_index=template_index,
                    template_label=self._template_label(template_index),
                    is_representative=source_index in representative_set,
                )
            )

        measured_atoms: list[IntercalatedSchemeAtom] = []
        for atom in atoms:
            if not atom.is_representative:
                measured_atoms.append(atom)
                continue
            measured_atoms.append(
                self._measure_atom(
                    atom=atom,
                    atoms=atoms,
                    representative_indexes=representative_indexes,
                    carbon_channel=carbon_channel,
                    boundary=boundary,
                    equilibrium_distance=equilibrium_distance,
                    repeat_length=repeat_length,
                )
            )

        dimensions: tuple[SchemeDimensionSegment, ...] = self._build_dimensions(
            measured_atoms, representative_indexes, boundary
        )
        carbon_projections: tuple[tuple[float, float, int], ...] = (
            self._unique_carbon_projections(carbon_channel.points)
        )
        stacking_type: str | None = (
            self._STACKING_BY_PERIOD[period] if period is not None else None
        )

        return IntercalatedChannelSchemeData(
            file_name=Path(file_name).name,
            element_symbol=atom_params.ATOM_SYMBOL,
            atom_diameter=float(atom_params.DIST_BETWEEN_ATOMS),
            equilibrium_inter_carbon_distance=equilibrium_distance,
            carbon_projections=carbon_projections,
            channel_boundary=boundary,
            atoms=tuple(measured_atoms),
            representative_indexes=representative_indexes,
            dimension_segments=dimensions,
            stacking_type=stacking_type,
            repeat_length=repeat_length,
            periodicity_source=periodicity_source,
            warnings=tuple(warnings),
        )

    @classmethod
    def _validate_input(
        cls, coordinates: NDArray[np.float64], file_name: str
    ) -> None:
        """Validate parsed coordinates and reject known non-model inputs."""
        basename: str = Path(file_name).name
        suffix: str = Path(basename).suffix.lower().lstrip(".")
        if suffix not in InterAtomsFileManager.SUPPORTED_COORDINATE_FORMATS:
            raise ValueError("Only one-channel CSV, XLSX and DAT files are supported.")
        if coordinates.ndim != 2 or coordinates.shape[1] != 3:
            raise ValueError(f"Intercalated coordinates must have shape (N, 3), got {coordinates.shape}.")
        if len(coordinates) == 0:
            raise ValueError("The selected file contains no intercalated atoms.")
        if not np.all(np.isfinite(coordinates)):
            raise ValueError("Intercalated coordinates must contain only finite values.")

        lower_name: str = basename.lower()
        current_match: re.Match[str] | None = InterAtomsFileManager.FINAL_FILE_NAME_PATTERN.match(
            basename
        )
        legacy_match: re.Match[str] | None = (
            InterAtomsFileManager.LEGACY_FINAL_FILE_NAME_PATTERN.match(basename)
        )
        channels: str | None = None
        if current_match is not None:
            channels = current_match.group("num_of_channels")
        elif legacy_match is not None:
            channels = legacy_match.group("num_of_channels")
        if (
            channels == "all"
            or lower_name.startswith("all_ch-")
            or lower_name.startswith("final_all_ch-")
            or "all-channels" in lower_name
            or "all_channels" in lower_name
        ):
            raise ValueError("All-channel coordinate files are not supported by this scheme.")
        if lower_name in cls._SERVICE_FILE_NAMES:
            raise ValueError("Select a final one-channel model, not a service or carbon file.")
        if any(token in lower_name for token in ("distance", "details", "carbon", "cell")):
            raise ValueError("The selected file is not a one-channel coordinate model.")

    @classmethod
    def _build_channel_boundary(
        cls, carbon_channel: ICarbonHoneycombChannel
    ) -> tuple[Coordinate2D, ...]:
        """Intersect ordered wall planes at the channel-centre z coordinate."""
        planes = carbon_channel.planes
        if len(planes) < 3:
            raise ValueError("At least three channel wall planes are required.")
        center: NDArray[np.float64] = np.asarray(carbon_channel.channel_center, dtype=np.float64)
        ordered_planes = sorted(
            planes,
            key=lambda plane: atan2(
                float(plane.center[1] - center[1]),
                float(plane.center[0] - center[0]),
            ),
        )
        lines: list[tuple[float, float, float]] = []
        for plane in ordered_planes:
            a, b, c, d = (float(value) for value in plane.plane_params)
            if float(np.hypot(a, b)) <= cls.DIMENSION_TOLERANCE:
                raise ValueError("A channel wall cannot be projected to a stable xOy line.")
            lines.append((a, b, c * float(center[2]) + d))

        vertices: list[Coordinate2D] = []
        for index, first in enumerate(lines):
            second: tuple[float, float, float] = lines[(index + 1) % len(lines)]
            determinant: float = first[0] * second[1] - second[0] * first[1]
            if abs(determinant) <= 1e-10:
                raise ValueError("Adjacent channel walls do not define a closed boundary.")
            x_coord: float = (first[1] * second[2] - second[1] * first[2]) / determinant
            y_coord: float = (second[0] * first[2] - first[0] * second[2]) / determinant
            vertices.append((x_coord, y_coord))

        if abs(cls._polygon_area(tuple(vertices))) <= cls.DIMENSION_TOLERANCE:
            raise ValueError("The projected channel boundary has zero area.")
        return tuple(vertices)

    @classmethod
    def _validate_one_channel(
        cls,
        coordinates: NDArray[np.float64],
        boundary: tuple[Coordinate2D, ...],
    ) -> None:
        """Require every intercalated projection to belong to the first channel."""
        outside: list[int] = []
        for index, point in enumerate(coordinates[:, :2]):
            point_xy: Coordinate2D = (float(point[0]), float(point[1]))
            if cls._point_in_polygon(point_xy, boundary):
                continue
            boundary_distance: float = min(
                cls._point_to_segment_distance(
                    point_xy, boundary[edge], boundary[(edge + 1) % len(boundary)]
                )
                for edge in range(len(boundary))
            )
            if boundary_distance > cls.POINT_IN_CHANNEL_TOLERANCE:
                outside.append(index)
        if outside:
            preview: str = ", ".join(str(index) for index in outside[:5])
            raise ValueError(
                "Coordinates do not belong to one carbon channel; outside row indexes: "
                f"{preview}."
            )

    @classmethod
    def _build_layers(cls, coordinates: NDArray[np.float64]) -> tuple[_Layer, ...]:
        """Group points into deterministic z layers."""
        sorted_indexes: NDArray[np.int64] = np.argsort(coordinates[:, 2], kind="stable")
        groups: list[list[int]] = []
        for source_index_value in sorted_indexes:
            source_index: int = int(source_index_value)
            if not groups:
                groups.append([source_index])
                continue
            anchor_z: float = float(coordinates[groups[-1][0], 2])
            if abs(float(coordinates[source_index, 2]) - anchor_z) <= cls.LAYER_Z_TOLERANCE:
                groups[-1].append(source_index)
            else:
                groups.append([source_index])

        return tuple(
            _Layer(
                z=float(np.mean(coordinates[indexes, 2])),
                source_indexes=tuple(indexes),
                xy=tuple(
                    sorted(
                        (float(coordinates[index, 0]), float(coordinates[index, 1]))
                        for index in indexes
                    )
                ),
            )
            for indexes in groups
        )

    @classmethod
    def _layers_match(cls, first: _Layer, second: _Layer) -> bool:
        """Compare layer multisets independently of atom order."""
        if len(first.xy) != len(second.xy):
            return False
        first_xy: NDArray[np.float64] = np.asarray(first.xy, dtype=np.float64)
        second_xy: NDArray[np.float64] = np.asarray(second.xy, dtype=np.float64)
        distances: NDArray[np.float64] = np.linalg.norm(
            first_xy[:, None, :] - second_xy[None, :, :], axis=2
        )
        row_indexes, column_indexes = linear_sum_assignment(distances)
        return bool(
            np.all(distances[row_indexes, column_indexes] <= cls.LAYER_XY_MATCH_TOLERANCE)
        )

    @classmethod
    def _assign_template_indexes(cls, layers: tuple[_Layer, ...]) -> tuple[int, ...]:
        """Assign equal layer geometries the same deterministic template index."""
        representatives: list[_Layer] = []
        result: list[int] = []
        for layer in layers:
            matching_index: int | None = next(
                (
                    index
                    for index, representative in enumerate(representatives)
                    if cls._layers_match(layer, representative)
                ),
                None,
            )
            if matching_index is None:
                matching_index = len(representatives)
                representatives.append(layer)
            result.append(matching_index)
        return tuple(result)

    @classmethod
    def _detect_period(
        cls, layers: tuple[_Layer, ...], filename_period: int | None
    ) -> tuple[int | None, PeriodicitySource, list[str]]:
        """Detect the shortest repeat and retain filename metadata only as a hint."""
        warnings: list[str] = []
        geometry_period: int | None = None
        for period in range(1, min(cls.MAX_PERIOD_LAYERS, len(layers) - 1) + 1):
            comparisons: list[bool] = [
                cls._layers_match(layers[index], layers[index + period])
                for index in range(len(layers) - period)
            ]
            if comparisons and all(comparisons):
                geometry_period = period
                break

        if geometry_period is not None:
            if filename_period is not None and filename_period != geometry_period:
                warnings.append(
                    "Filename stacking hint conflicts with geometry; geometry is used."
                )
            return geometry_period, "geometry-confirmed", warnings

        if filename_period is not None and len(layers) >= filename_period:
            comparisons = [
                cls._layers_match(layers[index], layers[index + filename_period])
                for index in range(len(layers) - filename_period)
            ]
            if not comparisons or all(comparisons):
                warnings.append("Periodicity is filename-derived and not geometry-confirmed.")
                return filename_period, "filename-derived", warnings

        warnings.append("Periodicity not established; finite neighbours are used.")
        return None, "unknown", warnings

    @classmethod
    def _filename_period(cls, file_name: str) -> int | None:
        """Extract a normalized stacking-period hint from supported file names."""
        basename: str = Path(file_name).name
        match: re.Match[str] | None = InterAtomsFileManager.FINAL_FILE_NAME_PATTERN.match(basename)
        if match is None:
            match = InterAtomsFileManager.LEGACY_FINAL_FILE_NAME_PATTERN.match(basename)
        stacking: str | None = match.group("stacking") if match is not None else None
        if stacking is None:
            fallback: re.Match[str] | None = re.search(
                r"(?:^|-)(AA|ABAB|ABCABC|ABCDABCD|ABC|ABCD)(?:-|\.)",
                basename,
                flags=re.IGNORECASE,
            )
            stacking = fallback.group(1) if fallback is not None else None
        if stacking is None:
            return None
        normalized: str = stacking.upper()
        return {
            "AA": 1,
            "ABAB": 2,
            "ABC": 3,
            "ABCABC": 3,
            "ABCD": 4,
            "ABCDABCD": 4,
        }.get(normalized)

    @classmethod
    def _calculate_repeat_length(
        cls,
        layers: tuple[_Layer, ...],
        period: int | None,
        periodicity_source: PeriodicitySource,
    ) -> float | None:
        """Calculate a reliable z repeat length when available."""
        if period is None:
            return None
        if periodicity_source == "geometry-confirmed":
            differences: list[float] = [
                layers[index + period].z - layers[index].z
                for index in range(len(layers) - period)
                if cls._layers_match(layers[index], layers[index + period])
            ]
            if differences:
                repeat_length: float = float(np.median(differences))
                return repeat_length if repeat_length > cls.LAYER_Z_TOLERANCE else None
            return None

        spacings: NDArray[np.float64] = np.diff(
            np.asarray([layer.z for layer in layers], dtype=np.float64)
        )
        if len(spacings) == 0:
            return None
        median_spacing: float = float(np.median(spacings))
        if np.max(np.abs(spacings - median_spacing)) > cls.REPEAT_SPACING_TOLERANCE:
            return None
        repeat_length = median_spacing * period
        return repeat_length if repeat_length > cls.LAYER_Z_TOLERANCE else None

    @classmethod
    def _measure_atom(
        cls,
        atom: IntercalatedSchemeAtom,
        atoms: list[IntercalatedSchemeAtom],
        representative_indexes: tuple[int, ...],
        carbon_channel: ICarbonHoneycombChannel,
        boundary: tuple[Coordinate2D, ...],
        equilibrium_distance: float,
        repeat_length: float | None,
    ) -> IntercalatedSchemeAtom:
        """Calculate unrounded local measurements for one representative atom."""
        point: NDArray[np.float64] = np.asarray(atom.coordinates, dtype=np.float64)
        plane_distance, plane_projection = cls._nearest_plane(point, carbon_channel)
        carbon_points: NDArray[np.float64] = np.asarray(carbon_channel.points, dtype=np.float64)
        carbon_distances: NDArray[np.float64] = np.linalg.norm(carbon_points - point, axis=1)
        carbon_index: int = int(np.argmin(carbon_distances))
        nearest_inter: _NearestInter | None = cls._nearest_inter(
            atom, atoms, representative_indexes, repeat_length
        )
        vertex_distances: NDArray[np.float64] = np.linalg.norm(
            np.asarray(boundary, dtype=np.float64) - point[:2], axis=1
        )
        vertex_index: int = int(np.argmin(vertex_distances))

        return replace(
            atom,
            is_near_wall=float(carbon_distances[carbon_index]) <= equilibrium_distance * 1.5,
            min_distance_to_plane=plane_distance,
            nearest_wall_projection=plane_projection,
            min_distance_to_carbon=float(carbon_distances[carbon_index]),
            nearest_carbon_coordinates=cls._coordinate3d(carbon_points[carbon_index]),
            min_distance_to_inter=None if nearest_inter is None else nearest_inter.distance,
            nearest_inter_source_index=None if nearest_inter is None else nearest_inter.source_index,
            nearest_inter_atom_id=(
                None if nearest_inter is None else atoms[nearest_inter.source_index].atom_id
            ),
            nearest_inter_base_coordinates=(
                None if nearest_inter is None else nearest_inter.base_coordinates
            ),
            nearest_inter_coordinates=(
                None if nearest_inter is None else nearest_inter.shifted_coordinates
            ),
            nearest_inter_periodic_shift=(
                0 if nearest_inter is None else nearest_inter.periodic_shift
            ),
            nearest_edge_vertex_index=vertex_index,
            nearest_edge_vertex_coordinates=boundary[vertex_index],
            distance_to_edge_vertex_xy=float(vertex_distances[vertex_index]),
        )

    @classmethod
    def _nearest_plane(
        cls,
        point: NDArray[np.float64],
        carbon_channel: ICarbonHoneycombChannel,
    ) -> tuple[float, Coordinate3D]:
        """Return the true nearest wall-plane distance and orthogonal projection."""
        candidates: list[tuple[float, Coordinate3D]] = []
        for plane in carbon_channel.planes:
            params: NDArray[np.float64] = np.asarray(plane.plane_params, dtype=np.float64)
            normal: NDArray[np.float64] = params[:3]
            normal_squared: float = float(np.dot(normal, normal))
            if normal_squared <= 1e-20:
                continue
            signed_numerator: float = float(np.dot(normal, point) + params[3])
            projection: NDArray[np.float64] = point - normal * signed_numerator / normal_squared
            distance: float = abs(signed_numerator) / float(np.sqrt(normal_squared))
            candidates.append((distance, cls._coordinate3d(projection)))
        if not candidates:
            raise ValueError("No valid carbon wall planes are available.")
        return min(candidates, key=lambda candidate: candidate[0])

    @classmethod
    def _nearest_inter(
        cls,
        atom: IntercalatedSchemeAtom,
        atoms: list[IntercalatedSchemeAtom],
        representative_indexes: tuple[int, ...],
        repeat_length: float | None,
    ) -> _NearestInter | None:
        """Find a finite or periodic nearest intercalated neighbour."""
        source: NDArray[np.float64] = np.asarray(atom.coordinates, dtype=np.float64)
        candidate_indexes: tuple[int, ...] = (
            representative_indexes if repeat_length is not None else tuple(range(len(atoms)))
        )
        shifts: tuple[int, ...] = (-1, 0, 1) if repeat_length is not None else (0,)
        candidates: list[tuple[float, int, int, _NearestInter]] = []
        for periodic_shift in shifts:
            z_shift: float = 0.0 if repeat_length is None else periodic_shift * repeat_length
            for candidate_index in candidate_indexes:
                if candidate_index == atom.source_index and periodic_shift == 0:
                    continue
                base: Coordinate3D = atoms[candidate_index].coordinates
                shifted: Coordinate3D = (base[0], base[1], base[2] + z_shift)
                distance: float = float(
                    np.linalg.norm(np.asarray(shifted, dtype=np.float64) - source)
                )
                result = _NearestInter(
                    distance=distance,
                    source_index=candidate_index,
                    base_coordinates=base,
                    shifted_coordinates=shifted,
                    periodic_shift=periodic_shift,
                )
                candidates.append(
                    (distance, abs(periodic_shift), candidate_index, result)
                )
        if not candidates:
            return None
        return min(candidates, key=lambda candidate: candidate[:3])[3]

    @classmethod
    def _build_dimensions(
        cls,
        atoms: list[IntercalatedSchemeAtom],
        representative_indexes: tuple[int, ...],
        boundary: tuple[Coordinate2D, ...],
    ) -> tuple[SchemeDimensionSegment, ...]:
        """Build coordinate-level chains and exact directional boundary gaps."""
        representative_atoms: list[IntercalatedSchemeAtom] = [
            atoms[index] for index in representative_indexes
        ]
        x_values: list[tuple[float, str]] = [
            (atom.coordinates[0], f"atom:{atom.source_index}")
            for atom in representative_atoms
        ] + [(vertex[0], f"edge:{index}") for index, vertex in enumerate(boundary)]
        y_values: list[tuple[float, str]] = [
            (atom.coordinates[1], f"atom:{atom.source_index}")
            for atom in representative_atoms
        ] + [(vertex[1], f"edge:{index}") for index, vertex in enumerate(boundary)]
        x_levels = cls._merge_levels(x_values)
        y_levels = cls._merge_levels(y_values)
        x_min: float = min(vertex[0] for vertex in boundary)
        x_max: float = max(vertex[0] for vertex in boundary)
        y_min: float = min(vertex[1] for vertex in boundary)
        y_max: float = max(vertex[1] for vertex in boundary)
        margin: float = max(x_max - x_min, y_max - y_min) * 0.08
        dimensions: list[SchemeDimensionSegment] = []

        for index, (first, second) in enumerate(zip(x_levels, x_levels[1:])):
            value: float = second[0] - first[0]
            if value <= cls.DIMENSION_TOLERANCE:
                continue
            y_coord: float = y_min - margin * (1.0 + index * 0.16)
            dimensions.append(
                SchemeDimensionSegment(
                    orientation="x",
                    kind="coordinate_level",
                    start=(first[0], y_coord),
                    end=(second[0], y_coord),
                    value=value,
                    source_ids=tuple(sorted(set(first[1] + second[1]))),
                )
            )
        for index, (first, second) in enumerate(zip(y_levels, y_levels[1:])):
            value = second[0] - first[0]
            if value <= cls.DIMENSION_TOLERANCE:
                continue
            x_coord: float = x_max + margin * (1.0 + index * 0.16)
            dimensions.append(
                SchemeDimensionSegment(
                    orientation="y",
                    kind="coordinate_level",
                    start=(x_coord, first[0]),
                    end=(x_coord, second[0]),
                    value=value,
                    source_ids=tuple(sorted(set(first[1] + second[1]))),
                )
            )

        dimensions.extend(cls._build_boundary_gaps(representative_atoms, boundary))
        return tuple(dimensions)

    @classmethod
    def _build_boundary_gaps(
        cls,
        atoms: list[IntercalatedSchemeAtom],
        boundary: tuple[Coordinate2D, ...],
    ) -> list[SchemeDimensionSegment]:
        """Measure extreme atom projections to directional contour intersections."""
        x_coordinates: list[float] = [atom.coordinates[0] for atom in atoms]
        y_coordinates: list[float] = [atom.coordinates[1] for atom in atoms]
        extremes: tuple[
            tuple[DimensionOrientation, float, Literal["negative", "positive"]], ...
        ] = (
            ("x", min(x_coordinates), "negative"),
            ("x", max(x_coordinates), "positive"),
            ("y", min(y_coordinates), "negative"),
            ("y", max(y_coordinates), "positive"),
        )
        result: list[SchemeDimensionSegment] = []
        seen: set[tuple[int, int, int, int]] = set()
        for orientation, extreme, direction in extremes:
            coordinate_index: int = 0 if orientation == "x" else 1
            for atom in atoms:
                if abs(atom.coordinates[coordinate_index] - extreme) > cls.DIMENSION_TOLERANCE:
                    continue
                start: Coordinate2D = (atom.coordinates[0], atom.coordinates[1])
                end: Coordinate2D | None = cls._ray_boundary_intersection(
                    start, boundary, orientation, direction
                )
                if end is None:
                    continue
                value: float = abs(end[coordinate_index] - start[coordinate_index])
                if value <= cls.DIMENSION_TOLERANCE:
                    continue
                scale: float = 1.0 / cls.DIMENSION_TOLERANCE
                key: tuple[int, int, int, int] = (
                    round(start[0] * scale),
                    round(start[1] * scale),
                    round(end[0] * scale),
                    round(end[1] * scale),
                )
                if key in seen:
                    continue
                seen.add(key)
                result.append(
                    SchemeDimensionSegment(
                        orientation="x" if orientation == "x" else "y",
                        kind="boundary_gap",
                        start=start,
                        end=end,
                        value=value,
                        source_ids=(f"atom:{atom.source_index}", f"boundary:{direction}"),
                    )
                )
        return result

    @classmethod
    def _ray_boundary_intersection(
        cls,
        start: Coordinate2D,
        boundary: tuple[Coordinate2D, ...],
        orientation: DimensionOrientation,
        direction: Literal["negative", "positive"],
    ) -> Coordinate2D | None:
        """Return the first polygon-boundary intersection along an axis-aligned ray."""
        intersections: list[float] = []
        fixed: float = start[1] if orientation == "x" else start[0]
        for index, first in enumerate(boundary):
            second: Coordinate2D = boundary[(index + 1) % len(boundary)]
            first_variable: float = first[1] if orientation == "x" else first[0]
            second_variable: float = second[1] if orientation == "x" else second[0]
            first_output: float = first[0] if orientation == "x" else first[1]
            second_output: float = second[0] if orientation == "x" else second[1]
            delta: float = second_variable - first_variable
            if abs(delta) <= cls.DIMENSION_TOLERANCE:
                if abs(fixed - first_variable) <= cls.DIMENSION_TOLERANCE:
                    intersections.extend((first_output, second_output))
                continue
            parameter: float = (fixed - first_variable) / delta
            if -cls.DIMENSION_TOLERANCE <= parameter <= 1.0 + cls.DIMENSION_TOLERANCE:
                intersections.append(first_output + parameter * (second_output - first_output))
        if not intersections:
            return None
        source_value: float = start[0] if orientation == "x" else start[1]
        if direction == "negative":
            candidates: list[float] = [
                value
                for value in intersections
                if value <= source_value + cls.DIMENSION_TOLERANCE
            ]
            output: float | None = max(candidates) if candidates else None
        else:
            candidates = [
                value
                for value in intersections
                if value >= source_value - cls.DIMENSION_TOLERANCE
            ]
            output = min(candidates) if candidates else None
        if output is None:
            return None
        return (output, fixed) if orientation == "x" else (fixed, output)

    @classmethod
    def _merge_levels(
        cls, values: list[tuple[float, str]]
    ) -> list[tuple[float, tuple[str, ...]]]:
        """Merge nearly equal coordinate levels and retain their sources."""
        sorted_values: list[tuple[float, str]] = sorted(values, key=lambda value: (value[0], value[1]))
        groups: list[list[tuple[float, str]]] = []
        for value in sorted_values:
            if not groups or abs(value[0] - groups[-1][0][0]) > cls.DIMENSION_TOLERANCE:
                groups.append([value])
            else:
                groups[-1].append(value)
        return [
            (
                float(np.mean([value for value, _ in group])),
                tuple(sorted(source for _, source in group)),
            )
            for group in groups
        ]

    @classmethod
    def _unique_carbon_projections(
        cls, carbon_points: NDArray[np.float64]
    ) -> tuple[tuple[float, float, int], ...]:
        """Collapse coincident carbon projections while retaining multiplicity."""
        projections: list[list[float | int]] = []
        for point in np.asarray(carbon_points, dtype=np.float64):
            match_index: int | None = next(
                (
                    index
                    for index, existing in enumerate(projections)
                    if np.hypot(float(existing[0]) - point[0], float(existing[1]) - point[1])
                    <= cls.DIMENSION_TOLERANCE
                ),
                None,
            )
            if match_index is None:
                projections.append([float(point[0]), float(point[1]), 1])
            else:
                projections[match_index][2] = int(projections[match_index][2]) + 1
        projections.sort(key=lambda point: (float(point[0]), float(point[1])))
        return tuple(
            (float(point[0]), float(point[1]), int(point[2])) for point in projections
        )

    @staticmethod
    def _point_in_polygon(point: Coordinate2D, polygon: tuple[Coordinate2D, ...]) -> bool:
        """Return whether a point lies inside a polygon using deterministic ray casting."""
        x_coord, y_coord = point
        inside: bool = False
        previous: Coordinate2D = polygon[-1]
        for current in polygon:
            if (current[1] > y_coord) != (previous[1] > y_coord):
                intersection_x: float = (
                    (previous[0] - current[0])
                    * (y_coord - current[1])
                    / (previous[1] - current[1])
                    + current[0]
                )
                if x_coord < intersection_x:
                    inside = not inside
            previous = current
        return inside

    @staticmethod
    def _point_to_segment_distance(
        point: Coordinate2D, start: Coordinate2D, end: Coordinate2D
    ) -> float:
        """Calculate the 2D distance from a point to a finite segment."""
        point_array: NDArray[np.float64] = np.asarray(point, dtype=np.float64)
        start_array: NDArray[np.float64] = np.asarray(start, dtype=np.float64)
        vector: NDArray[np.float64] = np.asarray(end, dtype=np.float64) - start_array
        squared_length: float = float(np.dot(vector, vector))
        if squared_length <= 1e-20:
            return float(np.linalg.norm(point_array - start_array))
        parameter: float = float(np.dot(point_array - start_array, vector) / squared_length)
        parameter = min(1.0, max(0.0, parameter))
        projection: NDArray[np.float64] = start_array + parameter * vector
        return float(np.linalg.norm(point_array - projection))

    @staticmethod
    def _polygon_area(polygon: tuple[Coordinate2D, ...]) -> float:
        """Calculate signed polygon area."""
        return 0.5 * sum(
            polygon[index][0] * polygon[(index + 1) % len(polygon)][1]
            - polygon[(index + 1) % len(polygon)][0] * polygon[index][1]
            for index in range(len(polygon))
        )

    @staticmethod
    def _coordinate3d(point: NDArray[np.float64]) -> Coordinate3D:
        """Convert a NumPy point to an immutable typed coordinate."""
        return float(point[0]), float(point[1]), float(point[2])

    @staticmethod
    def _template_label(template_index: int) -> str:
        """Return an A-D label or a deterministic fallback layer label."""
        return chr(ord("A") + template_index) if template_index < 26 else f"L{template_index}"
