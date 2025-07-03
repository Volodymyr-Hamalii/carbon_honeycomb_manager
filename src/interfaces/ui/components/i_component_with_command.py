from typing import Callable
from abc import ABC, abstractmethod


class IComponentWithCommand(ABC):
    @abstractmethod
    def set_command(self, command: Callable) -> None:
        ...
