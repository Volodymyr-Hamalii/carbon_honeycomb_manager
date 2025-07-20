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

    @abstractmethod
    def show_success_message(self, message: str) -> None:
        ...

    @abstractmethod
    def show_warning_message(self, message: str) -> None:
        ...

    @abstractmethod
    def show_processing_message(self, message: str) -> None:
        ...
