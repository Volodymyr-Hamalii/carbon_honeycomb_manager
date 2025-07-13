from pathlib import Path
import numpy as np
import pandas as pd

from src.utils import (
    Constants,
    ConstantsAtomParams,
    ATOM_PARAMS_MAP,
    Logger,
    FileReader,
    FileWriter,
    PathBuilder,
)
from src.base_structure_classes import LatticeType, Points, CoordinateLimits
from src.coordinate_operations import DistanceMeasure
from src.structure_visualizer import (
    StructureVisualizer,
    VisualizationParams,
    StructureVisualParams,
)
from src.projects import (
    IntercalatedChannelBuilder,
    CarbonHoneycombChannel,
    CarbonHoneycombActions,
    CoordinatesTableManager,
    InterAtomsParser,
    InterAtomsTranslator,
)
from .view_model_params_setter import VMParamsSetter


logger = Logger("Actions")


class VMIntercalationAndSorption(VMParamsSetter):
    def plot_inter_in_c_structure(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        inter_atoms_plane_coordinates: Points = InterAtomsParser.get_inter_atoms_plane_coordinates(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            carbon_channel=carbon_channel,
            number_of_planes=self.number_of_planes,
            atom_params=atom_params,
            file_name=self.file_name,
            to_replace_nearby_atoms=self.to_replace_nearby_atoms,
            to_remove_too_close_atoms=self.to_remove_too_close_atoms,
        )

        plane_points: np.ndarray = np.vstack(
            [carbon_channel.planes[i].points for i in range(self.number_of_planes)])

        self._show_structures(
            carbon_channel_points=plane_points,
            inter_atoms=inter_atoms_plane_coordinates.points,
            subproject_dir=subproject_dir,
            title=structure_dir,
        )

    def generate_inter_plane_coordinates_file(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> Path:
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        inter_atoms_plane_coordinates: Points = InterAtomsParser.build_inter_atoms_plane_coordinates(
            carbon_channel,
            num_of_planes=self.number_of_planes,
            atom_params=atom_params,
            to_replace_nearby_atoms=self.to_replace_nearby_atoms,
            to_remove_too_close_atoms=self.to_remove_too_close_atoms,
        )

        # Filter out atoms with min and max coordinates
        coordinates: np.ndarray = inter_atoms_plane_coordinates.points
        coordinates_filtered: np.ndarray = coordinates[
            (coordinates[:, 0] >= self.x_min) &
            (coordinates[:, 0] <= self.x_max) &
            (coordinates[:, 1] >= self.y_min) &
            (coordinates[:, 1] <= self.y_max) &
            (coordinates[:, 2] >= self.z_min) &
            (coordinates[:, 2] <= self.z_max)
        ]

        # Sort by z coordinate
        coordinates_filtered = coordinates_filtered[
            np.lexsort((coordinates_filtered[:, 2],
                        coordinates_filtered[:, 1],
                        coordinates_filtered[:, 0],
                        ))]

        inter_atoms_plane_coordinates: Points = Points(points=coordinates_filtered)

        path_to_file = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.PLANE_COORDINATES_XLSX_FILE,
        )

        path_to_file: Path | None = FileWriter.write_excel_file(
            df=inter_atoms_plane_coordinates.to_df(columns=["i", "x_inter", "y_inter", "z_inter"]),
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms for the plane",
        )

        if path_to_file is None:
            raise IOError(f"Failed to write {Constants.file_names.PLANE_COORDINATES_XLSX_FILE} file.")

        return path_to_file

    def update_inter_plane_coordinates_file(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> Path:
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        path_to_file: Path = CoordinatesTableManager.update_plane_tbl_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            carbon_channel=carbon_channel,
            number_of_planes=self.number_of_planes,
            atom_params=atom_params,
            file_name=self.file_name,
            to_replace_nearby_atoms=self.to_replace_nearby_atoms,
            to_remove_too_close_atoms=self.to_remove_too_close_atoms,
        )

        return path_to_file

    def translate_inter_atoms_to_other_planes(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        """
        Read intercalated atoms coordinates from the Excel table and translate the structure to other planes.
        """
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        # inter_atoms: Points = InterAtomsParser.get_inter_atoms_channel_coordinates(
        #     structure_dir, carbon_channel, self.number_of_planes, self.to_to_try_to_reflect_inter_atoms)

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=self.file_name)

        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if inter_atoms_full_channel_coordinates_df is None:
            raise IOError(f"Failed to read {self.file_name} Excel file")

        inter_atoms_coordinates: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(
            inter_atoms_full_channel_coordinates_df)
        inter_atoms_coordinates: Points = InterAtomsTranslator.translate_for_all_planes(
            carbon_channel,
            inter_atoms_coordinates,
            self.number_of_planes,
            self.to_to_try_to_reflect_inter_atoms,
            atom_params,
        )

        if self.number_of_planes > 1:
            # Build only specified planes
            carbon_channel_points: np.ndarray = np.vstack(
                [carbon_channel.planes[i].points for i in range(self.number_of_planes)])
        else:
            # Build all planes
            carbon_channel_points: np.ndarray = carbon_channel.points

        self._show_structures(
            carbon_channel_points=carbon_channel_points,
            inter_atoms=inter_atoms_coordinates.points,
            subproject_dir=subproject_dir,
            title=structure_dir,
        )

    def update_inter_channel_coordinates(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> Path:
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        # inter_atoms: Points = InterAtomsParser.get_inter_atoms_channel_coordinates(
        #     structure_dir, carbon_channel, self.number_of_planes, self.to_to_try_to_reflect_inter_atoms)

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=self.file_name)

        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if inter_atoms_full_channel_coordinates_df is None:
            raise IOError(f"Failed to read {self.file_name} Excel file")

        inter_atoms: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(
            inter_atoms_full_channel_coordinates_df)
        inter_atoms: Points = InterAtomsTranslator.translate_for_all_planes(
            carbon_channel,
            inter_atoms,
            self.number_of_planes,
            self.to_to_try_to_reflect_inter_atoms,
            atom_params,
        )

        FileWriter.write_excel_file(
            df=inter_atoms.to_df(columns=["i", "x_inter", "y_inter", "z_inter"]),
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms for the channel",
        )

        return path_to_file

    def save_inter_in_channel_details(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> Path:
        """
        Save intercalated in channel details to an Excel file.
        """
        data: pd.DataFrame = self.get_inter_in_channel_details(
            project_dir, subproject_dir, structure_dir)

        result_file_name: str = self.file_name.split(".")[0] + "_" + Constants.file_names.CHANNEL_DETAILS_XLSX_FILE

        # Write DataFrame to Excel file
        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=result_file_name)

        FileWriter.write_excel_file(
            df=data,
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms in channel details",
        )

        return path_to_file

    def get_inter_in_channel_details(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> pd.DataFrame:
        """
        Get details of intercalated atoms in the channel.
        """
        carbon_channel: CarbonHoneycombChannel = InterAtomsParser.build_carbon_channel(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=self.file_name)

        intercalated_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if intercalated_coordinates_df is None:
            raise IOError(f"Failed to read {self.file_name} Excel file")

        inter_atoms: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(
            intercalated_coordinates_df)

        # Prepare data for DataFrame
        data: list[dict] = []

        for inter_atom in inter_atoms.points:
            min_dist_to_plane: float = float("inf")
            min_dist_to_carbon: float = np.min(DistanceMeasure.calculate_min_distances(
                np.array([inter_atom]), carbon_channel.points))

            for plane in carbon_channel.planes:
                dist: float = DistanceMeasure.calculate_distance_from_plane(
                    np.array([inter_atom]), plane.plane_params)

                if dist < min_dist_to_plane:
                    min_dist_to_plane = dist

            dists_to_inter: np.ndarray = DistanceMeasure.calculate_min_distances(
                inter_atoms.points, np.array([inter_atom]))
            min_dist_to_inter: float = np.min(dists_to_inter[dists_to_inter > 0])  # Exclude self-distance

            # Collect data for each intercalated atoms coordinate
            data.append({
                ("Intercalated atoms", "X"): np.round(inter_atom[0], 2),
                ("Intercalated atoms", "Y"): np.round(inter_atom[1], 2),
                ("Intercalated atoms", "Z"): np.round(inter_atom[2], 2),
                ("Min distance to", "plane"): np.round(min_dist_to_plane, 2),
                ("Min distance to", "C"): np.round(min_dist_to_carbon, 2),
                ("Min distance to", "inter"): np.round(min_dist_to_inter, 2),
                **{("Dists to other intercalated atoms",
                    f"{i}"): np.round(dist, 2) for i, dist in enumerate(dists_to_inter)}
            })

        # Create DataFrame with multi-level columns
        df: pd.DataFrame = pd.DataFrame(data)

        # Set multi-level columns
        df.columns = pd.MultiIndex.from_tuples(df.columns)

        return df

    def get_inter_chc_constants(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> pd.DataFrame:
        """ Returns the dict with name of the table and the table itself. """

        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        carbon_points: np.ndarray = FileReader.read_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=Constants.file_names.INIT_DAT_FILE,
        )

        min_distances_between_c_points: np.ndarray = DistanceMeasure.calculate_min_distances_between_points(
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

    def translate_inter_to_all_channels_plot(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        """
        Read intercalated atoms plane coordinates from the Excel table and translate the structure to other planes.
        Returns path_to_inter_atoms_xlsx_file, path_to_inter_atoms_dat_file, path_to_c_dat_file.
        """
        coordinates_carbon: Points = IntercalatedChannelBuilder.build_carbon_coordinates(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=self.file_name)

        al_one_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if al_one_channel_coordinates_df is None:
            raise IOError(f"Failed to read {self.file_name} Excel file")

        inter_atoms: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(al_one_channel_coordinates_df)

        if self.to_remove_inter_atoms_with_min_and_max_x_coordinates:
            logger.info("Removing intercalated atoms with min and max X coordinates")
            points_upd: np.ndarray = inter_atoms.points[
                (inter_atoms.points[:, 0] != np.min(inter_atoms.points[:, 0])) &
                (inter_atoms.points[:, 0] != np.max(inter_atoms.points[:, 0]))
            ]
            inter_atoms = Points(points=points_upd)

        self._show_structures(
            carbon_channel_points=coordinates_carbon.points,
            inter_atoms=inter_atoms.points,
            subproject_dir=subproject_dir,
            title=structure_dir,
        )

    def translate_inter_to_all_channels_generate_files(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> tuple[Path, Path, Path]:
        """
        Read intercalated atoms plane coordinates from the Excel table
        and translate the structure to other planes.
        Returns path_to_inter_atoms_xlsx_file, path_to_inter_atoms_dat_file, path_to_c_dat_file.
        """
        atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

        coordinates_carbon: Points = IntercalatedChannelBuilder.build_carbon_coordinates(
            project_dir, subproject_dir, structure_dir, file_name=Constants.file_names.INIT_DAT_FILE)

        carbon_channels: list[CarbonHoneycombChannel] = CarbonHoneycombActions.split_init_structure_into_separate_channels(
            coordinates_carbon=coordinates_carbon)

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=self.file_name)

        al_one_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(
            path_to_file=path_to_file,
            to_print_warning=False,
        )

        if al_one_channel_coordinates_df is None:
            raise IOError(f"Failed to read {self.file_name} Excel file")

        inter_atoms_channel_coordinates: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(
            al_one_channel_coordinates_df)

        inter_atoms: Points = InterAtomsTranslator.translate_for_all_channels(
            coordinates_carbon=coordinates_carbon,
            carbon_channels=carbon_channels,
            inter_atoms_channel_coordinates=inter_atoms_channel_coordinates,
        )

        if self.to_remove_inter_atoms_with_min_and_max_x_coordinates:
            logger.info("Removing intercalated atoms with min and max X coordinates")
            points_upd: np.ndarray = inter_atoms.points[
                (inter_atoms.points[:, 0] != np.min(inter_atoms.points[:, 0])) &
                (inter_atoms.points[:, 0] != np.max(inter_atoms.points[:, 0]))
            ]
            inter_atoms = Points(points=points_upd)

        self._show_structures(
            carbon_channel_points=coordinates_carbon.points,
            inter_atoms=inter_atoms.points,
            subproject_dir=subproject_dir,
            title=structure_dir,
        )

        if " " in self.file_name:
            parts: list[str] = self.file_name.split(" ")
            parts.pop(0)
            parts[-1] = parts[-1].split(".")[0]
            output_dir_name: str = " ".join(parts)
        else:
            output_dir_name: str = "all_channels"

        file_name_xlsx: str = self._get_path_to_file_to_save(f"{output_dir_name}/{Constants.file_names.ALL_CHANNELS_COORDINATES_XLSX_FILE}")
        path_to_inter_atoms_xlsx_file: Path | None = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=file_name_xlsx)

        path_to_inter_atoms_xlsx_file = FileWriter.write_excel_file(
            df=inter_atoms.to_df(columns=["i", "x_inter", "y_inter", "z_inter"]),
            path_to_file=path_to_inter_atoms_xlsx_file,
            sheet_name="Intercalated atoms for the channel",
        )

        if path_to_inter_atoms_xlsx_file is None:
            raise IOError(f"Failed to write {file_name_xlsx} file")

        file_name_dat: str = self._get_path_to_file_to_save(f"{output_dir_name}/{atom_params.ATOM_SYMBOL}.dat")
        path_to_inter_atoms_dat_file: Path | None = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=file_name_dat)
        path_to_inter_atoms_dat_file = FileWriter.write_dat_file(
            inter_atoms.points,
            path_to_file=path_to_inter_atoms_dat_file,
        )

        if path_to_inter_atoms_dat_file is None:
            raise IOError(f"Failed to write {file_name_dat} file")

        file_name_c_dat: str = self._get_path_to_file_to_save(f"{output_dir_name}/{Constants.file_names.C_ALL_CHANNELS_COORDINATES_DAT_FILE}")
        path_to_c_dat_file: Path | None = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=file_name_c_dat)
        path_to_c_dat_file = FileWriter.write_dat_file(
            coordinates_carbon.points,
            path_to_file=path_to_c_dat_file,
        )

        if path_to_c_dat_file is None:
            raise IOError(f"Failed to write {file_name_c_dat} file")

        return path_to_inter_atoms_xlsx_file, path_to_inter_atoms_dat_file, path_to_c_dat_file

    def _build_inter_atoms(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            coordinate_limits: CoordinateLimits,
    ) -> Points:
        inter_atoms_lattice_type = LatticeType(self.inter_atoms_lattice_type)

        if inter_atoms_lattice_type.is_cell:
            return IntercalatedChannelBuilder.build_inter_coordinates_for_cell(
                to_translate_inter=self.to_translate_inter,
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                file_name=self.file_name,
                coordinate_limits=coordinate_limits,
            )

        else:
            # Fill the volume with aluminium for close-packed lattice
            atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[subproject_dir.lower()]

            return IntercalatedChannelBuilder.build_inter_coordinates_for_close_packed(
                inter_atoms_lattice_type=inter_atoms_lattice_type,
                coordinate_limits=coordinate_limits,
                atom_params=atom_params,
            )

    def _show_structures(
        self,
        carbon_channel_points: np.ndarray,
        inter_atoms: np.ndarray,
        subproject_dir: str,
        title: str | None = None,
    ) -> None:
        # TODO: refactor

        coordinate_limits: CoordinateLimits = CoordinateLimits(
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max,
            z_min=self.z_min,
            z_max=self.z_max,
        )

        to_show_inter_atoms_indexes: bool = self.to_show_inter_atoms_indexes

        inter_atoms_visual_params_map: dict[str, list[StructureVisualParams]] = {
            "al": [VisualizationParams.al_1, VisualizationParams.al_2, VisualizationParams.al_3],
            "ar": [VisualizationParams.ar_1, VisualizationParams.ar_2, VisualizationParams.ar_3],
        }
        inter_atoms_visual_params: list[StructureVisualParams] = inter_atoms_visual_params_map[subproject_dir.lower()]

        if self.num_of_inter_atoms_layers == 1:
            StructureVisualizer.show_two_structures(
                coordinates_first=carbon_channel_points,
                coordinates_second=inter_atoms,
                title=title,
                to_build_bonds=self.to_build_bonds,
                num_of_min_distances=self.bonds_num_of_min_distances,
                skip_first_distances=self.bonds_skip_first_distances,
                to_show_coordinates=self.to_show_coordinates,
                to_show_indexes_first=False,
                to_show_indexes_second=to_show_inter_atoms_indexes,
                # is_interactive_mode=self.interactive_mode,
                coordinate_limits_first=coordinate_limits,
                coordinate_limits_second=coordinate_limits,
                visual_params_second=inter_atoms_visual_params[0],
            )

        elif self.num_of_inter_atoms_layers == 2:
            # Split the inter_atoms by layers along Oz (by rounded z coordinate)
            al_groups_with_indices: list[tuple[np.ndarray, np.ndarray]] = self._split_atoms_along_z_axis(inter_atoms)

            a_layer_indices: list[int] = []
            b_layer_indices: list[int] = []

            for i, (group, indices) in enumerate(al_groups_with_indices):
                if i % self.num_of_inter_atoms_layers == 0:
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
                    self.to_build_bonds,
                    False,
                    False,
                ],
                to_show_indexes_list=[
                    False,
                    to_show_inter_atoms_indexes,
                    to_show_inter_atoms_indexes,
                ],
                title=title,
                num_of_min_distances=self.bonds_num_of_min_distances,
                skip_first_distances=self.bonds_skip_first_distances,
                to_show_coordinates=self.to_show_coordinates,
                # is_interactive_mode=self.interactive_mode,
                custom_indices_list=[None, a_layer_indices, b_layer_indices],
                coordinate_limits_list=[coordinate_limits for _ in range(3)],
            )

        elif self.num_of_inter_atoms_layers == 3:
            al_groups_with_indices: list[tuple[np.ndarray, np.ndarray]] = self._split_atoms_along_z_axis(inter_atoms)

            a_layer_indices: list[int] = []
            b_layer_indices: list[int] = []
            c_layer_indices: list[int] = []

            for i, (group, indices) in enumerate(al_groups_with_indices):
                if i % self.num_of_inter_atoms_layers == 0:
                    a_layer_indices.extend(indices)
                elif i % self.num_of_inter_atoms_layers == 1:
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
                    self.to_build_bonds,
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
                num_of_min_distances=self.bonds_num_of_min_distances,
                skip_first_distances=self.bonds_skip_first_distances,
                to_show_coordinates=self.to_show_coordinates,
                # is_interactive_mode=self.interactive_mode,
                custom_indices_list=[None, a_layer_indices, b_layer_indices, c_layer_indices],
                coordinate_limits_list=[coordinate_limits for _ in range(4)],
            )

        else:
            raise NotImplementedError(f"Number of layers {self.num_of_inter_atoms_layers} is not implemented")

    @staticmethod
    def _split_atoms_along_z_axis(coordinates: np.ndarray) -> list[tuple[np.ndarray, np.ndarray]]:
        """ Returns grouped coordinates with their original indices, grouped by rounded Z coordinate. """
        # Round Z values to the nearest integer or a desired precision
        rounded_z_values: np.ndarray = np.round(coordinates[:, 2], decimals=1)

        # Get unique rounded Z values
        unique_z_values: np.ndarray = np.unique(rounded_z_values)

        # Group points and their indices by their rounded Z coordinate
        grouped_coordinates: list[tuple[np.ndarray, np.ndarray]] = [
            (coordinates[rounded_z_values == z], np.where(rounded_z_values == z)[0])
            for z in unique_z_values
        ]

        return grouped_coordinates

    def _get_path_to_file_to_save(self, file_name: str) -> str:
        if "/" in self.file_name:
            return self.file_name.split("/")[-2] + "/" + file_name
        return file_name
