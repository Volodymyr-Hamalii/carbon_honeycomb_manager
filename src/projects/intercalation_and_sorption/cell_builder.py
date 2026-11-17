"""Warnings and file output of a cut elementary cell, shared by the GUI presenter and the MCP server."""

from dataclasses import dataclass
from pathlib import Path

from src.projects.intercalation_and_sorption.cell_building import CellFolderNamer, CellParamsBuilder
from src.projects.intercalation_and_sorption.intercalared_structure_cell_cutter import CellCutResult
from src.services import FileWriter, Logger, PathBuilder


logger = Logger("CellBuilder")


@dataclass(frozen=True)
class CellFiles:
    """Files written for one cut cell."""

    cell_dir: Path
    carbon_path: Path
    intercalated_path: Path
    params_path: Path


class CellBuilder:
    """Describe the problems of a cut cell and write it to a new `cell_{type}_v{i}` folder."""

    PARAMS_FILE_NAME: str = "cell_params.txt"

    @classmethod
    def collect_warnings(cls, file_name: str, result: CellCutResult) -> list[str]:
        """Warnings the user has to see: an incomplete one_ch cell and an unconfirmed z repeat."""
        warnings: list[str] = []

        if "one_ch" in file_name.lower():
            warnings.append("The cell cut from a one_ch file will be incomplete, use an all_ch file.")

        if not result.z_cell.verified:
            warnings.append(
                "The z repeat is not confirmed by an overlap: the cell height is taken from the file height "
                f"({result.z_cell.num_of_periods} carbon periods, c={result.cell_params.c:.3f})."
            )

        return warnings

    @classmethod
    def write_cell(
            cls,
            project_dir: str,
            element: str,
            structure: str,
            file_name: str,
            result: CellCutResult,
    ) -> CellFiles:
        """
        Write the cell atoms and `cell_params.txt` into a new folder next to the result data.

        The folder is `cell_{type}_v{i}` (`_{j}` is appended when it already exists); existing folders
        and files are never overwritten.
        """
        cell_dir: Path = CellFolderNamer.create_unique_dir(
            PathBuilder.build_path_to_result_data_dir(project_dir, element, structure),
            file_name,
        )

        carbon_path: Path = cell_dir / f"{structure}_cell_carbon.dat"
        intercalated_path: Path = cell_dir / f"{structure}_cell_{element}_intercalated.dat"
        params_path: Path = cell_dir / cls.PARAMS_FILE_NAME

        FileWriter.write_dat_file(data_lines=result.carbon.points, path_to_file=carbon_path)
        FileWriter.write_dat_file(data_lines=result.intercalated.points, path_to_file=intercalated_path)
        params_path.write_text(CellParamsBuilder.format_params(result.cell_params), encoding="utf-8")

        logger.info(f"Saved carbon cell to: {carbon_path}")
        logger.info(f"Saved intercalated cell to: {intercalated_path}")
        logger.info(f"Saved cell parameters to: {params_path}")

        return CellFiles(
            cell_dir=cell_dir,
            carbon_path=carbon_path,
            intercalated_path=intercalated_path,
            params_path=params_path,
        )
