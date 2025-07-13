from pathlib import Path
import pandas as pd

from src.interfaces import IDataConverterPresenter, IDataConverterModel, IDataConverterView
from src.services import (
    Logger,
    FileReader,
    FileWriter,
    DataConverter,
    PathBuilder,
)

logger = Logger("DataConverterPresenter")


class DataConverterPresenter(IDataConverterPresenter):
    """Presenter for data converter functionality."""

    def __init__(self, model: IDataConverterModel, view: IDataConverterView) -> None:
        self.model: IDataConverterModel = model
        self.view: IDataConverterView = view
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the presenter."""
        self.view.set_available_formats(self.model.get_available_formats())
        self.view.set_conversion_callback(self._handle_conversion_request)

    def convert_file(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        file_name: str,
        target_format: str,
    ) -> Path:
        """Convert a file from one format to another."""
        try:
            self.view.show_conversion_progress("Starting conversion...")
            
            # Validate parameters
            if not self.validate_conversion_parameters(
                project_dir, subproject_dir, structure_dir, file_name, target_format
            ):
                raise ValueError("Invalid conversion parameters")

            path_to_init_file = PathBuilder.build_path_to_result_data_file(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
                file_name=file_name,
            )

            # Determine the source format
            source_format = path_to_init_file.suffix

            self.view.show_conversion_progress("Reading source file...")
            
            # Read the data based on the source format
            df = self._read_source_file(path_to_init_file, source_format)

            self.view.show_conversion_progress("Writing target file...")
            
            # Write the data based on the target format
            path_to_file_to_save = path_to_init_file.with_suffix(f".{target_format}")
            self._write_target_file(df, path_to_file_to_save, target_format)

            # Save conversion history
            conversion_info = {
                "source_file": str(path_to_init_file),
                "target_file": str(path_to_file_to_save),
                "source_format": source_format,
                "target_format": target_format,
                "timestamp": pd.Timestamp.now().isoformat(),
            }
            self.model.save_conversion_history(conversion_info)

            self.on_conversion_completed(path_to_file_to_save)
            return path_to_file_to_save

        except Exception as e:
            self.on_conversion_failed(e)
            raise

    def get_available_formats(self) -> list[str]:
        """Get available file formats for conversion."""
        return self.model.get_available_formats()

    def validate_conversion_parameters(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        file_name: str,
        target_format: str,
    ) -> bool:
        """Validate conversion parameters."""
        if not all([project_dir, subproject_dir, structure_dir, file_name]):
            return False
        
        if target_format not in self.model.get_available_formats():
            return False
        
        path_to_file = PathBuilder.build_path_to_result_data_file(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=file_name,
        )
        
        return path_to_file.exists()

    def on_conversion_completed(self, output_path: Path) -> None:
        """Handle conversion completion."""
        self.view.show_conversion_success(output_path)
        logger.info(f"Conversion completed successfully: {output_path}")

    def on_conversion_failed(self, error: Exception) -> None:
        """Handle conversion failure."""
        error_message = f"Conversion failed: {str(error)}"
        self.view.show_conversion_error(error_message)
        logger.error(error_message)

    def _handle_conversion_request(self) -> None:
        """Handle conversion request from view."""
        try:
            params = self.view.get_conversion_parameters()
            self.convert_file(
                project_dir=params["project_dir"],
                subproject_dir=params["subproject_dir"],
                structure_dir=params["structure_dir"],
                file_name=params["file_name"],
                target_format=params["target_format"],
            )
        except Exception as e:
            self.on_conversion_failed(e)

    def _read_source_file(self, path_to_file: Path, source_format: str) -> pd.DataFrame:
        """Read source file and return DataFrame."""
        if source_format == ".xlsx":
            df = FileReader.read_excel_file(path_to_file=path_to_file)
            if df is None:
                raise ValueError(f"Failed to read Excel file: {path_to_file}")

            # If more than 3 columns, find columns with "X", "Y", "Z"
            if len(df.columns) > 3:
                x_col = next((col for col in df.columns if "x" in col.lower()), None)
                y_col = next((col for col in df.columns if "y" in col.lower()), None)
                z_col = next((col for col in df.columns if "z" in col.lower()), None)
                if x_col and y_col and z_col:
                    df = df[[x_col, y_col, z_col]]
                else:
                    raise ValueError("Could not find X, Y, Z columns in Excel file.")

        elif source_format == ".dat":
            data = FileReader.read_dat_file(path_to_file=path_to_file)
            df = pd.DataFrame(data, columns=["X", "Y", "Z"])

        elif source_format == ".pdb":
            data = FileReader.read_pdb_file(path_to_file=path_to_file)
            df = pd.DataFrame(data, columns=["X", "Y", "Z"])

        else:
            raise ValueError(f"Unsupported source format: {source_format}")

        return df

    def _write_target_file(self, df: pd.DataFrame, path_to_file: Path, target_format: str) -> None:
        """Write DataFrame to target file."""
        if target_format == "xlsx":
            FileWriter.write_excel_file(
                df=df,
                path_to_file=path_to_file,
                sheet_name="Sheet1",
            )

        elif target_format == "dat":
            dat_lines = DataConverter.convert_df_to_dat(df)
            FileWriter.write_dat_file(
                data_lines=dat_lines,
                path_to_file=path_to_file,
            )

        elif target_format == "pdb":
            pdb_lines = DataConverter.convert_df_to_pdb(df)
            FileWriter.write_pdb_file(
                data_lines=pdb_lines,
                path_to_file=path_to_file,
            )

        else:
            raise ValueError(f"Unsupported target format: {target_format}")