from abc import ABC, abstractmethod
from src.interfaces import PMvpParams


class IGeneralModel(ABC):
    """Interface for general model."""

    mvp_name: str

    @classmethod
    @abstractmethod
    def get_mvp_params(cls) -> PMvpParams:
        ...

    @classmethod
    @abstractmethod
    def set_mvp_params(
            cls,
            params: PMvpParams,
            mvp_params_file_name: str | None = None,
    ) -> None:
        ...

    @classmethod
    @abstractmethod
    def _get_mvp_params_file_name(cls) -> str:
        ...

    @classmethod
    @abstractmethod
    def _parse_mvp_params(cls, mvp_params_dict: dict) -> PMvpParams:
        ...

    @classmethod
    @abstractmethod
    def _get_default_mvp_params(cls) -> PMvpParams:
        ...
