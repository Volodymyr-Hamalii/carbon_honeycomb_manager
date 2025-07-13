from pathlib import Path
from dataclasses import asdict
from src.interfaces import IGeneralModel, PMvpParams
from src.entities import MvpParams, CoordinateLimits
from src.services import Constants, Logger, FileReader, FileWriter


logger: Logger = Logger("GeneralModel")


class GeneralModel(IGeneralModel):
    """ General model with default logic. """
    mvp_name: str

    @classmethod
    def get_mvp_params(cls) -> PMvpParams:
        file_name: str = cls._get_mvp_params_file_name()
        path_to_mvp_params: Path = Constants.path.MVP_PARAMS_DATA_PATH / file_name

        if path_to_mvp_params.exists():
            mvp_params_dict: dict | None = FileReader.read_json_file(
                folder_path=Constants.path.MVP_PARAMS_DATA_PATH,
                file_name=file_name,
            )

            if mvp_params_dict:
                return cls._parse_mvp_params(mvp_params_dict)

        mvp_params_dict: dict | None = FileReader.read_json_file(
            folder_path=Constants.path.MVP_PARAMS_DATA_PATH,
            file_name=Constants.file_names.DEFAULT_MVP_PARAMS_JSON_FILE,
        )

        if mvp_params_dict:
            return cls._parse_mvp_params(mvp_params_dict)

        return cls._get_default_mvp_params()

    @classmethod
    def set_mvp_params(
            cls,
            params: MvpParams,
            mvp_params_file_name: str | None = None,
    ) -> None:
        if mvp_params_file_name is None:
            mvp_params_file_name = cls._get_mvp_params_file_name()

        mvp_params_dict: dict = asdict(params)
        FileWriter.write_json_file(
            data=mvp_params_dict,
            path_to_file=Constants.path.MVP_PARAMS_DATA_PATH / mvp_params_file_name,
        )

    @classmethod
    def _get_mvp_params_file_name(cls) -> str:
        return f"{cls.mvp_name}.json"

    @classmethod
    def _parse_mvp_params(cls, mvp_params_dict: dict) -> PMvpParams:
        """
        Parse dictionary to MvpParams object.
        If parsing fails, return default params.
        """
        try:
            # Handle coordinate_limits nested object
            if "coordinate_limits" in mvp_params_dict:
                coord_limits_dict = mvp_params_dict["coordinate_limits"]
                mvp_params_dict["coordinate_limits"] = CoordinateLimits(**coord_limits_dict)

            # Handle data_dir Path conversion
            if "data_dir" in mvp_params_dict and mvp_params_dict["data_dir"]:
                mvp_params_dict["data_dir"] = Path(mvp_params_dict["data_dir"])

            return MvpParams(**mvp_params_dict)

        except Exception:
            # Return default params if parsing fails
            logger.error(f"Failed to parse MVP parameters for {cls.mvp_name}.")
            return MvpParams()

    @classmethod
    def _get_default_mvp_params(cls) -> PMvpParams:
        """ Create and set default values. """
        params = MvpParams()
        cls.set_mvp_params(
            params,
            mvp_params_file_name=Constants.file_names.DEFAULT_MVP_PARAMS_JSON_FILE,
        )
        return params
