
"""Intercalation and sorption analysis functionality."""

from pathlib import Path
import numpy as np
from numpy.typing import NDArray
import pandas as pd

from src.interfaces import (
    IPoints,
    ICarbonHoneycombChannel,
    PMvpParams,
)
from src.entities import Points
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


logger = Logger("IntercalationAndSorption")


class IntercalationAndSorption:
    """Intercalation and sorption analysis functionality."""
    @staticmethod
    def generate_inter_plane_coordinates_file(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Generate intercalated plane coordinates file."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )

        inter_atoms_plane_coordinates: IPoints = InterAtomsParser.build_inter_atoms_plane_coordinates(
            carbon_channel,
            num_of_planes=params.number_of_planes,
            atom_params=atom_params,
            to_replace_nearby_atoms=params.to_replace_nearby_atoms,
            to_remove_too_close_atoms=params.to_remove_too_close_atoms,
        )

        # Filter out atoms with min and max coordinates
        coordinates: NDArray[np.float64] = inter_atoms_plane_coordinates.points
        coordinates_filtered: NDArray[np.float64] = coordinates[
            (coordinates[:, 0] >= params.x_min) &
            (coordinates[:, 0] <= params.x_max) &
            (coordinates[:, 1] >= params.y_min) &
            (coordinates[:, 1] <= params.y_max) &
            (coordinates[:, 2] >= params.z_min) &
            (coordinates[:, 2] <= params.z_max)
        ]

        # Sort by z coordinate
        coordinates_filtered = coordinates_filtered[
            np.lexsort((
                coordinates_filtered[:, 0],
                coordinates_filtered[:, 1],
                coordinates_filtered[:, 2],
            ))]

        inter_atoms_plane_coordinates = Points(points=coordinates_filtered)

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir,
            file_name=Constants.file_names.PLANE_COORDINATES_XLSX_FILE,
        )

        path_to_file_result: Path | None = FileWriter.write_excel_file(
            df=inter_atoms_plane_coordinates.to_df(columns=["i", "x_inter", "y_inter", "z_inter"]),
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms for the plane",
        )

        if path_to_file_result is None:
            raise IOError(f"Failed to write {Constants.file_names.PLANE_COORDINATES_XLSX_FILE} file.")

        return path_to_file_result

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
        """
        Read intercalated atoms coordinates from the Excel table and translate the structure to other planes.
        """
        file_name: str | None = params.file_name
        if file_name is None:
            raise ValueError("File name is required")

        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=file_name
        )

        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if inter_atoms_full_channel_coordinates_df is None:
            raise IOError(f"Failed to read {params.file_name} Excel file")

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
        }

        # Convert the dictionary to a DataFrame
        intercalation_constants_df: pd.DataFrame = pd.DataFrame.from_dict(
            intercalation_constants, orient='index', columns=pd.Index(['Value'])
        ).reset_index().rename(columns={'index': 'Name'})

        return intercalation_constants_df

    @staticmethod
    def update_inter_channel_coordinates(
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
        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir,
            file_name=params.file_name or "intercalated-channel-coordinates.xlsx")

        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if inter_atoms_full_channel_coordinates_df is None:
            raise IOError(f"Failed to read {params.file_name} Excel file")

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

        FileWriter.write_excel_file(
            df=inter_atoms.to_df(columns=["i", "x_inter", "y_inter", "z_inter"]),
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms for the channel",
        )

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

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir,
            file_name=params.file_name or "intercalated-channel-coordinates.xlsx")

        intercalated_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if intercalated_coordinates_df is None:
            raise IOError(f"Failed to read {params.file_name} Excel file")

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
    ) -> tuple[Path, Path]:
        """Generate files for intercalated atoms in all channels."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        # 1. Read intercalated atoms from channel coordinates file
        file_name: str | None = params.file_name
        if file_name is None:
            raise ValueError("File name is required")

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=file_name
        )

        inter_atoms_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file, to_print_warning=False
        )

        if inter_atoms_df is None:
            raise IOError(f"Failed to read {file_name} Excel file")

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
        result_file_name: str = file_name.replace(".xlsx", "_all_channels.xlsx")
        coords_path: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=result_file_name
        )

        FileWriter.write_excel_file(
            df=all_channels_atoms.to_df(columns=["i", "x_inter", "y_inter", "z_inter"]),
            path_to_file=coords_path,
            sheet_name="Intercalated atoms for all channels",
        )

        # 5. Generate distance matrix using the translated atoms
        # (update params.file_name temporarily to use the new file)
        original_file_name: str | None = params.file_name
        params.file_name = result_file_name
        details_path: Path = cls.save_distance_matrix(
            project_dir, subproject_dir, structure_dir, params
        )
        params.file_name = original_file_name

        return coords_path, details_path

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
            # Try to read existing intercalated coordinates file
            path_to_file: Path = PathBuilder.build_path_to_result_data_file(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                file_name=file_name
            )

            intercalated_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
                path_to_file=path_to_file,
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
