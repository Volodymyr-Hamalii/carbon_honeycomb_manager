from abc import ABC, abstractmethod
from pathlib import Path

from src.interfaces.entities.figures.i_points import IPoints


class IInterAtomsFileManager(ABC):
    """Interface for reading and writing intercalated atom coordinate files."""

    @staticmethod
    @abstractmethod
    def read_inter_atoms(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
    ) -> IPoints:
        ...

    @classmethod
    @abstractmethod
    def write_inter_atoms(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_name: str,
            inter_atoms: IPoints,
            sheet_name: str | None = None,
    ) -> Path:
        ...

    @staticmethod
    @abstractmethod
    def list_result_files(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            file_format: str | None = "csv",
    ) -> list[str]:
        ...

    @classmethod
    @abstractmethod
    def build_final_file_name(
            cls,
            version: int,
            stacking: str,
            model_family: str | None = None,
            author: str = "Agent",
            num_of_channels: str = "one",
            file_format: str = "csv",
    ) -> str:
        ...

    @classmethod
    @abstractmethod
    def get_next_final_version(
            cls,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            stacking: str,
            model_family: str | None = None,
    ) -> int:
        ...
