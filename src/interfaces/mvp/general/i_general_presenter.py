from abc import ABC, abstractmethod
from typing import Any


class IGeneralPresenter(ABC):
    """Interface for general presenter."""

    def handle_error(self, operation: str, error: Exception) -> None:
        ...

    def handle_success(self, operation: str, message: str | None = None) -> None:
        ...

    def get_parameters(self) -> Any:
        ...

    def set_parameters(self, params: Any) -> None:
        ...

    def update_parameter(self, parameter_name: str, value: Any) -> None:
        ...
