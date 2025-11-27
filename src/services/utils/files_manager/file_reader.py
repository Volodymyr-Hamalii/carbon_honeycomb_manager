import json
from typing import Any
from pathlib import Path

import pandas as pd
from pandas.core.indexes.base import Index
import numpy as np
import MDAnalysis as mda

from ..logger import Logger
from .path_builder import PathBuilder


logger = Logger("FileReader")


class FileReader:
    @staticmethod
    def read_list_of_dirs(
            folder_path: Path | str,
    ) -> list[str]:
        """ Read a list of directories in the given folder path. By default uses 'project_data' folder. """
        try:
            return sorted(
                [
                    dir.name for dir in Path(folder_path).iterdir()
                    if dir.is_dir()
                ]
            )
        except FileNotFoundError:
            logger.error(f"Folder {folder_path} not found.")
            return []
        except Exception as e:
            logger.error(f"Failed to read list of directories in {folder_path}: {e}")
            return []

    @classmethod
    def read_list_of_files(
            cls,
            folder_path: Path | str,
            format: str | None = None,
            to_include_nested_files: bool = False,
            to_append_parent_dir: bool = False,
    ) -> list[str]:
        """
        Read a list of files in the given folder path. By default uses '.xlsx' format.
        If to_include_nested_files is True, it will include files from nested folders.
        """
        try:
            file_names: list[str] = []

            for file in Path(folder_path).iterdir():
                if file.is_file() and (
                    file.name.endswith(format) if format else True
                ):
                    if to_append_parent_dir:
                        file_names.append(file.parent.name + "/" + file.name)
                    else:
                        file_names.append(file.name)

                if to_include_nested_files and file.is_dir():
                    file_names.extend(
                        cls.read_list_of_files(
                            file,
                            format=format,
                            to_include_nested_files=to_include_nested_files,
                            to_append_parent_dir=True,
                        )
                    )

            return sorted(file_names)

        except FileNotFoundError:
            logger.error(f"Folder {folder_path} not found.")
            return []
        except Exception as e:
            logger.error(f"Failed to read list of files in {folder_path}: {e}")
            return []

    @staticmethod
    def read_json_file(
            folder_path: Path | str,
            file_name: str,
    ) -> Any:
        """
        Read JSON file (by default 'structure_settings.json').
        If folder_path=None -- uses path to 'result_data' folder.
        """

        path_to_file: Path = Path(folder_path) / file_name

        if not path_to_file.exists():
            # logger.warning(f"File {path_to_file} not exists.")
            return None

        data_json: str = Path(path_to_file).read_text(encoding="utf-8")
        return json.loads(data_json)

    @classmethod
    def read_dat_file(
            cls,
            path_to_file: Path,
    ) -> np.ndarray:
        atom_data: list[list[float]] = []

        with Path(path_to_file).open("r") as dat_file:
            # Skip the first and second lines
            dat_file.readline()
            dat_file.readline()

            for line in dat_file:
                if line.strip():  # Skip empty liness
                    coords: list[str] = line.split()
                    if len(coords) == 3:
                        atom_data.append([float(coord) for coord in coords])

        return np.array(atom_data)

    @staticmethod
    def read_pdb_file(
            path_to_file: Path,
    ) -> np.ndarray:
        """
        Read a PDB file and return its atomic coordinates as a NumPy array.

        Parameters:
        - structure_dir: str, the name of the structure folder.
        - folder_path: Path | str | None, the base folder path. If None, uses default from PathBuilder.
        - file_name: str, the PDB file name to read.
        - is_init_data_dir: bool | None: to build path to the specific dir. If it's False - builds path to result data.

        Returns:
        - np.ndarray: A NumPy array containing the atomic coordinates from the PDB file.
        """

        try:
            # Load a structure from a file
            u = mda.Universe(path_to_file)

            # Access atoms and coordinates
            atoms = u.atoms
            points: np.ndarray = atoms.positions  # type: ignore

            return np.array(points)

        except FileNotFoundError:
            logger.error(f"PDB file not found at {path_to_file}")
            return np.array([])

        except Exception as e:
            logger.error(f"Failed to read PDB file {path_to_file}: {e}")
            return np.array([])

    @classmethod
    def read_excel_file(
            cls,
            path_to_file: Path,
            sheet_name: str | int = 0,
            to_print_warning: bool = True,
    ) -> pd.DataFrame | None:
        """
        Read an Excel file.

        Parameters:
        - structure_dir: str, the name of the structure folder.
        - folder_path: Path | str | None, the base folder path. If None, uses default from PathBuilder.
        - file_name: str, the Excel file name to read.
        - sheet_name: str | int, the sheet name or index to read (default is the first sheet).
        - is_init_data_dir: bool | None: to build path to the specific dir. If it's False - builds path to result data.

        Returns:
        - pd.DataFrame: A pandas DataFrame containing the data from the specified Excel file and sheet.
        """

        # Check if the file exists
        if not path_to_file.exists():
            if to_print_warning:
                logger.warning(f"File not found at {path_to_file}")
            return None

        try:
            # Read the Excel file into a pandas DataFrame
            df: pd.DataFrame = pd.read_excel(
                path_to_file, sheet_name=sheet_name, engine='openpyxl'
            )
            return df

        except FileNotFoundError:
            if to_print_warning:
                logger.warning(f"File {path_to_file} not exists.")

        except Exception as e:
            logger.error(f"Failed to read file {path_to_file}: {e}")

    @classmethod
    def read_init_data_file(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
    ) -> np.ndarray:
        path_to_file: Path = PathBuilder.build_path_to_init_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        file_format: str = file_name.split(".")[-1].lower()

        if file_format == "pdb":
            return cls.read_pdb_file(path_to_file)
        elif file_format == "dat":
            return cls.read_dat_file(path_to_file)
        elif file_format == "xlsx":
            carbon_points_df: pd.DataFrame | None = cls.read_excel_file(path_to_file)
            if carbon_points_df is None:
                raise IOError(f"Failed to read file: {file_name}")
            return carbon_points_df.to_numpy()
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @classmethod
    def read_result_data_file(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
            to_print_warning: bool = True,
    ) -> pd.DataFrame | None:
        """
        Read result data file (supports .xlsx and .dat formats).
        Returns pandas DataFrame or None if file doesn't exist or fails to read.
        """
        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        if not path_to_file.exists():
            if to_print_warning:
                logger.warning(f"File not found at {path_to_file}")
            return None

        file_format: str = file_name.split(".")[-1].lower()

        if file_format == "xlsx":
            return cls.read_excel_file(path_to_file, to_print_warning=to_print_warning)
        elif file_format == "dat":
            try:
                coords: np.ndarray = cls.read_dat_file(path_to_file)
                # Convert to DataFrame with standard column names
                return pd.DataFrame(coords, columns=Index(["x_inter", "y_inter", "z_inter"]))
            except Exception as e:
                if to_print_warning:
                    logger.error(f"Failed to read .dat file {path_to_file}: {e}")
                return None
        else:
            if to_print_warning:
                logger.error(f"Unsupported file format: {file_format}")
            return None
