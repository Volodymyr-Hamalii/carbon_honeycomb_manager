
"""Intercalation and sorption analysis functionality."""

from pathlib import Path
import numpy as np
from numpy.typing import NDArray
import pandas as pd

from src.interfaces import (
    IPoints,
    ICarbonHoneycombChannel,
    PMvpParams,
    PCoordinateLimits,
)
from src.entities import Points, CoordinateLimits
from src.services import (
    Constants,
    ConstantsAtomParams,
    ATOM_PARAMS_MAP,
    Logger,
    FileReader,
    FileWriter,
    PathBuilder,
    StructureVisualizer,
    VisualizationParams,
    StructureVisualParams,
    DistanceMeasurer,
)

from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller
from .build_intercalated_structure import (
    CoordinatesTableManager,
    InterAtomsParser,
    InterAtomsTranslator,
)


logger = Logger("IntercalationAndSorption")


class IntercalationAndSorption:
    """Intercalation and sorption analysis functionality."""

    @staticmethod
    def plot_inter_in_c_structure(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> None:
        """Plot intercalated atoms in carbon structure."""
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: ICarbonHoneycombChannel = CarbonHoneycombModeller.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE
        )

        inter_atoms_plane_coordinates: IPoints = InterAtomsParser.get_inter_atoms_plane_coordinates(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            carbon_channel=carbon_channel,
            number_of_planes=params.number_of_planes,
            atom_params=atom_params,
            file_name=params.file_name,
            to_replace_nearby_atoms=params.to_replace_nearby_atoms,
            to_remove_too_close_atoms=params.to_remove_too_close_atoms,
        )

        plane_points: NDArray[np.float64] = np.vstack(
            [carbon_channel.planes[i].points for i in range(params.number_of_planes)]
        )

        IntercalationAndSorption._show_structures(
            carbon_channel_points=plane_points,
            inter_atoms=inter_atoms_plane_coordinates.points,
            subproject_dir=subproject_dir,
            title=structure_dir,
            params=params,
        )

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
            np.lexsort((coordinates_filtered[:, 2],
                        coordinates_filtered[:, 1],
                        coordinates_filtered[:, 0],
                        ))]

        inter_atoms_plane_coordinates = Points(points=coordinates_filtered)

        path_to_file = PathBuilder.build_path_to_result_data_file(
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

        inter_atoms_coordinates: IPoints = InterAtomsParser.parse_inter_atoms_coordinates_df(
            inter_atoms_full_channel_coordinates_df
        )
        inter_atoms_coordinates = InterAtomsTranslator.translate_for_all_planes(
            carbon_channel,
            inter_atoms_coordinates,
            params.number_of_planes,
            params.to_to_try_to_reflect_inter_atoms,
            atom_params,
        )

        if params.number_of_planes > 1:
            # Build only specified planes
            carbon_channel_points: NDArray[np.float64] = np.vstack(
                [carbon_channel.planes[i].points for i in range(params.number_of_planes)]
            )
        else:
            # Build all planes
            carbon_channel_points: NDArray[np.float64] = carbon_channel.points

        IntercalationAndSorption._show_structures(
            carbon_channel_points=carbon_channel_points,
            inter_atoms=inter_atoms_coordinates.points,
            subproject_dir=subproject_dir,
            title=structure_dir,
            params=params,
        )

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
            intercalation_constants, orient='index', columns=['Value']
        ).reset_index().rename(columns={'index': 'Name'})

        return intercalation_constants_df

    @staticmethod
    def _show_structures(
        carbon_channel_points: NDArray[np.float64],
        inter_atoms: NDArray[np.float64],
        subproject_dir: str,
        params: PMvpParams,
        title: str | None = None,
    ) -> None:
        """Show carbon and intercalated structures with visualization."""
        coordinate_limits: PCoordinateLimits = CoordinateLimits(
            x_min=params.x_min,
            x_max=params.x_max,
            y_min=params.y_min,
            y_max=params.y_max,
            z_min=params.z_min,
            z_max=params.z_max,
        )

        to_show_inter_atoms_indexes: bool = params.to_show_inter_atoms_indexes

        inter_atoms_visual_params_map: dict[str, list[StructureVisualParams]] = {
            "al": [VisualizationParams.al_1, VisualizationParams.al_2, VisualizationParams.al_3],
            "default": [VisualizationParams.al_1, VisualizationParams.al_2, VisualizationParams.al_3],
            # "ar": [VisualizationParams.ar_1, VisualizationParams.ar_2, VisualizationParams.ar_3],
        }

        visual_params_key: str = subproject_dir.lower()
        if visual_params_key not in inter_atoms_visual_params_map:
            visual_params_key = "default"
        inter_atoms_visual_params: list[StructureVisualParams] = inter_atoms_visual_params_map[
            visual_params_key
        ]

        if params.num_of_inter_atoms_layers == 1:
            StructureVisualizer.show_two_structures(
                coordinates_first=carbon_channel_points,
                coordinates_second=inter_atoms,
                title=title,
                to_build_bonds=params.to_build_bonds,
                num_of_min_distances=params.bonds_num_of_min_distances,
                skip_first_distances=params.bonds_skip_first_distances,
                to_show_coordinates=params.to_show_coordinates,
                to_show_indexes_first=False,
                to_show_indexes_second=to_show_inter_atoms_indexes,
                coordinate_limits_first=coordinate_limits,
                coordinate_limits_second=coordinate_limits,
                visual_params_first=VisualizationParams.carbon,
                visual_params_second=inter_atoms_visual_params[0],
            )

        elif params.num_of_inter_atoms_layers == 2:
            # Split the inter_atoms by layers along Oz (by rounded z coordinate)
            al_groups_with_indices: list[tuple[NDArray[np.float64], NDArray[np.int64]]] = (
                IntercalationAndSorption._split_atoms_along_z_axis(inter_atoms)
            )

            a_layer_indices: list[int] = []
            b_layer_indices: list[int] = []

            for i, (group, indices) in enumerate(al_groups_with_indices):
                if i % params.num_of_inter_atoms_layers == 0:
                    a_layer_indices.extend(indices)
                else:
                    b_layer_indices.extend(indices)

            StructureVisualizer.show_structures(
                coordinates_list=[
                    carbon_channel_points,
                    inter_atoms[a_layer_indices],
                    inter_atoms[b_layer_indices],
                ],
                visual_params_list=[
                    VisualizationParams.carbon,
                    inter_atoms_visual_params[0],
                    inter_atoms_visual_params[1],
                ],
                to_build_bonds_list=[
                    params.to_build_bonds,
                    False,
                    False,
                ],
                to_show_indexes_list=[
                    False,
                    to_show_inter_atoms_indexes,
                    to_show_inter_atoms_indexes,
                ],
                title=title,
                num_of_min_distances=params.bonds_num_of_min_distances,
                skip_first_distances=params.bonds_skip_first_distances,
                to_show_coordinates=params.to_show_coordinates,
                custom_indices_list=[None, a_layer_indices, b_layer_indices],
                coordinate_limits_list=[coordinate_limits for _ in range(3)],
            )

        elif params.num_of_inter_atoms_layers == 3:
            al_groups_with_indices: list[tuple[NDArray[np.float64], NDArray[np.int64]]] = (
                IntercalationAndSorption._split_atoms_along_z_axis(inter_atoms)
            )

            a_layer_indices: list[int] = []
            b_layer_indices: list[int] = []
            c_layer_indices: list[int] = []

            for i, (group, indices) in enumerate(al_groups_with_indices):
                if i % params.num_of_inter_atoms_layers == 0:
                    a_layer_indices.extend(indices)
                elif i % params.num_of_inter_atoms_layers == 1:
                    b_layer_indices.extend(indices)
                else:
                    c_layer_indices.extend(indices)

            StructureVisualizer.show_structures(
                coordinates_list=[
                    carbon_channel_points,
                    inter_atoms[a_layer_indices],
                    inter_atoms[b_layer_indices],
                    inter_atoms[c_layer_indices],
                ],
                visual_params_list=[
                    VisualizationParams.carbon,
                    inter_atoms_visual_params[0],
                    inter_atoms_visual_params[1],
                    inter_atoms_visual_params[2],
                ],
                to_build_bonds_list=[
                    params.to_build_bonds,
                    False,
                    False,
                    False,
                ],
                to_show_indexes_list=[
                    False,
                    to_show_inter_atoms_indexes,
                    to_show_inter_atoms_indexes,
                    to_show_inter_atoms_indexes,
                ],
                title=title,
                num_of_min_distances=params.bonds_num_of_min_distances,
                skip_first_distances=params.bonds_skip_first_distances,
                to_show_coordinates=params.to_show_coordinates,
                custom_indices_list=[None, a_layer_indices, b_layer_indices, c_layer_indices],
                coordinate_limits_list=[coordinate_limits for _ in range(4)],
            )

        else:
            raise NotImplementedError(f"Number of layers {params.num_of_inter_atoms_layers} is not implemented")

    @staticmethod
    def _split_atoms_along_z_axis(
        coordinates: NDArray[np.float64]
    ) -> list[tuple[NDArray[np.float64], NDArray[np.int64]]]:
        """Returns grouped coordinates with their original indices, grouped by rounded Z coordinate."""
        # Round Z values to the nearest integer or a desired precision
        rounded_z_values: NDArray[np.float64] = np.round(coordinates[:, 2], decimals=1)

        # Get unique rounded Z values
        unique_z_values: NDArray[np.float64] = np.unique(rounded_z_values)

        # Group points and their indices by their rounded Z coordinate
        grouped_coordinates: list[tuple[NDArray[np.float64], NDArray[np.int64]]] = [
            (coordinates[rounded_z_values == z], np.where(rounded_z_values == z)[0])
            for z in unique_z_values
        ]

        return grouped_coordinates

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
            project_dir, subproject_dir, structure_dir, file_name=params.file_name or "intercalated-channel-coordinates.xlsx"
        )

        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if inter_atoms_full_channel_coordinates_df is None:
            raise IOError(f"Failed to read {params.file_name} Excel file")

        inter_atoms: IPoints = InterAtomsParser.parse_inter_atoms_coordinates_df(
            inter_atoms_full_channel_coordinates_df
        )
        inter_atoms: IPoints = InterAtomsTranslator.translate_for_all_planes(
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

    @staticmethod
    def save_inter_in_channel_details(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> Path:
        """Save intercalated in channel details to an Excel file."""
        data: pd.DataFrame = IntercalationAndSorption.get_inter_in_channel_details(
            project_dir, subproject_dir, structure_dir, params
        )

        result_file_name: str = (params.file_name or "intercalated-channel-coordinates").split(".")[0] + "_" + Constants.file_names.CHANNEL_DETAILS_XLSX_FILE

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
    def get_inter_in_channel_details(
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
            project_dir, subproject_dir, structure_dir, file_name=params.file_name or "intercalated-channel-coordinates.xlsx"
        )

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
        IntercalationAndSorption.plot_inter_in_c_structure(
            project_dir, subproject_dir, structure_dir, params
        )

    @staticmethod
    def translate_inter_to_all_channels_generate_files(
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        params: PMvpParams,
    ) -> tuple[Path, Path]:
        """Generate files for intercalated atoms in all channels."""
        # This would generate multiple files - for now, we'll create basic outputs
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]
        
        # Generate the main coordinates file
        coords_path: Path = IntercalationAndSorption.generate_inter_plane_coordinates_file(
            project_dir, subproject_dir, structure_dir, params
        )
        
        # Generate the details file
        details_path = IntercalationAndSorption.save_inter_in_channel_details(
            project_dir, subproject_dir, structure_dir, params
        )
        
        return coords_path, details_path
