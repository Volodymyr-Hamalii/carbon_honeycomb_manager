"""MCP server exposing the carbon honeycomb / intercalation domain layer as tools."""

from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
import pandas as pd
from mcp.server.mcpserver import MCPServer

from src.interfaces import (
    ICarbonHoneycombChannel,
    ICarbonHoneycombPlane,
    IPoints,
    PMvpParams,
    PValidationTargets,
)
from src.entities import PolygonSiteMeasurementReport, PolygonSiteType
from src.services import ATOM_PARAMS_MAP, Constants, FileReader, PathBuilder
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller
from src.projects.intercalation_and_sorption import (
    CandidateComparator,
    InterAtomsEditor,
    InterAtomsFileManager,
    IntercalationAndSorption,
    StructureValidator,
    PolygonReferenceAnalyzer,
)

from .channel_provider import ChannelProvider
from .mvp_params_adapter import MvpParamsAdapter
from .run_checkpoint_store import RunCheckpointStore
from .serializers import (
    df_to_records,
    list_to_points,
    name_value_df_to_dict,
    points_to_atom_records,
    points_to_list,
)
from .validation_targets_builder import ValidationTargetsBuilder


SERVER_INSTRUCTIONS: str = """
Tools for building and validating intercalated carbon honeycomb structures.

The server is deliberately rule-agnostic: it measures, reports and edits, but it never decides
whether a structure is good. Targets and tolerances are arguments of `validate_structure`, so the
rules a structure has to follow belong to the calling skill, not to this server.

It is also element-agnostic: `element` is a required argument of every structure tool and all
physical constants are resolved from it, so the same tools work for ar, xe, kr and al.

Coordinates are lists of `[x, y, z]` triples in angstroms. Every result also returns stable
`atom_id` values; prefer `selected_atom_ids` over indexes when editing. New coordinate files are CSV
with `atom_id,x_inter,y_inter,z_inter` columns. Legacy XLSX and DAT files remain readable.
""".strip()


server: MCPServer = MCPServer(
    name="carbon-honeycomb-manager",
    version="0.1.0",
    instructions=SERVER_INSTRUCTIONS,
)


### DISCOVERY ###


@server.tool()
def list_projects() -> list[str]:
    """List the available project directories under `data/projects`."""
    return FileReader.read_list_of_dirs(Constants.path.PROJECTS_DATA_PATH)


@server.tool()
def list_elements(project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR) -> dict[str, Any]:
    """List the intercalated elements that have data in the project, and the supported ones."""
    return {
        "elements_with_data": FileReader.read_list_of_dirs(
            PathBuilder.build_path_to_project_dir(project_dir)
        ),
        "supported_elements": sorted(ATOM_PARAMS_MAP),
    }


@server.tool()
def list_structures(
        element: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> list[str]:
    """List the carbon structures available in the init data of the element (subdirectories only)."""
    path_to_dir: Path = PathBuilder.build_path_to_init_data_dir(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=".",
    )
    return FileReader.read_list_of_dirs(path_to_dir)


@server.tool()
def list_result_files(
        element: str,
        structure: str,
        file_format: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """List the result data files of the structure and the next free `final_one_ch-v{i}` version."""
    return {
        "files": InterAtomsFileManager.list_result_files(
            project_dir, element, structure, file_format=file_format
        ),
        "next_final_version": InterAtomsFileManager.get_next_final_version(
            project_dir, element, structure
        ),
        "result_data_dir": str(
            PathBuilder.build_path_to_result_data_dir(project_dir, element, structure)
        ),
    }


### METADATA ###


@server.tool()
def get_intercalation_constants(
        element: str,
        structure: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Physical constants for the element + structure pair (the GUI `Get intercalation constants`).

    `Average {element}-C distance` depends on the structure as well as on the element, because it is
    averaged with the real C-C distances of that structure - do not cache it per element.
    """
    constants_df: pd.DataFrame = IntercalationAndSorption.get_inter_chc_constants(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
    )
    return name_value_df_to_dict(constants_df)


@server.tool()
def get_channel_params(
        element: str,
        structure: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Geometry of the carbon channel: center, z limits, z self-repeat period and per-plane polygons.

    `polygons_per_plane` can legitimately be 0: the walls of the armchair-oriented C-family
    structures (e.g. `C0-7_h3`) have all their hexagons straddling the channel edges, so no polygon
    fits entirely into a single plane. Use `edge_holes_per_plane` as the wall features there.
    """
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    params: PMvpParams = MvpParamsAdapter.build(file_name=Constants.file_names.INIT_DAT_FILE)

    channel_params_df: pd.DataFrame = CarbonHoneycombModeller.get_channel_params(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )

    points: NDArray[np.float64] = carbon_channel.points
    ave_hexagon_centers_dist: float = float(carbon_channel.ave_dist_between_closest_hexagon_centers)

    return {
        "element": element,
        "structure": structure,
        "num_of_carbon_atoms": len(points),
        "num_of_planes": len(carbon_channel.planes),
        "channel_center": [round(float(value), 3) for value in carbon_channel.channel_center],
        "coordinate_limits": {
            "x_min": round(float(points[:, 0].min()), 3),
            "x_max": round(float(points[:, 0].max()), 3),
            "y_min": round(float(points[:, 1].min()), 3),
            "y_max": round(float(points[:, 1].max()), 3),
            "z_min": round(float(points[:, 2].min()), 3),
            "z_max": round(float(points[:, 2].max()), 3),
        },
        "ave_dist_between_closest_atoms": round(
            float(carbon_channel.ave_dist_between_closest_atoms), 4
        ),
        "ave_dist_between_closest_hexagon_centers": (
            None if np.isnan(ave_hexagon_centers_dist) else round(ave_hexagon_centers_dist, 4)
        ),
        "carbon_z_period": round(ValidationTargetsBuilder.get_carbon_z_period(carbon_channel), 3),
        "hexagons_per_plane": [len(plane.hexagons) for plane in carbon_channel.planes],
        "pentagons_per_plane": [len(plane.pentagons) for plane in carbon_channel.planes],
        "edge_holes_per_plane": [len(plane.edge_holes) for plane in carbon_channel.planes],
        **name_value_df_to_dict(channel_params_df),
    }


@server.tool()
def get_plane_geometry(
        element: str,
        structure: str,
        plane_index: int,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Geometry of one channel wall plane: plane equation, polygon centers and edge holes.

    The polygon centers and edge holes are the positions rule 3 refers to (intercalated atoms tend to
    sit opposite them, on the normal to the wall).
    """
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    plane: ICarbonHoneycombPlane = _get_plane(carbon_channel, plane_index)

    return {
        "plane_index": plane_index,
        "num_of_planes": len(carbon_channel.planes),
        "plane_params": [round(float(value), 6) for value in plane.plane_params],
        "plane_center": [round(float(value), 3) for value in plane.center],
        "faces_the_channel_center": plane.get_direction_to_center(carbon_channel.channel_center),
        "num_of_carbon_atoms": len(plane.points),
        "hexagon_centers": points_to_list(np.array([h.center for h in plane.hexagons]))
        if plane.hexagons else [],
        "pentagon_centers": points_to_list(np.array([p.center for p in plane.pentagons]))
        if plane.pentagons else [],
        "edge_holes": points_to_list(plane.edge_holes),
    }


@server.tool()
def get_carbon_coordinates(
        element: str,
        structure: str,
        plane_index: int | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Carbon coordinates of the channel, or of a single wall plane when `plane_index` is given."""
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )

    if plane_index is None:
        coordinates: NDArray[np.float64] = carbon_channel.points
    else:
        coordinates = _get_plane(carbon_channel, plane_index).points

    return {
        "num_of_atoms": len(coordinates),
        "coordinates": points_to_list(coordinates),
    }


### INTERCALATED ATOMS: READ / WRITE ###


@server.tool()
def read_inter_atoms(
        element: str,
        structure: str,
        file_name: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Read coordinates from CSV or a legacy XLSX/DAT file, preserving stable atom IDs."""
    inter_atoms: IPoints = InterAtomsFileManager.read_inter_atoms(
        project_dir, element, structure, file_name
    )
    return {
        "file_name": file_name,
        "num_of_atoms": len(inter_atoms.points),
        "coordinates": points_to_list(inter_atoms),
        "atom_ids": list(inter_atoms.atom_ids or ()),
        "atoms": points_to_atom_records(inter_atoms),
    }


@server.tool()
def write_inter_atoms(
        element: str,
        structure: str,
        file_name: str,
        atoms: list[list[float]],
        atom_ids: list[str] | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Write coordinates; use a `.csv` name for the CSV-first format."""
    inter_atoms: IPoints = list_to_points(atoms, atom_ids)
    path_to_file: Path = InterAtomsFileManager.write_inter_atoms(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        file_name=file_name,
        inter_atoms=inter_atoms,
    )
    return {
        "path": str(path_to_file),
        "num_of_atoms": len(atoms),
        "atom_ids": list(inter_atoms.atom_ids or ()),
    }


@server.tool()
def write_final_structure(
        element: str,
        structure: str,
        atoms: list[list[float]],
        atom_ids: list[str] | None = None,
        version: int | None = None,
        stacking: str | None = None,
        author: str = "Agent",
        required_checks: list[str] | None = None,
        target_dist_to_carbon: float | None = None,
        target_dist_between_inter_atoms: float | None = None,
        hard_min_dist_between_inter_atoms: float | None = None,
        max_compression_percent: float = 8.0,
        max_expansion_percent: float = 10.0,
        carbon_z_period: float | None = None,
        z_period_tolerance: float = 0.1,
        max_z_period_multiplier: int = 10,
        opposite_position_tolerance: float | None = None,
        near_wall_max_dist_to_plane: float | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Validate and write `final_one_ch-v{i}[-{stacking}]-{author}.csv`.

    Validation is recomputed immediately before writing. `required_checks` defaults to
    `["hard_floor_check"]`; every named report check must contain `passed: true`. All targets are
    explicit arguments or resolve through the same element/structure constants as
    `validate_structure`. The hard-floor check includes the inferred periodic seam as well as
    explicit atom pairs. Existing files are never overwritten.
    """
    inter_atoms: IPoints = list_to_points(atoms, atom_ids)
    report: dict[str, Any] = _build_validation_report(
        project_dir=project_dir,
        element=element,
        structure=structure,
        inter_atoms=inter_atoms,
        target_dist_to_carbon=target_dist_to_carbon,
        target_dist_between_inter_atoms=target_dist_between_inter_atoms,
        hard_min_dist_between_inter_atoms=hard_min_dist_between_inter_atoms,
        max_compression_percent=max_compression_percent,
        max_expansion_percent=max_expansion_percent,
        carbon_z_period=carbon_z_period,
        z_period_tolerance=z_period_tolerance,
        max_z_period_multiplier=max_z_period_multiplier,
        opposite_position_tolerance=opposite_position_tolerance,
        near_wall_max_dist_to_plane=near_wall_max_dist_to_plane,
    )
    checks_to_require: list[str] = required_checks or ["hard_floor_check"]
    unsupported_checks: list[str] = [name for name in checks_to_require if name not in report]
    if unsupported_checks:
        raise ValueError(f"Unknown required checks: {unsupported_checks}.")
    failed_checks: list[str] = [
        name
        for name in checks_to_require
        if not isinstance(report[name], dict) or report[name].get("passed") is not True
    ]
    if failed_checks:
        raise ValueError(f"Refusing to write: required validation checks failed: {failed_checks}.")

    if version is None:
        version = InterAtomsFileManager.get_next_final_version(project_dir, element, structure)

    file_name: str = InterAtomsFileManager.build_final_file_name(
        version=version,
        stacking=stacking,
        author=author,
        num_of_channels="one",
        file_format="csv",
    )

    destination: Path = PathBuilder.build_path_to_result_data_file(
        project_dir, element, structure, file_name
    )
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing final structure: {destination}")

    path_to_file: Path = InterAtomsFileManager.write_inter_atoms(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        file_name=file_name,
        inter_atoms=inter_atoms,
    )

    return {
        "path": str(path_to_file),
        "file_name": file_name,
        "version": version,
        "num_of_atoms": len(atoms),
        "atom_ids": list(inter_atoms.atom_ids or ()),
        "required_checks": checks_to_require,
        "validation": {
            "summary": report["summary"],
            "hard_floor_check": report["hard_floor_check"],
            "dist_to_carbon_corridor_check": report["dist_to_carbon_corridor_check"],
            "dist_between_inter_atoms_corridor_check": report[
                "dist_between_inter_atoms_corridor_check"
            ],
            "z_periodicity_check": report["z_periodicity_check"],
            "violations": report["violations"],
            "compromise": report["compromise"],
        },
    }


### GENERATORS ###


@server.tool()
def generate_atoms_near_planes(
        element: str,
        structure: str,
        number_of_planes: int = 6,
        to_replace_nearby_atoms: bool = True,
        to_remove_too_close_atoms: bool = False,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    The GUI `Generate near planes` command: candidate positions near the channel walls.

    Places atoms opposite wall polygons and edge holes at the average intercalated-carbon distance.
    This tool is pure: it returns coordinates and writes no intermediate file.
    """
    params: PMvpParams = MvpParamsAdapter.build(
        number_of_planes=number_of_planes,
        to_replace_nearby_atoms=to_replace_nearby_atoms,
        to_remove_too_close_atoms=to_remove_too_close_atoms,
    )
    inter_atoms: IPoints = IntercalationAndSorption.generate_inter_plane_coordinates(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )
    return _edit_result(project_dir, element, structure, inter_atoms, output_file_name=None)


@server.tool()
def generate_atoms_opposite_centers(
        element: str,
        structure: str,
        number_of_planes: int = 6,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    The GUI `Generate opposite centers` command.

    Places one atom opposite each wall polygon center, offset along the wall normal by the element's
    `place_opposite_centers` constant. This tool writes no intermediate file.
    """
    params: PMvpParams = MvpParamsAdapter.build(number_of_planes=number_of_planes)
    inter_atoms: IPoints = IntercalationAndSorption.generate_opposite_centers_coordinates(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )
    return _edit_result(project_dir, element, structure, inter_atoms, output_file_name=None)


@server.tool()
def generate_atoms_opposite_faces(
        element: str,
        structure: str,
        number_of_planes: int = 6,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    The GUI `Generate opposite faces` command.

    Places atoms opposite wall polygon vertices and edge midpoints. This tool writes no intermediate
    file.
    """
    params: PMvpParams = MvpParamsAdapter.build(number_of_planes=number_of_planes)
    inter_atoms: IPoints = IntercalationAndSorption.generate_opposite_faces_coordinates(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )
    return _edit_result(project_dir, element, structure, inter_atoms, output_file_name=None)


@server.tool()
def get_polygon_reference_sites(
        element: str,
        structure: str,
        site_types: list[str] | None = None,
        wall_indexes: list[int] | None = None,
        include_details: bool = True,
        limit: int = 500,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Return stable center, carbon-vertex and C-C edge-midpoint reference sites.

    Carbon pairs at a strict 3D distance below 1.65 Å form edges. Centers come from chordless
    five- and six-member rings across the whole channel, including cross-wall rings. Use
    `site_types`, `wall_indexes`, `include_details=False`, or `limit` to keep payloads compact.
    Coordinates are in Å and inward normals are unit vectors. This tool writes no file.
    """
    resolved_types: tuple[PolygonSiteType, ...] | None = _polygon_site_types(site_types)
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    sites = PolygonReferenceAnalyzer.get_reference_sites(
        carbon_channel,
        site_types=resolved_types,
        wall_indexes=None if wall_indexes is None else tuple(wall_indexes),
    )
    counts: dict[str, int] = {
        site_type: sum(site.site_type == site_type for site in sites)
        for site_type in ("center", "vertex", "edge_midpoint")
    }
    safe_limit: int = max(0, limit)
    payload: dict[str, Any] = {
        "counts": counts,
        "total": len(sites),
        "returned": min(len(sites), safe_limit),
    }
    if include_details:
        payload["sites"] = [site.to_dict() for site in sites[:safe_limit]]
    return payload


@server.tool()
def generate_atoms_at_polygon_sites(
        element: str,
        structure: str,
        site_types: list[str] | None = None,
        wall_indexes: list[int] | None = None,
        center_target: float | None = None,
        face_target: float | None = None,
        limit: int = 1000,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Purely generate candidates along each polygon site's inward wall normal.

    Center and face targets are distances in Å. Unset targets resolve through `ATOM_PARAMS_MAP`
    for `element`. A multi-wall source site yields one stable candidate per association. Candidates
    are deliberately not merged or packing-filtered, and no intermediate file is written.
    """
    atom_params = ChannelProvider.get_atom_params(element)
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    candidates = PolygonReferenceAnalyzer.generate_candidates(
        carbon_channel,
        center_target=(
            atom_params.PLACE_OPPOSITE_CENTERS_DIST if center_target is None else center_target
        ),
        face_target=atom_params.PLACE_OPPOSITE_FACES_DIST if face_target is None else face_target,
        site_types=_polygon_site_types(site_types),
        wall_indexes=None if wall_indexes is None else tuple(wall_indexes),
    )
    return {
        "total": len(candidates),
        "returned": min(len(candidates), max(0, limit)),
        "candidates": [candidate.to_dict() for candidate in candidates[:max(0, limit)]],
    }


@server.tool()
def measure_polygon_site_distances(
        element: str,
        structure: str,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        center_target: float | None = None,
        face_target: float | None = None,
        near_wall_max_dist_to_plane: float | None = None,
        alignment_tolerance: float | None = None,
        corridor_lower_percent: float = -8.0,
        corridor_upper_percent: float = 10.0,
        reference_wall_index: int | None = None,
        reference_wall_indexes: list[int] | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Measure polygon-site alignment and normal-distance deviations per atom.

    Supply exactly one of inline `atoms` (with optional aligned `atom_ids`) or `file_name`. Distances
    are in Å. Targets default to the element constants; near-wall classification and alignment
    tolerance use the same project defaults as `validate_structure`. By default each atom is
    measured against its nearest wall. Use `reference_wall_index` for one wall shared by all atoms,
    or aligned `reference_wall_indexes` for a mixed-wall model; these options are mutually
    exclusive. Central atoms are explicitly exempt unless an explicit wall makes them fall within
    the supplied near-wall limit. The report measures and flags the -8%/+10% corridor by default
    but never accepts a model or writes a file.
    """
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    atom_params = ChannelProvider.get_atom_params(element)
    validation_targets = ValidationTargetsBuilder.build(
        project_dir,
        element,
        structure,
        carbon_channel,
        near_wall_max_dist_to_plane=near_wall_max_dist_to_plane,
        opposite_position_tolerance=alignment_tolerance,
    )
    if reference_wall_index is not None and reference_wall_indexes is not None:
        raise ValueError(
            "Use either reference_wall_index or reference_wall_indexes, not both."
        )
    resolved_reference_walls: tuple[int, ...] | None = None
    if reference_wall_index is not None:
        resolved_reference_walls = tuple(
            reference_wall_index for _ in inter_atoms.points
        )
    elif reference_wall_indexes is not None:
        resolved_reference_walls = tuple(reference_wall_indexes)
    report: PolygonSiteMeasurementReport = PolygonReferenceAnalyzer.measure(
        carbon_channel,
        inter_atoms,
        center_target=(
            atom_params.PLACE_OPPOSITE_CENTERS_DIST if center_target is None else center_target
        ),
        face_target=atom_params.PLACE_OPPOSITE_FACES_DIST if face_target is None else face_target,
        near_wall_max_dist_to_plane=validation_targets.near_wall_dist_to_plane_limit,
        alignment_tolerance=validation_targets.opposite_position_tolerance,
        corridor_lower_percent=corridor_lower_percent,
        corridor_upper_percent=corridor_upper_percent,
        reference_wall_indexes=resolved_reference_walls,
    )
    return report.to_dict()


### DISTANCES ###


@server.tool()
def get_distance_matrix(
        element: str,
        structure: str,
        file_name: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    The GUI `Get distance matrix` command for a saved intercalated atoms file.

    Per atom: coordinates, min distance to the wall plane / to carbon / to another intercalated
    atom, and the distances to every other intercalated atom.
    """
    params: PMvpParams = MvpParamsAdapter.build(file_name=file_name)
    matrix_df: pd.DataFrame = IntercalationAndSorption.get_distance_matrix(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )
    return {"file_name": file_name, "rows": df_to_records(matrix_df)}


### EDIT PRIMITIVES ###


@server.tool()
def add_atoms(
        element: str,
        structure: str,
        new_atoms: list[list[float]],
        new_atom_ids: list[str] | None = None,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Add atoms at explicit coordinates to a set (given inline via `atoms` or read from `file_name`)."""
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    result: IPoints = InterAtomsEditor.add_atoms(
        inter_atoms, np.array(new_atoms, dtype=np.float64), new_atom_ids
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def delete_atoms(
        element: str,
        structure: str,
        indexes: list[int] | None = None,
        selected_atom_ids: list[str] | None = None,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Delete atoms selected by stable IDs (preferred) or legacy indexes."""
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    resolved_indexes: list[int] = _resolve_selected_indexes(
        inter_atoms, indexes, selected_atom_ids
    )
    result: IPoints = InterAtomsEditor.delete_atoms(inter_atoms, resolved_indexes)
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def move_atoms_on_vector(
        element: str,
        structure: str,
        vector: list[float],
        indexes: list[int] | None = None,
        selected_atom_ids: list[str] | None = None,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Move atoms selected by stable IDs (preferred) or indexes on `[dx, dy, dz]`."""
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    resolved_indexes: list[int] = _resolve_selected_indexes(
        inter_atoms, indexes, selected_atom_ids
    )
    result: IPoints = InterAtomsEditor.move_atoms_on_vector(
        inter_atoms, resolved_indexes, np.array(vector, dtype=np.float64)
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def move_atoms_to_channel_center(
        element: str,
        structure: str,
        distance: float,
        indexes: list[int] | None = None,
        selected_atom_ids: list[str] | None = None,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Move the atoms with the given indexes towards the channel axis by `distance`.

    A negative `distance` moves them away from the axis. The z coordinate is preserved.
    """
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    resolved_indexes: list[int] = _resolve_selected_indexes(
        inter_atoms, indexes, selected_atom_ids
    )
    result: IPoints = InterAtomsEditor.move_atoms_to_channel_center(
        inter_atoms, resolved_indexes, carbon_channel.channel_center, distance
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def move_atoms_along_plane_normal(
        element: str,
        structure: str,
        plane_index: int,
        distance: float,
        indexes: list[int] | None = None,
        selected_atom_ids: list[str] | None = None,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Move the atoms with the given indexes along the normal of a channel wall plane.

    A positive `distance` moves them away from that wall (towards the channel center), a negative
    one moves them towards the wall.
    """
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    plane: ICarbonHoneycombPlane = _get_plane(carbon_channel, plane_index)
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    resolved_indexes: list[int] = _resolve_selected_indexes(
        inter_atoms, indexes, selected_atom_ids
    )
    result: IPoints = InterAtomsEditor.move_atoms_along_plane_normal(
        inter_atoms, resolved_indexes, plane, carbon_channel.channel_center, distance
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def shift_atoms_along_z(
        element: str,
        structure: str,
        shift: float,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Shift the whole set of atoms along the Oz axis by `shift`."""
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    result: IPoints = InterAtomsEditor.shift_along_z(inter_atoms, shift)
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def translate_atoms_along_z(
        element: str,
        structure: str,
        num_of_periods: int,
        z_period: float | None = None,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Replicate the set of atoms along Oz: the original plus `num_of_periods` shifted copies.

    `z_period` defaults to the z self-repeat period of the carbon channel.
    """
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )

    if z_period is None:
        z_period = ValidationTargetsBuilder.get_carbon_z_period(carbon_channel)

    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    result: IPoints = InterAtomsEditor.translate_along_z(inter_atoms, z_period, num_of_periods)

    payload: dict[str, Any] = _edit_result(
        project_dir, element, structure, result, output_file_name
    )
    payload["z_period"] = round(z_period, 3)
    return payload


### VALIDATION ###


@server.tool()
def validate_structure(
        element: str,
        structure: str,
        atoms: list[list[float]] | None = None,
        atom_ids: list[str] | None = None,
        file_name: str | None = None,
        target_dist_to_carbon: float | None = None,
        target_dist_between_inter_atoms: float | None = None,
        hard_min_dist_between_inter_atoms: float | None = None,
        max_compression_percent: float = 8.0,
        max_expansion_percent: float = 10.0,
        carbon_z_period: float | None = None,
        z_period_tolerance: float = 0.1,
        max_z_period_multiplier: int = 10,
        opposite_position_tolerance: float | None = None,
        near_wall_max_dist_to_plane: float | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Numeric validation report for a set of intercalated atoms inside the channel.

    Reports, per atom and aggregated: min distance to carbon and its deviation from
    `target_dist_to_carbon`; min distance to the nearest intercalated atom and its deviation from
    `target_dist_between_inter_atoms`; min distance to a wall plane; whether the atom sits near a
    wall; which wall feature (hexagon / pentagon center or edge hole) it sits opposite to and at what
    normal distance; whether any pair breaks `hard_min_dist_between_inter_atoms`; and the smallest
    number of carbon z periods after which the structure maps onto itself.

    The intercalated-carbon corridor is only applied to atoms that sit **near a wall**, i.e. whose
    distance to the nearest wall plane is at most `near_wall_max_dist_to_plane` (default: the upper
    edge of the carbon corridor). Atoms filling the middle of a wide channel are legitimately much
    further from carbon, are listed under `atom_indexes_exempt`, and never count as violations -
    their spacing is judged by `target_dist_between_inter_atoms` instead.

    Every target is optional and defaults to the value from `get_intercalation_constants` for this
    element + structure, so the caller can validate the same structure against a different set of
    rules by passing its own numbers. The report flags violations but does not judge the structure.
    """
    inter_atoms: IPoints = _resolve_atoms(
        project_dir, element, structure, atoms, file_name, atom_ids
    )
    report: dict[str, Any] = _build_validation_report(
        project_dir=project_dir,
        element=element,
        structure=structure,
        inter_atoms=inter_atoms,
        target_dist_to_carbon=target_dist_to_carbon,
        target_dist_between_inter_atoms=target_dist_between_inter_atoms,
        hard_min_dist_between_inter_atoms=hard_min_dist_between_inter_atoms,
        max_compression_percent=max_compression_percent,
        max_expansion_percent=max_expansion_percent,
        carbon_z_period=carbon_z_period,
        z_period_tolerance=z_period_tolerance,
        max_z_period_multiplier=max_z_period_multiplier,
        opposite_position_tolerance=opposite_position_tolerance,
        near_wall_max_dist_to_plane=near_wall_max_dist_to_plane,
    )
    return {"element": element, "structure": structure, "source_file_name": file_name, **report}


### CANDIDATE COMPARISON AND RUN CHECKPOINTS ###


@server.tool()
def compare_structures(
        atoms_a: list[list[float]],
        atoms_b: list[list[float]],
        distinct_rmsd_threshold: float = 0.4,
        z_period: float | None = None,
) -> dict[str, Any]:
    """Compare unordered candidates and classify diversity using a caller-supplied RMSD threshold."""
    return CandidateComparator.compare(
        candidate_a=list_to_points(atoms_a),
        candidate_b=list_to_points(atoms_b),
        distinct_rmsd_threshold=distinct_rmsd_threshold,
        z_period=z_period,
    )


@server.tool()
def save_run_checkpoint(
        element: str,
        structure: str,
        run_id: str,
        state: dict[str, Any],
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Save explicit JSON loop state so a Codex or Claude run can resume after interruption."""
    path: Path = RunCheckpointStore.save(project_dir, element, structure, run_id, state)
    return {"run_id": run_id, "path": str(path)}


@server.tool()
def load_run_checkpoint(
        element: str,
        structure: str,
        run_id: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Load an explicit JSON loop checkpoint."""
    return {
        "run_id": run_id,
        "state": RunCheckpointStore.load(project_dir, element, structure, run_id),
    }


@server.tool()
def list_run_checkpoints(
        element: str,
        structure: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> list[str]:
    """List resumable run checkpoint IDs for one element and structure."""
    return RunCheckpointStore.list_run_ids(project_dir, element, structure)


### HELPERS ###


def _polygon_site_types(site_types: list[str] | None) -> tuple[PolygonSiteType, ...] | None:
    """Validate and narrow public string values to supported polygon site types."""
    if site_types is None:
        return None
    allowed: frozenset[str] = frozenset({"center", "vertex", "edge_midpoint"})
    invalid: list[str] = sorted(set(site_types) - allowed)
    if invalid:
        raise ValueError(f"Unknown site_types {invalid}; expected values from {sorted(allowed)}.")
    return tuple(cast(PolygonSiteType, site_type) for site_type in site_types)


def _get_plane(carbon_channel: ICarbonHoneycombChannel, plane_index: int) -> ICarbonHoneycombPlane:
    """Return the wall plane by index, with a helpful error when it is out of range."""
    planes: list[ICarbonHoneycombPlane] = carbon_channel.planes

    if plane_index < 0 or plane_index >= len(planes):
        raise IndexError(
            f"plane_index {plane_index} is out of range: the channel has {len(planes)} planes."
        )

    return planes[plane_index]


def _resolve_atoms(
        project_dir: str,
        element: str,
        structure: str,
        atoms: list[list[float]] | None,
        file_name: str | None,
        atom_ids: list[str] | None = None,
) -> IPoints:
    """Take the atoms from the inline `atoms` argument or read them from `file_name`."""
    if atoms is not None and file_name is not None:
        raise ValueError("Provide either `atoms` or `file_name`, not both.")

    if atoms is not None:
        return list_to_points(atoms, atom_ids)

    if file_name is not None:
        return InterAtomsFileManager.read_inter_atoms(project_dir, element, structure, file_name)

    raise ValueError("Provide either `atoms` (inline coordinates) or `file_name`.")


def _resolve_selected_indexes(
        inter_atoms: IPoints,
        indexes: list[int] | None,
        selected_atom_ids: list[str] | None,
) -> list[int]:
    """Resolve one unambiguous atom selection, preferring stable IDs."""
    if indexes is not None and selected_atom_ids is not None:
        raise ValueError("Provide either indexes or selected_atom_ids, not both.")
    if selected_atom_ids is not None:
        if inter_atoms.atom_ids is None:
            raise ValueError("The atom set has no stable IDs.")
        id_to_index: dict[str, int] = {
            atom_id: index for index, atom_id in enumerate(inter_atoms.atom_ids)
        }
        missing_ids: list[str] = [
            atom_id for atom_id in selected_atom_ids if atom_id not in id_to_index
        ]
        if missing_ids:
            raise KeyError(f"Unknown atom IDs: {missing_ids}.")
        return [id_to_index[atom_id] for atom_id in selected_atom_ids]
    if indexes is not None:
        return indexes
    raise ValueError("Provide selected_atom_ids or indexes.")


def _edit_result(
        project_dir: str,
        element: str,
        structure: str,
        result: IPoints,
        output_file_name: str | None,
) -> dict[str, Any]:
    """Serialize the result of an edit operation, optionally writing it to a file."""
    payload: dict[str, Any] = {
        "num_of_atoms": len(result.points),
        "coordinates": points_to_list(result),
        "atom_ids": list(result.atom_ids or ()),
        "atoms": points_to_atom_records(result),
    }

    if output_file_name is not None:
        path_to_file: Path = InterAtomsFileManager.write_inter_atoms(
            project_dir=project_dir,
            subproject_dir=element,
            structure_dir=structure,
            file_name=output_file_name,
            inter_atoms=result,
        )
        payload["path"] = str(path_to_file)

    return payload


def _build_validation_report(
        project_dir: str,
        element: str,
        structure: str,
        inter_atoms: IPoints,
        target_dist_to_carbon: float | None,
        target_dist_between_inter_atoms: float | None,
        hard_min_dist_between_inter_atoms: float | None,
        max_compression_percent: float,
        max_expansion_percent: float,
        carbon_z_period: float | None,
        z_period_tolerance: float,
        max_z_period_multiplier: int,
        opposite_position_tolerance: float | None,
        near_wall_max_dist_to_plane: float | None,
) -> dict[str, Any]:
    """Build a validation report and attach stable IDs to all index-based findings."""
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    targets: PValidationTargets = ValidationTargetsBuilder.build(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        carbon_channel=carbon_channel,
        target_dist_to_carbon=target_dist_to_carbon,
        target_dist_between_inter_atoms=target_dist_between_inter_atoms,
        hard_min_dist_between_inter_atoms=hard_min_dist_between_inter_atoms,
        max_compression_percent=max_compression_percent,
        max_expansion_percent=max_expansion_percent,
        carbon_z_period=carbon_z_period,
        z_period_tolerance=z_period_tolerance,
        max_z_period_multiplier=max_z_period_multiplier,
        opposite_position_tolerance=opposite_position_tolerance,
        near_wall_max_dist_to_plane=near_wall_max_dist_to_plane,
    )
    report: dict[str, Any] = StructureValidator.build_report(
        carbon_channel=carbon_channel, inter_atoms=inter_atoms, targets=targets
    )
    _attach_atom_ids(report, inter_atoms)
    return report


def _attach_atom_ids(report: dict[str, Any], inter_atoms: IPoints) -> None:
    """Add stable atom IDs alongside validator indexes without removing legacy fields."""
    atom_ids: tuple[str, ...] = inter_atoms.atom_ids or tuple(
        f"atom-{index + 1:04d}" for index in range(len(inter_atoms.points))
    )
    for index, atom_report in enumerate(report.get("atoms", [])):
        atom_report["atom_id"] = atom_ids[index]

    hard_floor: dict[str, Any] = report.get("hard_floor_check", {})
    for violation in hard_floor.get("violations", []):
        violation["atom_ids"] = [atom_ids[index] for index in violation["atom_indexes"]]

    for check_name in (
        "dist_to_carbon_corridor_check",
        "dist_between_inter_atoms_corridor_check",
    ):
        check: dict[str, Any] = report.get(check_name, {})
        for key, value in list(check.items()):
            if key.startswith("atom_indexes_") and isinstance(value, list):
                check[key.replace("atom_indexes_", "atom_ids_")] = [
                    atom_ids[index] for index in value
                ]
