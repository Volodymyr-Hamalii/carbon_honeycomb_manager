from typing import Protocol

__all__: list[str] = [
    "IPlotAtomParams",
    "IColors",
    "IStructureVisualParams",
    "IVisualizationParams",
]


class IPlotAtomParams(Protocol):
    atoms_color: str
    bonds_color: str


class IColors(Protocol):
    carbon_colors: IPlotAtomParams
    intercalated_atoms_colors_1_layer: IPlotAtomParams
    intercalated_atoms_colors_2_layer: IPlotAtomParams
    intercalated_atoms_colors_3_layer: IPlotAtomParams


class IStructureVisualParams(Protocol):
    color_atoms: str
    color_bonds: str

    as_shaded_3d_spheres: bool

    size: int
    bonds_width: float

    transparency: float
    transparency_bonds: float

    to_set_equal_scale: bool
    to_show_coordinates: bool
    to_show_indexes: bool


class IVisualizationParams(Protocol):
    carbon: IStructureVisualParams
    intercalated_atoms_1_layer: IStructureVisualParams
    intercalated_atoms_2_layer: IStructureVisualParams
    intercalated_atoms_3_layer: IStructureVisualParams
