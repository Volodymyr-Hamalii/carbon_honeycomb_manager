"""Reading and writing intercalated atom coordinate files."""

import re
from pathlib import Path

import pandas as pd

from src.interfaces import IInterAtomsFileManager, IPoints
from src.services import FileReader, FileWriter, Logger, PathBuilder

from ..build_intercalated_structure import InterAtomsParser


logger = Logger("InterAtomsFileManager")


class InterAtomsFileManager(IInterAtomsFileManager):
    """
    Reading and writing the intercalated atom coordinate files of a structure.

    The written files follow the format of the existing `final_*` files: a single sheet with the
    `i`, `x_inter`, `y_inter`, `z_inter` columns and the coordinates rounded to 3 decimal places.
    """

    DEFAULT_SHEET_NAME: str = "Intercalated atoms"

    # final_one_ch-v3-ABC-Volod.xlsx -> num_of_channels="one", version=3, stacking="ABC", author="Volod"
    FINAL_FILE_NAME_PATTERN: re.Pattern[str] = re.compile(
        r"^final_(?P<num_of_channels>one|all)_ch-v(?P<version>\d+)"
        r"(?:-(?P<stacking>AA|ABAB|ABC|ABCD))?"
        r"(?:-(?P<author>[^.]+))?\.xlsx$"
    )

    @staticmethod
    def read_inter_atoms(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
    ) -> IPoints:
        """Read the intercalated atom coordinates from a result data file."""
        inter_atoms_df: pd.DataFrame | None = FileReader.read_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
            to_print_warning=False,
        )

        if inter_atoms_df is None:
            path_to_file: Path = PathBuilder.build_path_to_result_data_file(
                project_dir, subproject_dir, structure_dir, file_name=file_name
            )
            raise IOError(f"Failed to read intercalated atoms file: {path_to_file}")

        return InterAtomsParser.parse_inter_atoms_coordinates_df(inter_atoms_df)

    @classmethod
    def write_inter_atoms(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
            inter_atoms: IPoints,
            sheet_name: str = DEFAULT_SHEET_NAME,
    ) -> Path:
        """Write the intercalated atom coordinates to a result data file."""
        if len(inter_atoms.points) == 0:
            raise ValueError("Refusing to write an empty set of intercalated atoms.")

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=file_name
        )

        path_to_file_result: Path | None = FileWriter.write_excel_file(
            df=inter_atoms.to_df(columns=["i", *InterAtomsParser.INTER_ATOMS_COORDINATES_COLUMNS]),
            path_to_file=path_to_file,
            sheet_name=sheet_name,
        )

        if path_to_file_result is None:
            raise IOError(f"Failed to write {file_name} file.")

        return path_to_file_result

    @staticmethod
    def list_result_files(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_format: str | None = "xlsx",
    ) -> list[str]:
        """List the files available in the result data folder of the structure."""
        path_to_dir: Path = PathBuilder.build_path_to_result_data_dir(
            project_dir, subproject_dir, structure_dir
        )
        return FileReader.read_list_of_files(folder_path=path_to_dir, format=file_format)

    @staticmethod
    def build_final_file_name(
            version: int,
            stacking: str | None = None,
            author: str = "Claude",
            num_of_channels: str = "one",
    ) -> str:
        """
        Build a final structure file name: `final_{one|all}_ch-v{version}[-{stacking}][-{author}].xlsx`.

        The `stacking` suffix is skipped for narrow structures where the stacking is not defined.
        """
        if num_of_channels not in ("one", "all"):
            raise ValueError(f"num_of_channels must be 'one' or 'all', got {num_of_channels!r}.")

        if version < 1:
            raise ValueError(f"version must be a positive integer, got {version}.")

        name: str = f"final_{num_of_channels}_ch-v{version}"

        if stacking:
            name += f"-{stacking}"

        if author:
            name += f"-{author}"

        return f"{name}.xlsx"

    @classmethod
    def get_next_final_version(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> int:
        """Return the next free `v{i}` number for the `final_one_ch-*` files of the structure."""
        file_names: list[str] = cls.list_result_files(
            project_dir, subproject_dir, structure_dir, file_format="xlsx"
        )

        versions: list[int] = []
        for file_name in file_names:
            match: re.Match[str] | None = cls.FINAL_FILE_NAME_PATTERN.match(file_name)
            if match is not None:
                versions.append(int(match.group("version")))

        return max(versions) + 1 if versions else 1
