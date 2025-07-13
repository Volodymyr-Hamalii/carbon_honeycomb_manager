from pathlib import Path
import numpy as np
import pandas as pd

from src.utils import (
    Constants,
    Logger,
    Inputs,
    FileReader,
    FileWriter,
    DataConverter,
    PathBuilder,
)
from .view_model_params_setter import VMParamsSetter

logger = Logger("Actions")


class VMDataConverter(VMParamsSetter):
    def convert_file(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
            target_format: str,
    ) -> Path:
        """
        Convert a file from one format to another. Return the path to the converted file.
        """
        path_to_init_file: Path = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )

        # Determine the source format
        source_format: str = path_to_init_file.suffix

        # Read the data based on the source format
        if source_format == ".xlsx":
            df: pd.DataFrame | None = FileReader.read_excel_file(
                path_to_file=path_to_init_file,
            )
            if df is None:
                raise ValueError(f"Failed to read Excel file: {path_to_init_file}")

            # If more than 3 columns, find columns with "X", "Y", "Z"
            if len(df.columns) > 3:
                x_col: str | None = next((col for col in df.columns if "x" in col.lower()), None)
                y_col: str | None = next((col for col in df.columns if "y" in col.lower()), None)
                z_col: str | None = next((col for col in df.columns if "z" in col.lower()), None)
                if x_col and y_col and z_col:
                    df = df[[x_col, y_col, z_col]]
                else:
                    raise ValueError("Could not find X, Y, Z columns in Excel file.")

        elif source_format == ".dat":
            data: np.ndarray = FileReader.read_dat_file(
                path_to_file=path_to_init_file,
            )
            df = pd.DataFrame(data, columns=["X", "Y", "Z"])

        elif source_format == ".pdb":
            # Assuming a method to read PDB files into a DataFrame
            data: np.ndarray = FileReader.read_pdb_file(
                path_to_file=path_to_init_file,
            )
            df = pd.DataFrame(data, columns=["X", "Y", "Z"])

        else:
            raise ValueError(f"Unsupported source format: {source_format}")

        # Write the data based on the target format
        path_to_file_to_save: Path = path_to_init_file.with_suffix(f".{target_format}")

        if target_format == "xlsx":
            FileWriter.write_excel_file(
                df=df,
                path_to_file=path_to_file_to_save,
                sheet_name="Sheet1",
            )

        elif target_format == "dat":
            dat_lines: list[str] = DataConverter.convert_df_to_dat(df)
            FileWriter.write_dat_file(
                data_lines=dat_lines,
                path_to_file=path_to_file_to_save,
            )

        elif target_format == "pdb":
            pdb_lines: list[str] = DataConverter.convert_df_to_pdb(df)
            FileWriter.write_pdb_file(
                data_lines=pdb_lines,
                path_to_file=path_to_file_to_save,
            )

        else:
            raise ValueError(f"Unsupported target format: {target_format}")

        return path_to_file_to_save
