from abc import ABC, abstractmethod
from src.interfaces import PMvpParams


class IGeneralModel(ABC):
    """Interface for general model."""

    mvp_name: str

    @abstractmethod
    @classmethod
    def get_mvp_params(cls) -> PMvpParams:
        ...

    @abstractmethod
    @classmethod
    def set_mvp_params(
            cls,
            params: PMvpParams,
            mvp_params_file_name: str | None = None,
    ) -> None:
        ...

    @abstractmethod
    @classmethod
    def _get_mvp_params_file_name(cls) -> str:
        ...

    @abstractmethod
    @classmethod
    def _parse_mvp_params(cls, mvp_params_dict: dict) -> PMvpParams:
        ...

    @abstractmethod
    @classmethod
    def _get_default_mvp_params(cls) -> PMvpParams:
        ...
