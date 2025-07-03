from abc import abstractmethod
from .i_component_with_command import IComponentWithCommand


class IDropdownList(IComponentWithCommand):
    @abstractmethod
    def set_options(
            self,
            options: list[str],
            default_value: str | None = None,
    ) -> None:
        ...
