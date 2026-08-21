
"""Intercalation and sorption analysis functionality."""

from pathlib import Path
import re
import numpy as np
from numpy.typing import NDArray
import pandas as pd

from src.interfaces import (
    IPoints,
    ICarbonHoneycombChannel,
    PMvpParams,
)
from src.entities import (
    Points,
    PolygonReferenceSite,
    PolygonSiteMeasurementReport,
    PolygonSiteType,
)
from src.services import (
    Constants,
    ConstantsAtomParams,
    ATOM_PARAMS_MAP,
    Logger,
    FileReader,
    FileWriter,
    PathBuilder,
    DistanceMeasurer,
)
from src.services.coordinate_operations import PointsFilter
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller, CarbonHoneycombActions

from .build_intercalated_structure import (
    CoordinatesTableManager,
    InterAtomsParser,
    InterAtomsTranslator,
)
from .structure_operations import InterAtomsFileManager, PolygonReferenceAnalyzer


logger = Logger("IntercalationAndSorption")


class IntercalationAndSorption:
    """Intercalation and sorption analysis functionality."""

    POLYGON_CANDIDATE_WALL_PATTERN: re.Pattern[str] = re.compile(r"-w(\d+)$")
    POLYGON_SITE_UI_COLUMNS: tuple[str, ...] = (
        "coordinates",
        "is_near_wall",
        "Min distance to plane",
        "Min distance to C",
        "Min distance to inter",
        "actual_normal_distance",
        "projection_coordinates",
        "nearest_center_coordinates",
        "nearest_vertex_coordinates",
        "nearest_edge_midpoint_coordinates",
        "d_center",
        "d_vertex",
        "d_edge_midpoint",
        "exemption_reason",
    )
    POLYGON_SITE_UI_COORDINATE_COLUMNS: tuple[str, ...] = (
        "coordinates",
        "projection_coordinates",
        "nearest_center_coordinates",
        "nearest_vertex_coordinates",
        "nearest_edge_midpoint_coordinates",
    )
    POLYGON_SITE_UI_DISTANCE_COLUMNS: tuple[str, ...] = (
        "Min distance to plane",
        "Min distance to C",
        "Min distance to inter",
        "actual_normal_distance",
        "d_center",
        "d_vertex",
        "d_edge_midpoint",
    )

    @staticmethod
    def generate_inter_plane_coordinates(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> IPoints:
        """Generate intercalated plane coordinates without writing a file."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]
        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )
        inter_atoms: IPoints = InterAtomsParser.build_inter_atoms_plane_coordinates(
            carbon_channel,
            num_of_planes=params.number_of_planes,
            atom_params=atom_params,
            to_replace_nearby_atoms=params.to_replace_nearby_atoms,
            to_remove_too_close_atoms=params.to_remove_too_close_atoms,
        )
        return IntercalationAndSorption._filter_and_sort_coordinates(inter_atoms, params)

    @staticmethod
    def generate_inter_plane_coordinates_file(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Generate intercalated plane coordinates file."""
        inter_atoms_plane_coordinates: IPoints = (
            IntercalationAndSorption.generate_inter_plane_coordinates(
                project_dir, subproject_dir, structure_dir, params
            )
        )

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir,
            file_name=Constants.file_names.PLANE_COORDINATES_CSV_FILE,
        )

        path_to_file_result: Path = FileWriter.write_csv_file(
            df=IntercalationAndSorption._coordinates_df(inter_atoms_plane_coordinates),
            path_to_file=path_to_file,
        )

        return path_to_file_result

    @classmethod
    def generate_opposite_centers_coordinates(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> IPoints:
        """Generate atoms opposite polygon centers without writing a file."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]
        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )
        inter_atoms: IPoints = InterAtomsParser.build_inter_atoms_opposite_centers_coordinates(
            carbon_channel, num_of_planes=params.number_of_planes, atom_params=atom_params
        )
        return cls._filter_and_sort_coordinates(inter_atoms, params)

    @classmethod
    def generate_opposite_centers_coordinates_file(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Generate intercalated atoms placed opposite the polygon centers."""
        inter_atoms: IPoints = cls.generate_opposite_centers_coordinates(
            project_dir, subproject_dir, structure_dir, params
        )

        return cls._write_inter_plane_coordinates(
            inter_atoms=inter_atoms,
            params=params,
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=Constants.file_names.OPPOSITE_CENTERS_COORDINATES_CSV_FILE,
        )

    @classmethod
    def generate_opposite_faces_coordinates(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> IPoints:
        """Generate atoms opposite polygon faces without writing a file."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]
        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )
        inter_atoms: IPoints = InterAtomsParser.build_inter_atoms_opposite_faces_coordinates(
            carbon_channel, num_of_planes=params.number_of_planes, atom_params=atom_params
        )
        return cls._filter_and_sort_coordinates(inter_atoms, params)

    @classmethod
    def generate_opposite_faces_coordinates_file(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Generate intercalated atoms placed opposite the polygon vertices and edge midpoints."""
        inter_atoms: IPoints = cls.generate_opposite_faces_coordinates(
            project_dir, subproject_dir, structure_dir, params
        )

        return cls._write_inter_plane_coordinates(
            inter_atoms=inter_atoms,
            params=params,
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=Constants.file_names.OPPOSITE_FACES_COORDINATES_CSV_FILE,
        )

    @staticmethod
    def _write_inter_plane_coordinates(
        inter_atoms: IPoints,
        params: PMvpParams,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        file_name: str,
    ) -> Path:
        """Filter, sort and write intercalated coordinates to CSV."""
        inter_atoms = IntercalationAndSorption._filter_and_sort_coordinates(inter_atoms, params)

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir,
            file_name=file_name,
        )

        path_to_file_result: Path = FileWriter.write_csv_file(
            df=IntercalationAndSorption._coordinates_df(inter_atoms), path_to_file=path_to_file
        )

        return path_to_file_result

    @staticmethod
    def _filter_and_sort_coordinates(inter_atoms: IPoints, params: PMvpParams) -> IPoints:
        """Apply coordinate limits and return points sorted by z, y, x."""
        coordinates: NDArray[np.float64] = inter_atoms.points
        mask: NDArray[np.bool_] = (
            (coordinates[:, 0] >= params.x_min)
            & (coordinates[:, 0] <= params.x_max)
            & (coordinates[:, 1] >= params.y_min)
            & (coordinates[:, 1] <= params.y_max)
            & (coordinates[:, 2] >= params.z_min)
            & (coordinates[:, 2] <= params.z_max)
        )
        filtered: NDArray[np.float64] = coordinates[mask]
        sort_indexes: NDArray[np.intp] = np.lexsort(
            (filtered[:, 0], filtered[:, 1], filtered[:, 2])
        )
        sorted_coordinates: NDArray[np.float64] = filtered[sort_indexes]
        source_ids: tuple[str, ...] = inter_atoms.atom_ids or tuple(
            f"atom-{index + 1:04d}" for index in range(len(coordinates))
        )
        filtered_ids: tuple[str, ...] = tuple(
            atom_id for atom_id, keep in zip(source_ids, mask) if keep
        )
        atom_ids: tuple[str, ...] = tuple(filtered_ids[int(index)] for index in sort_indexes)
        return Points(points=sorted_coordinates, atom_ids=atom_ids)

    @staticmethod
    def _coordinates_df(inter_atoms: IPoints) -> pd.DataFrame:
        """Serialize intercalated coordinates with stable atom IDs."""
        atom_ids: tuple[str, ...] = inter_atoms.atom_ids or tuple(
            f"atom-{index + 1:04d}" for index in range(len(inter_atoms.points))
        )
        return pd.DataFrame({
            InterAtomsParser.ATOM_ID_COLUMN: atom_ids,
            InterAtomsParser.INTER_ATOMS_COORDINATES_COLUMNS[0]: inter_atoms.points[:, 0],
            InterAtomsParser.INTER_ATOMS_COORDINATES_COLUMNS[1]: inter_atoms.points[:, 1],
            InterAtomsParser.INTER_ATOMS_COORDINATES_COLUMNS[2]: inter_atoms.points[:, 2],
        })

    @staticmethod
    def update_inter_plane_coordinates_file(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Update intercalated plane coordinates file."""
        file_name: str | None = params.file_name
        if file_name is None:
            raise ValueError("File name is required")

        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )

        path_to_file: Path = CoordinatesTableManager.update_plane_tbl_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            carbon_channel=carbon_channel,
            number_of_planes=params.number_of_planes,
            atom_params=atom_params,
            file_name=file_name,
            to_replace_nearby_atoms=params.to_replace_nearby_atoms,
            to_remove_too_close_atoms=params.to_remove_too_close_atoms,
        )

        return path_to_file

    @staticmethod
    def translate_inter_atoms_to_other_planes(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> None:
        """Read intercalated coordinates and translate the structure to other planes."""
        file_name: str | None = params.file_name
        if file_name is None:
            raise ValueError("File name is required")

        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )

        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
            to_print_warning=False,
        )

        if inter_atoms_full_channel_coordinates_df is None:
            raise IOError(f"Failed to read {params.file_name} file")

        # inter_atoms_coordinates: IPoints = InterAtomsParser.parse_inter_atoms_coordinates_df(
        #     inter_atoms_full_channel_coordinates_df
        # )
        # inter_atoms_coordinates = InterAtomsTranslator.translate_for_all_planes(
        #     carbon_channel,
        #     inter_atoms_coordinates,
        #     params.number_of_planes,
        #     params.to_to_try_to_reflect_inter_atoms,
        #     atom_params,
        # )

        # if params.number_of_planes > 1:
        #     # Build only specified planes
        #     carbon_channel_points: NDArray[np.float64] = np.vstack(
        #         [carbon_channel.planes[i].points for i in range(params.number_of_planes)]
        #     )
        # else:
        #     # Build all planes
        #     carbon_channel_points: NDArray[np.float64] = carbon_channel.points

        raise NotImplementedError("Not implemented fully")

    @staticmethod
    def get_inter_chc_constants(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        # params: PMvpParams,
    ) -> pd.DataFrame:
        """Returns the intercalation constants DataFrame."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_points: NDArray[np.float64] = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=Constants.file_names.INIT_DAT_FILE,
        )

        min_distances_between_c_points: NDArray[np.float64] = DistanceMeasurer.calculate_min_distances_between_points(
            carbon_points
        )

        mean_inter_c_dist = float(
            np.mean(
                (float(np.mean(min_distances_between_c_points)),
                 atom_params.DIST_BETWEEN_ATOMS)
            )
        )

        intercalation_constants: dict[str, float] = {
            "Lattice parameter (Å)": round(atom_params.LATTICE_PARAM, 4),
            "Distance between atoms (Å)": round(atom_params.DIST_BETWEEN_ATOMS, 4),
            "Distance between layers (Å)": round(atom_params.DIST_BETWEEN_LAYERS, 4),
            "Min allowed distance between atoms (Å)": round(atom_params.MIN_RECOMENDED_DIST_BETWEEN_ATOMS, 4),
            "Distance to replace nearby atoms (Å)": round(atom_params.DIST_TO_REPLACE_NEARBY_ATOMS, 4),
            "Distance to remove too close atoms (Å)": round(atom_params.MIN_ALLOWED_DIST_BETWEEN_ATOMS, 4),
            f"Average {atom_params.ATOM_SYMBOL}-C distance (Å)": round(float(mean_inter_c_dist), 4),
            "Place opposite centers distance (Å)": round(
                atom_params.PLACE_OPPOSITE_CENTERS_DIST, 4
            ),
            "Place opposite faces distance (Å)": round(
                atom_params.PLACE_OPPOSITE_FACES_DIST, 4
            ),
        }

        # Convert the dictionary to a DataFrame
        intercalation_constants_df: pd.DataFrame = pd.DataFrame.from_dict(
            intercalation_constants, orient='index', columns=pd.Index(['Value'])
        ).reset_index().rename(columns={'index': 'Name'})

        return intercalation_constants_df

    @staticmethod
    def get_polygon_reference_sites(
        carbon_channel: ICarbonHoneycombChannel,
        site_types: tuple[PolygonSiteType, ...] | None = None,
        wall_indexes: tuple[int, ...] | None = None,
    ) -> tuple[PolygonReferenceSite, ...]:
        """Return polygon-reference sites for an already built channel."""
        return PolygonReferenceAnalyzer.get_reference_sites(
            carbon_channel, site_types=site_types, wall_indexes=wall_indexes
        )

    @staticmethod
    def measure_polygon_site_distances(
        carbon_channel: ICarbonHoneycombChannel,
        inter_atoms: IPoints,
        atom_params: ConstantsAtomParams,
        near_wall_max_dist_to_plane: float,
        alignment_tolerance: float,
        reference_wall_indexes: tuple[int, ...] | None = None,
    ) -> PolygonSiteMeasurementReport:
        """Measure polygon-site distances using explicit project-resolved defaults."""
        return PolygonReferenceAnalyzer.measure(
            carbon_channel=carbon_channel,
            inter_atoms=inter_atoms,
            center_target=atom_params.PLACE_OPPOSITE_CENTERS_DIST,
            face_target=atom_params.PLACE_OPPOSITE_FACES_DIST,
            near_wall_max_dist_to_plane=near_wall_max_dist_to_plane,
            alignment_tolerance=alignment_tolerance,
            reference_wall_indexes=reference_wall_indexes,
        )

    @staticmethod
    def get_polygon_site_distances(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> pd.DataFrame:
        """Read the selected file and return its polygon-site measurement table."""
        if params.file_name is None:
            raise ValueError("File name is required")
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]
        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )
        inter_atoms: IPoints = InterAtomsFileManager.read_inter_atoms(
            project_dir, subproject_dir, structure_dir, params.file_name
        )
        min_carbon_distances: NDArray[np.float64] = (
            DistanceMeasurer.calculate_min_distances_between_points(carbon_channel.points)
        )
        target_to_carbon: float = float(np.mean((
            float(np.mean(min_carbon_distances)),
            atom_params.DIST_BETWEEN_ATOMS,
        )))
        report: PolygonSiteMeasurementReport = PolygonReferenceAnalyzer.measure(
            carbon_channel,
            inter_atoms,
            atom_params.PLACE_OPPOSITE_CENTERS_DIST,
            atom_params.PLACE_OPPOSITE_FACES_DIST,
            near_wall_max_dist_to_plane=target_to_carbon * 1.10,
            alignment_tolerance=float(carbon_channel.ave_dist_between_closest_atoms) / 2.0,
            reference_wall_indexes=(
                IntercalationAndSorption._polygon_reference_walls_from_atom_ids(
                    inter_atoms.atom_ids
                )
            ),
        )
        rows: list[dict[str, object]] = [row.to_dict() for row in report.rows]
        min_distances_to_carbon: NDArray[np.float64] = DistanceMeasurer.calculate_min_distances(
            inter_atoms.points, carbon_channel.points
        )
        min_distances_to_inter: NDArray[np.float64] = (
            DistanceMeasurer.calculate_min_distances_between_points(inter_atoms.points)
            if len(inter_atoms.points) > 1
            else np.full(len(inter_atoms.points), np.nan, dtype=np.float64)
        )
        for index, (row, inter_atom) in enumerate(zip(rows, inter_atoms.points)):
            min_distance_to_plane: float = min(
                DistanceMeasurer.calculate_distance_from_plane(
                    np.asarray([inter_atom], dtype=np.float64), plane.plane_params
                )
                for plane in carbon_channel.planes
            )
            row["Min distance to plane"] = min_distance_to_plane
            row["Min distance to C"] = float(min_distances_to_carbon[index])
            row["Min distance to inter"] = float(min_distances_to_inter[index])
        return IntercalationAndSorption._polygon_site_measurements_ui_df(rows)

    @classmethod
    def _polygon_site_measurements_ui_df(
        cls,
        rows: list[dict[str, object]],
    ) -> pd.DataFrame:
        """Select and format the polygon measurements shown by the desktop UI."""
        measurements: pd.DataFrame = pd.DataFrame(rows)
        table: pd.DataFrame = measurements.reindex(
            columns=list(cls.POLYGON_SITE_UI_COLUMNS)
        ).copy()
        for column in cls.POLYGON_SITE_UI_COORDINATE_COLUMNS:
            table[column] = table[column].map(cls._format_coordinate_for_ui)
        for column in cls.POLYGON_SITE_UI_DISTANCE_COLUMNS:
            table[column] = table[column].map(cls._format_distance_for_ui)
        return table

    @classmethod
    def _polygon_reference_walls_from_atom_ids(
        cls,
        atom_ids: tuple[str, ...] | None,
    ) -> tuple[int, ...] | None:
        """Recover aligned source walls from generated polygon-candidate atom IDs."""
        if atom_ids is None:
            return None
        wall_indexes: list[int] = []
        for atom_id in atom_ids:
            match: re.Match[str] | None = cls.POLYGON_CANDIDATE_WALL_PATTERN.search(atom_id)
            if match is None:
                return None
            wall_indexes.append(int(match.group(1)))
        return tuple(wall_indexes)

    @staticmethod
    def _format_coordinate_for_ui(value: object) -> str | None:
        """Format one coordinate triple with two decimal places."""
        if value is None:
            return None
        if not isinstance(value, (list, tuple, np.ndarray)):
            raise TypeError(f"Expected a coordinate sequence, got {type(value).__name__}.")
        return "[" + ", ".join(f"{float(coordinate):.2f}" for coordinate in value) + "]"

    @staticmethod
    def _format_distance_for_ui(value: object) -> str | None:
        """Format one optional distance with two decimal places."""
        if value is None or bool(pd.isna(value)):
            return None
        return f"{float(value):.2f}"

    @classmethod
    def update_inter_channel_coordinates(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Update inter channel coordinates using selected file."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        # Build carbon channel from init data
        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )

        # Read the selected file
        file_name: str = params.file_name or Constants.file_names.FULL_CHANNEL_COORDINATES_CSV_FILE

        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
            to_print_warning=False,
        )

        if inter_atoms_full_channel_coordinates_df is None:
            raise IOError(f"Failed to read {params.file_name} file")

        inter_atoms: IPoints = InterAtomsParser.parse_inter_atoms_coordinates_df(
            inter_atoms_full_channel_coordinates_df
        )
        inter_atoms = InterAtomsTranslator.translate_for_all_planes(
            carbon_channel,
            inter_atoms,
            params.number_of_planes,
            params.to_to_try_to_reflect_inter_atoms,
            atom_params,
        )

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir,
            file_name=file_name)

        FileWriter.write_csv_file(df=cls._coordinates_df(inter_atoms), path_to_file=path_to_file)

        return path_to_file

    @classmethod
    def save_distance_matrix(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Save intercalated in channel details to an Excel file."""
        data: pd.DataFrame = cls.get_distance_matrix(
            project_dir, subproject_dir, structure_dir, params
        )

        result_file_name: str = (params.file_name or "intercalated-channel-coordinates").split(".")[
            0] + "_" + Constants.file_names.CHANNEL_DETAILS_XLSX_FILE

        # Write DataFrame to Excel file
        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=result_file_name
        )

        FileWriter.write_excel_file(
            df=data,
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms in channel details",
        )

        return path_to_file

    @staticmethod
    def get_distance_matrix(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> pd.DataFrame:
        """Get details of intercalated atoms in the channel."""
        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )

        file_name: str = params.file_name or Constants.file_names.FULL_CHANNEL_COORDINATES_CSV_FILE

        intercalated_coordinates_df: pd.DataFrame | None = FileReader.read_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
            to_print_warning=False,
        )

        if intercalated_coordinates_df is None:
            raise IOError(f"Failed to read {params.file_name} file")

        inter_atoms: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(
            intercalated_coordinates_df
        )

        # Prepare data for DataFrame with multi-level columns like the old implementation
        data: list[dict[tuple[str, str], float]] = []

        for inter_atom in inter_atoms.points:
            # Calculate minimum distance to carbon atoms
            min_dist_to_carbon: float = float(np.min(DistanceMeasurer.calculate_min_distances(
                np.array([inter_atom]), carbon_channel.points
            )))

            # Calculate minimum distance to planes
            min_dist_to_plane: float = float("inf")
            for plane in carbon_channel.planes:
                dist: float = DistanceMeasurer.calculate_distance_from_plane(
                    np.array([inter_atom]), plane.plane_params
                )
                if dist < min_dist_to_plane:
                    min_dist_to_plane = dist

            # Calculate distances to all other intercalated atoms
            dists_to_inter: NDArray[np.float64] = DistanceMeasurer.calculate_min_distances(
                inter_atoms.points, np.array([inter_atom])
            )
            min_dist_to_inter: float = float(np.min(dists_to_inter[dists_to_inter > 0]))  # Exclude self-distance

            # Collect data for each intercalated atom coordinate
            data.append({
                ("Intercalated atoms", "X"): round(float(inter_atom[0]), 2),
                ("Intercalated atoms", "Y"): round(float(inter_atom[1]), 2),
                ("Intercalated atoms", "Z"): round(float(inter_atom[2]), 2),
                ("Min distance to", "plane"): round(min_dist_to_plane, 2),
                ("Min distance to", "C"): round(min_dist_to_carbon, 2),
                ("Min distance to", "inter"): round(min_dist_to_inter, 2),
                **{("Dists to other intercalated atoms", f"{i}"): round(float(dist), 2)
                   for i, dist in enumerate(dists_to_inter)}
            })

        # Create DataFrame with multi-level columns
        df: pd.DataFrame = pd.DataFrame(data)

        # Set multi-level columns
        df.columns = pd.MultiIndex.from_tuples(df.columns)

        return df

    @staticmethod
    def translate_inter_to_all_channels_plot(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> None:
        """Plot intercalated atoms translated to all channels."""
        # This would show a visualization of all channels with intercalated atoms
        # For now, we'll use the existing plot functionality

        raise NotImplementedError("Not implemented")

    @classmethod
    def translate_inter_to_all_channels_generate_files(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Generate files for intercalated atoms in all channels."""
        # 1. Read intercalated atoms from channel coordinates file
        file_name: str | None = params.file_name
        if file_name is None:
            raise ValueError("File name is required")

        inter_atoms_df: pd.DataFrame | None = FileReader.read_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
            to_print_warning=False,
        )

        if inter_atoms_df is None:
            raise IOError(f"Failed to read {file_name} file")

        inter_atoms_channel: IPoints = InterAtomsParser.parse_inter_atoms_coordinates_df(
            inter_atoms_df
        )

        # 2. Build carbon structure and channels
        carbon_points: NDArray[np.float64] = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=Constants.file_names.INIT_DAT_FILE,
        )
        coordinates_carbon: IPoints = Points(carbon_points)

        carbon_channels: list[ICarbonHoneycombChannel] = (
            CarbonHoneycombActions.split_init_structure_into_separate_channels(
                coordinates_carbon=coordinates_carbon
            )
        )

        # 3. Translate to all channels (full channels + edge channels)
        all_channels_atoms: IPoints = InterAtomsTranslator.translate_for_all_channels(
            coordinates_carbon=coordinates_carbon,
            carbon_channels=carbon_channels,
            inter_atoms_channel_coordinates=inter_atoms_channel,
        )

        # 3.5. Filter out atoms with min and max X coordinates if requested
        if params.to_remove_inter_atoms_with_min_and_max_x_coordinates:
            logger.info(
                f"Removing atoms with min/max X coordinates. "
                f"Before: {len(all_channels_atoms.points)} atoms"
            )
            all_channels_atoms = PointsFilter.remove_atoms_with_min_and_max_x_coordinates(
                all_channels_atoms
            )
            logger.info(f"After filtering: {len(all_channels_atoms.points)} atoms")

        # 4. Save translated coordinates
        result_file_name: str = f"{Path(file_name).stem}_all_channels.csv"
        coords_path: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=result_file_name
        )

        FileWriter.write_csv_file(df=cls._coordinates_df(all_channels_atoms), path_to_file=coords_path)

        # # 5. Generate distance matrix using the translated atoms
        # # (update params.file_name temporarily to use the new file)
        # original_file_name: str | None = params.file_name
        # params.file_name = result_file_name
        # details_path: Path = cls.save_distance_matrix(
        #     project_dir, subproject_dir, structure_dir, params
        # )
        # params.file_name = original_file_name

        return coords_path

    @staticmethod
    def get_carbon_coords(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
    ) -> NDArray[np.float64]:
        """Get carbon structure coordinates."""
        carbon_points: NDArray[np.float64] = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=Constants.file_names.INIT_DAT_FILE,
        )
        return carbon_points

    @staticmethod
    def get_inter_coords(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        file_name: str,
    ) -> NDArray[np.float64] | None:
        """Get intercalated atoms coordinates."""
        try:
            # Read existing intercalated coordinates from CSV or a legacy format.
            intercalated_coordinates_df: pd.DataFrame | None = FileReader.read_result_data_file(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                file_name=file_name,
                to_print_warning=False,
            )

            if intercalated_coordinates_df is not None:
                inter_atoms: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(
                    intercalated_coordinates_df
                )
                return inter_atoms.points

            return None

        except Exception:
            return None

    @classmethod
    def get_translated_inter_coords(
        cls,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        file_name: str,
    ) -> NDArray[np.float64] | None:
        """Get translated intercalated atoms coordinates."""
        try:
            # This would be the result of translation operations
            # For now, return the same as regular inter coords
            return cls.get_inter_coords(
                project_dir, subproject_dir, structure_dir,
                file_name=file_name
            )

        except Exception:
            return None
