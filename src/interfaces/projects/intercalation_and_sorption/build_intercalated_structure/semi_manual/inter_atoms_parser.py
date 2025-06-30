from pathlib import Path
import numpy as np
import pandas as pd

from src_1.utils import Constants, ConstantsAtomParams, Logger, FileReader, PathBuilder
from src_1.base_structure_classes import Points
from src_1.projects.carbon_honeycomb_actions import (
    CarbonHoneycombChannel,
    CarbonHoneycombActions,
)

from ..intercalated_channel_builder import (
    IntercalatedChannelBuilder,
)
from ..based_on_planes_configs import (
    InterAtomsBuilder,
    InterAtomsFilter,
)
from .inter_atoms_translator import InterAtomsTranslator


logger = Logger("AtomsBuilder")


class InterAtomsParser:
    @classmethod
    def get_inter_atoms_channel_coordinates(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            carbon_channel: CarbonHoneycombChannel,
            number_of_planes: int,
            to_try_to_reflect_inter_atoms: bool,
            to_replace_nearby_atoms: bool,
            to_remove_too_close_atoms: bool,
            atom_params: ConstantsAtomParams,
    ) -> Points:
        """ Read intercalated atoms coordinates from the Excel file or build them if there is no Excel file. """

        # Try to read the full channel coordinates
        file_name: str = Constants.file_names.FULL_CHANNEL_COORDINATES_XLSX_FILE
        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )
        inter_atoms_full_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(path_to_file)

        if inter_atoms_full_channel_coordinates_df is not None:
            logger.info(f"Read {file_name} file.")
            return cls.parse_inter_atoms_coordinates_df(inter_atoms_full_channel_coordinates_df)

        # Try to read the channelintercalated atoms plane coordinates
        file_name: str = Constants.file_names.CHANNEL_COORDINATES_XLSX_FILE
        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )
        inter_atoms_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(path_to_file)
        if inter_atoms_channel_coordinates_df is not None:
            logger.info(f"Read {file_name} file.")
            return cls.parse_inter_atoms_coordinates_df(inter_atoms_channel_coordinates_df)

        # logger.warning(f"Excel table withintercalated atoms for {structure_dir} structure not found.intercalated atoms builder.")

        file_name: str = Constants.file_names.PLANE_COORDINATES_XLSX_FILE
        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )
        inter_atoms_plane_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(path_to_file)
        if inter_atoms_plane_coordinates_df is not None:
            logger.info(f"Read {file_name} file.")
            inter_atoms_plane_coordinates: Points = cls.parse_inter_atoms_coordinates_df(
                inter_atoms_plane_coordinates_df)
        else:
            # Build atoms
            logger.info(f"Building inter_atoms for {structure_dir} structure...")
            inter_atoms_plane_coordinates: Points = cls.build_inter_atoms_plane_coordinates(
                carbon_channel,
                num_of_planes=number_of_planes,
                atom_params=atom_params,
                to_replace_nearby_atoms=to_replace_nearby_atoms,
                to_remove_too_close_atoms=to_remove_too_close_atoms,
            )

        try:
            inter_atoms_coordinates: Points = InterAtomsTranslator.translate_for_all_planes(
                carbon_channel, inter_atoms_plane_coordinates, number_of_planes, to_try_to_reflect_inter_atoms, atom_params)
        except Exception as e:
            logger.error(f"Error translating inter_atoms: {e}", exc_info=False)
            logger.warning(f"Structure for {structure_dir} is not translated. Using the original structure.")
            inter_atoms_coordinates: Points = inter_atoms_plane_coordinates

        return inter_atoms_coordinates

    @classmethod
    def get_inter_atoms_plane_coordinates(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            carbon_channel: CarbonHoneycombChannel,
            number_of_planes: int,
            atom_params: ConstantsAtomParams,
            to_replace_nearby_atoms: bool,
            to_remove_too_close_atoms: bool,
            file_name: str | None = None,
    ) -> Points:
        """ Read intercalated atoms coordinates from the file or build them if there is no Excel file. """

        if file_name and file_name != "None":
            path_to_file: Path = PathBuilder.build_path_to_result_data_file(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                file_name=file_name,
            )
            inter_atoms_plane_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(path_to_file)

            if inter_atoms_plane_coordinates_df is not None:
                return cls.parse_inter_atoms_coordinates_df(inter_atoms_plane_coordinates_df)

        logger.warning(
            f"Excel table with intercalated atoms for {structure_dir} structure not found. Intercalated atoms builder.")

        # Build atoms
        # carbon_channel: CarbonHoneycombChannel = cls.build_carbon_channel(structure_dir)
        coordinates_inter_atoms: Points = cls.build_inter_atoms_plane_coordinates(
            carbon_channel,
            num_of_planes=number_of_planes,
            atom_params=atom_params,
            to_replace_nearby_atoms=to_replace_nearby_atoms,
            to_remove_too_close_atoms=to_remove_too_close_atoms,
        )

        return coordinates_inter_atoms

    @staticmethod
    def build_carbon_channel(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str | None = None,
    ) -> CarbonHoneycombChannel:
        coordinates_carbon: Points = IntercalatedChannelBuilder.build_carbon_coordinates(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        carbon_channels: list[CarbonHoneycombChannel] = CarbonHoneycombActions.split_init_structure_into_separate_channels(
            coordinates_carbon=coordinates_carbon)
        return carbon_channels[0]

    @staticmethod
    def build_inter_atoms_plane_coordinates(
            carbon_channel: CarbonHoneycombChannel,
            num_of_planes: int,
            atom_params: ConstantsAtomParams,
            to_replace_nearby_atoms: bool,
            to_remove_too_close_atoms: bool,
    ) -> Points:
        """ Build intercalated atoms for one plane """
        coordinates_inter_atoms: Points = InterAtomsBuilder.build_inter_atoms_near_planes(
            carbon_channel, planes_limit=num_of_planes, atom_params=atom_params)

        if to_replace_nearby_atoms:
            coordinates_inter_atoms = InterAtomsFilter.replace_nearby_atoms_with_one_atom(
                coordinates_inter_atoms, atom_params)

        if to_remove_too_close_atoms:
            coordinates_inter_atoms = InterAtomsFilter.remove_too_close_atoms(coordinates_inter_atoms, atom_params)

        # Round coordinates to 3 decimal places
        coordinates_inter_atoms = Points(points=np.round(coordinates_inter_atoms.points, 3))

        return Points(points=coordinates_inter_atoms.sorted_points)

    @staticmethod
    def parse_inter_atoms_coordinates_df(inter_atoms_plane_coordinates_df: pd.DataFrame) -> Points:
        """
        Parse inter_atoms_plane_coordinates_df DataFrame with columns
        i, x_inter, y_inter, z_inter, min_dist_to_inter, Al_1, Al_2, Al_3 ...
        into Points with x_inter, y_inter, z_inter coordinates.

        The points with x_inter, y_inter, z_inter that equals NaN is ignored.
        """
        # Extract the x_inter, y_inter, z_inter columns
        required_columns: list[str] = ["x_inter", "y_inter", "z_inter"]
        if not all(col in inter_atoms_plane_coordinates_df.columns for col in required_columns):
            # Start of the temp block
            required_columns: list[str] = ["x_Al", "y_Al", "z_Al"]
            if not all(col in inter_atoms_plane_coordinates_df.columns for col in required_columns):
                raise ValueError(f"DataFrame must contain columns: {["x_inter", "y_inter", "z_inter"]}")
            # End of the temp block

            # raise ValueError(f"DataFrame must contain columns: {required_columns}")

        # Filter out rows where any of the required coordinates are NaN
        filtered_df: pd.DataFrame = inter_atoms_plane_coordinates_df.dropna(subset=required_columns)

        # Extract the coordinates as a numpy array
        points_array: np.ndarray = filtered_df[required_columns].to_numpy()

        # Round coordinates to 3 decimal places
        points_array = np.round(points_array, 3)

        # Return the Points instance
        return Points(points=points_array)
