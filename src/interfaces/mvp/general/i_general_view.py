from abc import ABC, abstractmethod


class IGeneralView(ABC):
    """Interface for general view."""

    @abstractmethod
    def set_ui(self) -> None:
        ...

    @abstractmethod
    def show_status_message(self, message: str) -> None:
        ...

    @abstractmethod
    def show_error_message(self, message: str) -> None:
        ...
