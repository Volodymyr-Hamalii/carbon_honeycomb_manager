from abc import ABC, abstractmethod


class IGeneralView(ABC):
    """Interface for general view."""

    @abstractmethod
    def set_ui(self) -> None:
        ...
