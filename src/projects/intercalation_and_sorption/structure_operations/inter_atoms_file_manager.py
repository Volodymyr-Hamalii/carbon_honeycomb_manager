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

    CSV is the default write format. Coordinate tables contain `atom_id`, `x_inter`, `y_inter`,
    `z_inter`, with coordinates rounded to 3 decimal places. Legacy XLSX and DAT reads remain.
    """

    DEFAULT_SHEET_NAME: str = "Intercalated atoms"

    SUPPORTED_COORDINATE_FORMATS: frozenset[str] = frozenset({"csv", "xlsx", "dat"})
    ALLOWED_STACKINGS: frozenset[str] = frozenset({"AA", "ABAB", "ABC", "ABCD"})

    # final_one_ch-v3-ABC-Volod.csv -> num_of_channels="one", version=3, stacking="ABC", author="Volod"
    FINAL_FILE_NAME_PATTERN: re.Pattern[str] = re.compile(
        r"^final_(?P<num_of_channels>one|all)_ch-v(?P<version>\d+)"
        r"(?:-(?P<stacking>AA|ABAB|ABC|ABCD))?"
        r"(?:-(?P<author>[A-Za-z0-9_-]+))?\.(?P<format>csv|xlsx)$"
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
            sheet_name: str | None = None,
    ) -> Path:
        """Write the intercalated atom coordinates to a result data file."""
        if len(inter_atoms.points) == 0:
            raise ValueError("Refusing to write an empty set of intercalated atoms.")

        path_to_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, subproject_dir, structure_dir, file_name=file_name
        )

        file_format: str = path_to_file.suffix.lower().lstrip(".") or "csv"
        if file_format not in cls.SUPPORTED_COORDINATE_FORMATS:
            raise ValueError(
                f"Unsupported coordinate format {file_format!r}; expected one of "
                f"{sorted(cls.SUPPORTED_COORDINATE_FORMATS)}."
            )

        atom_ids: tuple[str, ...] = inter_atoms.atom_ids or tuple(
            f"atom-{index + 1:04d}" for index in range(len(inter_atoms.points))
        )
        coordinates_df: pd.DataFrame = pd.DataFrame({
            InterAtomsParser.ATOM_ID_COLUMN: atom_ids,
            InterAtomsParser.INTER_ATOMS_COORDINATES_COLUMNS[0]: inter_atoms.points[:, 0],
            InterAtomsParser.INTER_ATOMS_COORDINATES_COLUMNS[1]: inter_atoms.points[:, 1],
            InterAtomsParser.INTER_ATOMS_COORDINATES_COLUMNS[2]: inter_atoms.points[:, 2],
        })

        path_to_file_result: Path | None
        if file_format == "csv":
            path_to_file_result = FileWriter.write_csv_file(coordinates_df, path_to_file)
        elif file_format == "xlsx":
            path_to_file_result = FileWriter.write_excel_file(
                df=coordinates_df,
                path_to_file=path_to_file,
                sheet_name=sheet_name or cls.DEFAULT_SHEET_NAME,
            )
        else:
            path_to_file_result = FileWriter.write_dat_file(
                data_lines=inter_atoms.points,
                path_to_file=path_to_file,
            )

        if path_to_file_result is None:
            raise IOError(f"Failed to write {file_name} file.")

        return path_to_file_result

    @staticmethod
    def list_result_files(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_format: str | None = "csv",
    ) -> list[str]:
        """List the files available in the result data folder of the structure."""
        path_to_dir: Path = PathBuilder.build_path_to_result_data_dir(
            project_dir, subproject_dir, structure_dir
        )
        return FileReader.read_list_of_files(folder_path=path_to_dir, format=file_format)

    @classmethod
    def build_final_file_name(
            cls,
            version: int,
            stacking: str | None = None,
            author: str = "Agent",
            num_of_channels: str = "one",
            file_format: str = "csv",
    ) -> str:
        """
        Build `final_{one|all}_ch-v{version}[-{stacking}][-{author}].{format}`.

        The `stacking` suffix is skipped for narrow structures where the stacking is not defined.
        """
        if num_of_channels not in ("one", "all"):
            raise ValueError(f"num_of_channels must be 'one' or 'all', got {num_of_channels!r}.")

        if version < 1:
            raise ValueError(f"version must be a positive integer, got {version}.")

        if stacking is not None and stacking not in cls.ALLOWED_STACKINGS:
            raise ValueError(f"Unsupported stacking {stacking!r}.")

        if author and re.fullmatch(r"[A-Za-z0-9_-]+", author) is None:
            raise ValueError("author may contain only letters, digits, underscores and hyphens.")

        normalized_format: str = file_format.lower().lstrip(".")
        if normalized_format not in {"csv", "xlsx"}:
            raise ValueError("Final structures support only csv and legacy xlsx formats.")

        name: str = f"final_{num_of_channels}_ch-v{version}"

        if stacking:
            name += f"-{stacking}"

        if author:
            name += f"-{author}"

        return f"{name}.{normalized_format}"

    @classmethod
    def get_next_final_version(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> int:
        """Return the next free `v{i}` number for the `final_one_ch-*` files of the structure."""
        file_names: list[str] = cls.list_result_files(
            project_dir, subproject_dir, structure_dir, file_format=None
        )

        versions: list[int] = []
        for file_name in file_names:
            match: re.Match[str] | None = cls.FINAL_FILE_NAME_PATTERN.match(file_name)
            if match is not None:
                versions.append(int(match.group("version")))

        return max(versions) + 1 if versions else 1
