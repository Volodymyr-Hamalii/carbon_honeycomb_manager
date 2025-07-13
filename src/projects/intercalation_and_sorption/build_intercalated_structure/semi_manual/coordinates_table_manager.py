from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

from src.interfaces import IPoints, ICarbonHoneycombChannel
from src.services.utils import (
    Constants,
    ConstantsAtomParams,
    Logger,
    FileReader,
    FileWriter,
    PathBuilder,
)
from src.entities import Points
from .inter_atoms_parser import InterAtomsParser


logger = Logger("CoordinatesTableManager")


class CoordinatesTableManager:
    @classmethod
    def update_plane_tbl_file(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
            carbon_channel: ICarbonHoneycombChannel,
            number_of_planes: int,
            atom_params: ConstantsAtomParams,
            to_replace_nearby_atoms: bool,
            to_remove_too_close_atoms: bool,
    ) -> Path:
        inter_atoms_plane: IPoints = InterAtomsParser.get_inter_atoms_plane_coordinates(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            carbon_channel=carbon_channel,
            number_of_planes=number_of_planes,
            atom_params=atom_params,
            file_name=file_name,
            to_replace_nearby_atoms=to_replace_nearby_atoms,
            to_remove_too_close_atoms=to_remove_too_close_atoms,
        )
        df: pd.DataFrame = cls._build_updated_df(inter_atoms_plane)

        path_to_file = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        path_to_file: Path | None = FileWriter.write_excel_file(
            df=df,
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms for the plane",
        )

        if path_to_file is None:
            raise IOError(f"Failed to write {file_name} file.")

        return path_to_file

    @classmethod
    def update_full_channel_tbl_file(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> Path:
        file_name: str = Constants.file_names.FULL_CHANNEL_COORDINATES_XLSX_FILE
        path_to_file = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        inter_channel_coordinates_df: pd.DataFrame | None = FileReader.read_excel_file(path_to_file)

        if inter_channel_coordinates_df is None:
            raise FileNotFoundError(
                f"Excel file withintercalated atoms for the full channel not found in {structure_dir}.")

        inter_channel_coordinates: Points = InterAtomsParser.parse_inter_atoms_coordinates_df(
            inter_channel_coordinates_df)
        df: pd.DataFrame = cls._build_updated_df(inter_channel_coordinates)

        path_to_file: Path | None = FileWriter.write_excel_file(
            df=df,
            path_to_file=path_to_file,
            sheet_name="Intercalated atoms for the full channel",
        )

        if path_to_file is None:
            raise IOError(f"Failed to write {file_name} file.")

        return path_to_file

    @staticmethod
    def _build_updated_df(inter_atoms: IPoints) -> pd.DataFrame:
        """
        Build pd.DataFrame based on the points with the colums
        i, x_inter, y_inter, z_inter, min_dist_to_inter, inter_1, inter_2, inter_3 ...

        where
        i - index of the point in the inter_atoms.points,
        x_inter, y_inter, z_inter - coordinates of the point,
        inter_1, inter_2, inter_3, ... - distance from the point to other points.
        """

        # Extract the array of points
        points: np.ndarray = inter_atoms.points

        # Validate the shape of the points
        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("Points must be a 2D array with shape (N, 3).")

        # Compute the distance matrix
        dists: np.ndarray = cdist(points, points)

        # Compute the minimum distance to each point (ignoring the self-distance)
        min_dist_to_inter: np.ndarray = np.min(dists + np.diag([np.inf] * len(points)), axis=1)

        # Prepare data for the DataFrame
        data: dict = {
            "i": np.arange(len(points)),  # Point index
            "x_inter": points[:, 0],      # X-coordinates
            "y_inter": points[:, 1],      # Y-coordinates
            "z_inter": points[:, 2],      # Z-coordinates
            "min_dist_to_inter": min_dist_to_inter,  # Minimum distance to other points
        }

        # Add columns for distances to other points
        for j in range(dists.shape[1]):
            data[f"Al_{j}"] = dists[:, j]

        # Build the DataFrame
        df = pd.DataFrame(data)

        return df
