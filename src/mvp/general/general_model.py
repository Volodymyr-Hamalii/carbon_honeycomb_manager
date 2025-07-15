from pathlib import Path
from dataclasses import asdict
from src.interfaces import IGeneralModel, PMvpParams
from src.entities import MvpParams
from src.services import Constants, Logger, FileReader, FileWriter


logger: Logger = Logger("GeneralModel")


class GeneralModel(IGeneralModel):
    """General model with default logic."""
    mvp_name: str
    
    def __init__(self) -> None:
        """Initialize the general model."""
        # Ensure MVP params directory exists
        Constants.path.MVP_PARAMS_DATA_PATH.mkdir(parents=True, exist_ok=True)

    def get_mvp_params(self) -> PMvpParams:
        """Get MVP parameters for this instance."""
        return self._get_mvp_params_impl()
    
    @classmethod 
    def get_mvp_params_cls(cls) -> PMvpParams:
        """Get MVP parameters for this class."""
        return cls._get_mvp_params_impl()
    
    @classmethod
    def _get_mvp_params_impl(cls) -> PMvpParams:
        file_name: str = cls._get_mvp_params_file_name()
        path_to_mvp_params: Path = Constants.path.MVP_PARAMS_DATA_PATH / file_name

        if path_to_mvp_params.exists():
            try:
                mvp_params_dict: dict | None = FileReader.read_json_file(
                    folder_path=Constants.path.MVP_PARAMS_DATA_PATH,
                    file_name=file_name,
                )

                if mvp_params_dict:
                    return cls._parse_mvp_params(mvp_params_dict)
            except Exception as e:
                logger.warning(f"Failed to read {file_name}: {e}. Creating new default params.")
                # Delete corrupted file and recreate with defaults
                path_to_mvp_params.unlink(missing_ok=True)

        try:
            mvp_params_dict: dict | None = FileReader.read_json_file(
                folder_path=Constants.path.MVP_PARAMS_DATA_PATH,
                file_name=Constants.file_names.DEFAULT_MVP_PARAMS_JSON_FILE,
            )

            if mvp_params_dict:
                return cls._parse_mvp_params(mvp_params_dict)
        except Exception as e:
            logger.warning(f"Failed to read default params: {e}. Creating new defaults.")

        return cls._get_default_mvp_params()

    def set_mvp_params(
            self,
            params: PMvpParams,
            mvp_params_file_name: str | None = None,
    ) -> None:
        """Set MVP parameters for this instance."""
        self._set_mvp_params_impl(params, mvp_params_file_name)
    
    @classmethod
    def set_mvp_params_cls(
            cls,
            params: PMvpParams,
            mvp_params_file_name: str | None = None,
    ) -> None:
        """Set MVP parameters for this class."""
        cls._set_mvp_params_impl(params, mvp_params_file_name)
    
    @classmethod
    def _set_mvp_params_impl(
            cls,
            params: PMvpParams,
            mvp_params_file_name: str | None = None,
    ) -> None:
        if mvp_params_file_name is None:
            mvp_params_file_name = cls._get_mvp_params_file_name()

        mvp_params_dict: dict = asdict(params)  # type: ignore
        
        # Convert Path objects to strings for JSON serialization
        cls._convert_paths_to_strings(mvp_params_dict)
        
        FileWriter.write_json_file(
            data=mvp_params_dict,
            path_to_file=Constants.path.MVP_PARAMS_DATA_PATH / mvp_params_file_name,
        )

    @classmethod
    def _get_mvp_params_file_name(cls) -> str:
        return f"{cls.mvp_name}.json"

    @classmethod
    def _convert_paths_to_strings(cls, data: dict) -> None:
        """Convert Path objects to strings and handle infinity values for JSON serialization."""
        import math
        
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)
            elif isinstance(value, float):
                # Handle infinity values
                if math.isinf(value):
                    if value > 0:
                        data[key] = "Infinity"
                    else:
                        data[key] = "-Infinity"
                elif math.isnan(value):
                    data[key] = None
            elif isinstance(value, dict):
                cls._convert_paths_to_strings(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, Path):
                        value[i] = str(item)
                    elif isinstance(item, float):
                        if math.isinf(item):
                            if item > 0:
                                value[i] = "Infinity"
                            else:
                                value[i] = "-Infinity"
                        elif math.isnan(item):
                            value[i] = None
                    elif isinstance(item, dict):
                        cls._convert_paths_to_strings(item)

    @classmethod
    def _convert_infinity_strings_to_floats(cls, data: dict) -> None:
        """Convert infinity string values back to float objects."""
        for key, value in data.items():
            if isinstance(value, str):
                if value == "Infinity":
                    data[key] = float("inf")
                elif value == "-Infinity":
                    data[key] = float("-inf")
            elif isinstance(value, dict):
                cls._convert_infinity_strings_to_floats(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        if item == "Infinity":
                            value[i] = float("inf")
                        elif item == "-Infinity":
                            value[i] = float("-inf")
                    elif isinstance(item, dict):
                        cls._convert_infinity_strings_to_floats(item)

    @classmethod
    def _parse_mvp_params(cls, mvp_params_dict: dict) -> PMvpParams:
        """
        Parse dictionary to MvpParams object.
        If parsing fails, return default params.
        """
        try:
            # Create a copy to avoid modifying the original dict
            params_dict: dict = mvp_params_dict.copy()
            
            # Remove coordinate_limits from dict if present (we use individual fields now)
            params_dict.pop("coordinate_limits", None)

            # Handle data_dir Path conversion
            if "data_dir" in params_dict and params_dict["data_dir"]:
                try:
                    params_dict["data_dir"] = Path(params_dict["data_dir"])
                except (TypeError, ValueError):
                    params_dict["data_dir"] = Path()

            # Handle infinity string values back to float
            cls._convert_infinity_strings_to_floats(params_dict)

            # Ensure required fields have safe defaults
            safe_defaults: dict = {
                "current_selection": {},
                "application_settings": {},
                "session_history": [],
                "data_dir": Path(),
                "file_name": None,
                "file_format": None,
                "excel_file_name": None,
                "dat_file_name": None,
                "pdb_file_name": None,
                "available_formats": ["xlsx", "dat", "pdb"],
            }
            
            # Apply safe defaults for missing fields
            for key, default_value in safe_defaults.items():
                if key not in params_dict:
                    params_dict[key] = default_value

            return MvpParams(**params_dict)

        except Exception as e:
            # Return default params if parsing fails
            logger.error(f"Failed to parse MVP parameters for {cls.mvp_name}: {e}")
            return MvpParams()

    @classmethod
    def _get_default_mvp_params(cls) -> PMvpParams:
        """ Create and set default values. """
        params = MvpParams()
        try:
            cls.set_mvp_params_cls(
                params,
                mvp_params_file_name=Constants.file_names.DEFAULT_MVP_PARAMS_JSON_FILE,
            )
        except Exception as e:
            logger.warning(f"Failed to save default MVP parameters: {e}")
        return params
