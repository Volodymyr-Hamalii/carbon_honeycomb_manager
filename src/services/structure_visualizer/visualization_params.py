from dataclasses import dataclass

from src.interfaces import (
    IVisualizationParams,
    IColors,
    IPlotAtomParams,
    IStructureVisualParams,
)


@dataclass(frozen=True)
class StructureVisualParams(IStructureVisualParams):
    color_atoms: str
    color_bonds: str
    size: int
    bonds_width: float
    transparency: float
    transparency_bonds: float
    to_set_equal_scale: bool
    to_show_coordinates: bool
    to_show_indexes: bool


@dataclass(frozen=True)
class PlotAtomParams(IPlotAtomParams):
    atoms_color: str
    bonds_color: str


class Colors(IColors):
    # TODO: move to the data/configs/colors.json
    carbon_colors: PlotAtomParams = PlotAtomParams(
        atoms_color="#0500a4",
        bonds_color="#00065f",
    )
    intercalated_atoms_colors_1_layer: PlotAtomParams = PlotAtomParams(
        atoms_color="#e00000",
        bonds_color="#500000",
    )
    intercalated_atoms_colors_2_layer: PlotAtomParams = PlotAtomParams(
        atoms_color="#00d11d",
        bonds_color="#004309",
    )
    intercalated_atoms_colors_3_layer: PlotAtomParams = PlotAtomParams(
        atoms_color="#1b9afa",
        bonds_color="#0062ad",
    )


class VisualizationParams(IVisualizationParams):
    carbon = StructureVisualParams(
        color_atoms=Colors.carbon_colors.atoms_color,
        transparency=0.2,
        size=100,

        color_bonds=Colors.carbon_colors.bonds_color,
        transparency_bonds=1,
        bonds_width=0.5,

        to_set_equal_scale=True,
        to_show_coordinates=False,
        to_show_indexes=False,
    )

    intercalated_atoms_1_layer = StructureVisualParams(
        color_atoms=Colors.intercalated_atoms_colors_1_layer.atoms_color,
        transparency=0.5,
        size=400,

        color_bonds=Colors.intercalated_atoms_colors_1_layer.bonds_color,
        transparency_bonds=1,
        bonds_width=1,

        to_set_equal_scale=False,
        to_show_coordinates=False,
        to_show_indexes=True,
    )

    intercalated_atoms_2_layer = StructureVisualParams(
        color_atoms=Colors.intercalated_atoms_colors_2_layer.atoms_color,
        transparency=0.5,
        size=400,

        color_bonds=Colors.intercalated_atoms_colors_2_layer.bonds_color,
        transparency_bonds=1,
        bonds_width=1,

        to_set_equal_scale=False,
        to_show_coordinates=False,
        to_show_indexes=True,
    )

    intercalated_atoms_3_layer = StructureVisualParams(
        color_atoms=Colors.intercalated_atoms_colors_3_layer.atoms_color,
        transparency=0.5,
        size=400,

        color_bonds=Colors.intercalated_atoms_colors_3_layer.bonds_color,
        transparency_bonds=1,
        bonds_width=1,

        to_set_equal_scale=False,
        to_show_coordinates=False,
        to_show_indexes=True,
    )
