from abc import abstractmethod
from .i_component_with_command import IComponentWithCommand


class IInputFieldCoordLimits(IComponentWithCommand):
    @abstractmethod
    def set_min_value(self, value: str | int | float) -> None:
        ...

    @abstractmethod
    def set_max_value(self, value: str | int | float) -> None:
        ...
