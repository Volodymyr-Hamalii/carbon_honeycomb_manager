from abc import ABC, abstractmethod
from pathlib import Path


class IDataConverterPresenter(ABC):
    """Interface for data converter presenter."""

    @abstractmethod
    def convert_file(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        file_name: str,
        target_format: str,
    ) -> Path:
        """Convert file from one format to another."""
        ...

    @abstractmethod
    def get_available_formats(self) -> list[str]:
        """Get available file formats for conversion."""
        ...

    @abstractmethod
    def validate_conversion_parameters(
        self,
        project_dir: str,
        subproject_dir: str,
        structure_dir: str,
        file_name: str,
        target_format: str,
    ) -> bool:
        """Validate conversion parameters."""
        ...

    @abstractmethod
    def on_conversion_completed(self, output_path: Path) -> None:
        """Handle conversion completion."""
        ...

    @abstractmethod
    def on_conversion_failed(self, error: Exception) -> None:
        """Handle conversion failure."""
        ...