from typing import Protocol

__all__: list[str] = [
    "IVisualizationParams",
    "IColors",
]


class IVisualizationParams(Protocol):
    color_atoms: str
    color_bonds: str
    size: int
    bonds_width: float
    transparency: float
    transparency_bonds: float
    label: str
    to_set_equal_scale: bool
    to_show_coordinates: bool
    to_show_indexes: bool


class IColors(Protocol):
    carbon_atoms: str
    carbon_bonds: str

    # TODO: refactor
    aluminum_1_atoms: str
    aluminum_1_bonds: str
    aluminum_2_atoms: str
    aluminum_2_bonds: str
    aluminum_3_atoms: str
    aluminum_3_bonds: str

    black: str
    gray100: str
    gray200: str
    gray300: str
    gray400: str
