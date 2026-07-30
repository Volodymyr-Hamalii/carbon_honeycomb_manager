"""MCP server exposing the carbon honeycomb / intercalation domain layer as tools."""

from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
import pandas as pd
from mcp.server.mcpserver import MCPServer

from src.interfaces import (
    ICarbonHoneycombChannel,
    ICarbonHoneycombPlane,
    IPoints,
    PMvpParams,
)
from src.services import ATOM_PARAMS_MAP, Constants, FileReader, PathBuilder
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller
from src.projects.intercalation_and_sorption import (
    InterAtomsEditor,
    InterAtomsFileManager,
    IntercalationAndSorption,
    StructureValidator,
)

from .channel_provider import ChannelProvider
from .mvp_params_adapter import MvpParamsAdapter
from .serializers import df_to_records, list_to_points, name_value_df_to_dict, points_to_list
from .validation_targets_builder import ValidationTargetsBuilder


SERVER_INSTRUCTIONS: str = """
Tools for building and validating intercalated carbon honeycomb structures.

The server is deliberately rule-agnostic: it measures, reports and edits, but it never decides
whether a structure is good. Targets and tolerances are arguments of `validate_structure`, so the
rules a structure has to follow belong to the calling skill, not to this server.

It is also element-agnostic: `element` is a required argument of every structure tool and all
physical constants are resolved from it, so the same tools work for ar, xe, kr and al.

Coordinates are always lists of `[x, y, z]` triples in angstroms. Atom indexes refer to the position
in the coordinate list that a tool returned; every edit tool re-sorts its result by z, y, x (the
order used in the xlsx files), so re-read the returned list before the next edit.
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
            Constants.path.PROJECTS_DATA_PATH / project_dir
        ),
        "supported_elements": sorted(ATOM_PARAMS_MAP),
    }


@server.tool()
def list_structures(
        element: str,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> list[str]:
    """List the carbon structures available in the init data of the element (subdirectories only)."""
    path_to_dir: Path = (
        Constants.path.PROJECTS_DATA_PATH / project_dir / element / Constants.file_names.INIT_DATA_DIR
    )
    return FileReader.read_list_of_dirs(path_to_dir)


@server.tool()
def list_result_files(
        element: str,
        structure: str,
        file_format: str = "xlsx",
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
    """Read intercalated atom coordinates from a result data file (`.xlsx` or `.dat`)."""
    inter_atoms: IPoints = InterAtomsFileManager.read_inter_atoms(
        project_dir, element, structure, file_name
    )
    return {
        "file_name": file_name,
        "num_of_atoms": len(inter_atoms.points),
        "coordinates": points_to_list(inter_atoms),
    }


@server.tool()
def write_inter_atoms(
        element: str,
        structure: str,
        file_name: str,
        atoms: list[list[float]],
        sheet_name: str = InterAtomsFileManager.DEFAULT_SHEET_NAME,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Write intercalated atom coordinates to a result data file with the `i, x/y/z_inter` columns."""
    path_to_file: Path = InterAtomsFileManager.write_inter_atoms(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        file_name=file_name,
        inter_atoms=list_to_points(atoms),
        sheet_name=sheet_name,
    )
    return {"path": str(path_to_file), "num_of_atoms": len(atoms)}


@server.tool()
def write_final_structure(
        element: str,
        structure: str,
        atoms: list[list[float]],
        version: int | None = None,
        stacking: str | None = None,
        author: str = "Claude",
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Write a final one-channel structure following the `final_one_ch-v{i}[-{stacking}]-{author}.xlsx`
    naming convention.

    `version` defaults to the next free number for the structure. Pass `stacking` only when it is
    determined from the built structure (`AA`, `ABAB`, `ABC`, `ABCD`).
    """
    if version is None:
        version = InterAtomsFileManager.get_next_final_version(project_dir, element, structure)

    file_name: str = InterAtomsFileManager.build_final_file_name(
        version=version,
        stacking=stacking,
        author=author,
        num_of_channels="one",
    )

    path_to_file: Path = InterAtomsFileManager.write_inter_atoms(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        file_name=file_name,
        inter_atoms=list_to_points(atoms),
        sheet_name=InterAtomsFileManager.DEFAULT_SHEET_NAME,
    )

    return {
        "path": str(path_to_file),
        "file_name": file_name,
        "version": version,
        "num_of_atoms": len(atoms),
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

    Places atoms opposite the wall polygons and edge holes at the average intercalated-carbon
    distance. Writes `sorbed-plane-coordinates.xlsx` and returns the coordinates.
    """
    params: PMvpParams = MvpParamsAdapter.build(
        number_of_planes=number_of_planes,
        to_replace_nearby_atoms=to_replace_nearby_atoms,
        to_remove_too_close_atoms=to_remove_too_close_atoms,
    )
    path_to_file: Path = IntercalationAndSorption.generate_inter_plane_coordinates_file(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )
    return _read_generated_file(project_dir, element, structure, path_to_file)


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
    `place_opposite_centers` constant. Writes `sorbed-opposite-centers-coordinates.xlsx`.
    """
    params: PMvpParams = MvpParamsAdapter.build(number_of_planes=number_of_planes)
    path_to_file: Path = IntercalationAndSorption.generate_opposite_centers_coordinates_file(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )
    return _read_generated_file(project_dir, element, structure, path_to_file)


@server.tool()
def generate_atoms_opposite_faces(
        element: str,
        structure: str,
        number_of_planes: int = 6,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    The GUI `Generate opposite faces` command.

    Places atoms opposite the wall polygon vertices and edge midpoints, offset along the wall normal
    by the element's `place_opposite_faces` constant. Writes
    `sorbed-opposite-faces-coordinates.xlsx`.
    """
    params: PMvpParams = MvpParamsAdapter.build(number_of_planes=number_of_planes)
    path_to_file: Path = IntercalationAndSorption.generate_opposite_faces_coordinates_file(
        project_dir=project_dir,
        subproject_dir=element,
        structure_dir=structure,
        params=params,
    )
    return _read_generated_file(project_dir, element, structure, path_to_file)


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
        atoms: list[list[float]] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Add atoms at explicit coordinates to a set (given inline via `atoms` or read from `file_name`)."""
    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)
    result: IPoints = InterAtomsEditor.add_atoms(
        inter_atoms, np.array(new_atoms, dtype=np.float64)
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def delete_atoms(
        element: str,
        structure: str,
        indexes: list[int],
        atoms: list[list[float]] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Delete the atoms with the given indexes from a set."""
    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)
    result: IPoints = InterAtomsEditor.delete_atoms(inter_atoms, indexes)
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def move_atoms_on_vector(
        element: str,
        structure: str,
        indexes: list[int],
        vector: list[float],
        atoms: list[list[float]] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Move the atoms with the given indexes on the given `[dx, dy, dz]` vector."""
    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)
    result: IPoints = InterAtomsEditor.move_atoms_on_vector(
        inter_atoms, indexes, np.array(vector, dtype=np.float64)
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def move_atoms_to_channel_center(
        element: str,
        structure: str,
        indexes: list[int],
        distance: float,
        atoms: list[list[float]] | None = None,
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
    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)
    result: IPoints = InterAtomsEditor.move_atoms_to_channel_center(
        inter_atoms, indexes, carbon_channel.channel_center, distance
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def move_atoms_along_plane_normal(
        element: str,
        structure: str,
        indexes: list[int],
        plane_index: int,
        distance: float,
        atoms: list[list[float]] | None = None,
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
    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)
    result: IPoints = InterAtomsEditor.move_atoms_along_plane_normal(
        inter_atoms, indexes, plane, carbon_channel.channel_center, distance
    )
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def shift_atoms_along_z(
        element: str,
        structure: str,
        shift: float,
        atoms: list[list[float]] | None = None,
        file_name: str | None = None,
        output_file_name: str | None = None,
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """Shift the whole set of atoms along the Oz axis by `shift`."""
    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)
    result: IPoints = InterAtomsEditor.shift_along_z(inter_atoms, shift)
    return _edit_result(project_dir, element, structure, result, output_file_name)


@server.tool()
def translate_atoms_along_z(
        element: str,
        structure: str,
        num_of_periods: int,
        z_period: float | None = None,
        atoms: list[list[float]] | None = None,
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

    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)
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
        project_dir: str = ChannelProvider.DEFAULT_PROJECT_DIR,
) -> dict[str, Any]:
    """
    Numeric validation report for a set of intercalated atoms inside the channel.

    Reports, per atom and aggregated: min distance to carbon and its deviation from
    `target_dist_to_carbon`; min distance to the nearest intercalated atom and its deviation from
    `target_dist_between_inter_atoms`; min distance to a wall plane; which wall feature (hexagon /
    pentagon center or edge hole) the atom sits opposite to and at what normal distance; whether any
    pair breaks `hard_min_dist_between_inter_atoms`; and the smallest number of carbon z periods
    after which the structure maps onto itself.

    Every target is optional and defaults to the value from `get_intercalation_constants` for this
    element + structure, so the caller can validate the same structure against a different set of
    rules by passing its own numbers. The report flags violations but does not judge the structure.
    """
    carbon_channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        project_dir, element, structure
    )
    inter_atoms: IPoints = _resolve_atoms(project_dir, element, structure, atoms, file_name)

    targets = ValidationTargetsBuilder.build(
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
    )

    report: dict[str, Any] = StructureValidator.build_report(
        carbon_channel=carbon_channel,
        inter_atoms=inter_atoms,
        targets=targets,
    )

    return {"element": element, "structure": structure, "source_file_name": file_name, **report}


### HELPERS ###


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
) -> IPoints:
    """Take the atoms from the inline `atoms` argument or read them from `file_name`."""
    if atoms is not None and file_name is not None:
        raise ValueError("Provide either `atoms` or `file_name`, not both.")

    if atoms is not None:
        return list_to_points(atoms)

    if file_name is not None:
        return InterAtomsFileManager.read_inter_atoms(project_dir, element, structure, file_name)

    raise ValueError("Provide either `atoms` (inline coordinates) or `file_name`.")


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
    }

    if output_file_name is not None:
        path_to_file: Path = InterAtomsFileManager.write_inter_atoms(
            project_dir=project_dir,
            subproject_dir=element,
            structure_dir=structure,
            file_name=output_file_name,
            inter_atoms=result,
            sheet_name=InterAtomsFileManager.DEFAULT_SHEET_NAME,
        )
        payload["path"] = str(path_to_file)

    return payload


def _read_generated_file(
        project_dir: str,
        element: str,
        structure: str,
        path_to_file: Path,
) -> dict[str, Any]:
    """Read back a file a generator has just written and return its coordinates."""
    inter_atoms: IPoints = InterAtomsFileManager.read_inter_atoms(
        project_dir, element, structure, path_to_file.name
    )
    return {
        "path": str(path_to_file),
        "file_name": path_to_file.name,
        "num_of_atoms": len(inter_atoms.points),
        "coordinates": points_to_list(inter_atoms),
    }
