from pathlib import Path
from ..constants import Constants


class PathBuilder:

    ### INIT DATA ###

    @staticmethod
    def build_path_to_init_data_dir(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            init_data_dir: str = Constants.file_names.INIT_DATA_DIR,
    ) -> Path:
        return Constants.path.PROJECT_DATA_PATH / project_dir / subproject_dir / init_data_dir / structure_dir

    @classmethod
    def build_path_to_init_data_file(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
            init_data_dir: str = Constants.file_names.INIT_DATA_DIR,
    ) -> Path:
        path_to_init_data_dir: Path = cls.build_path_to_init_data_dir(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            init_data_dir=init_data_dir,
        )
        return path_to_init_data_dir / file_name

    ### RESULT DATA ###

    @staticmethod
    def build_path_to_result_data_dir(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            result_dir: str = Constants.file_names.RESULT_DATA_DIR,
    ) -> Path:

        return Constants.path.PROJECT_DATA_PATH / project_dir / subproject_dir / result_dir / structure_dir

    @classmethod
    def build_path_to_result_data_file(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
            result_dir: str = Constants.file_names.RESULT_DATA_DIR,
    ) -> Path:

        path_to_result_dir: Path = cls.build_path_to_result_data_dir(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            result_dir=result_dir,
        )

        return path_to_result_dir / file_name
