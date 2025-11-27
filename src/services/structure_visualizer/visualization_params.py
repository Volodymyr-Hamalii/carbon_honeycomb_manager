from dataclasses import dataclass

from src.interfaces import (
    IVisualizationParams,
    IColors,
    IPlotAtomParams,
    IStructureVisualParams,
)
from src.ui.styles import Colors as UI_Colors


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
    as_shaded_3d_spheres: bool


@dataclass(frozen=True)
class PlotAtomParams(IPlotAtomParams):
    atoms_color: str
    bonds_color: str


class Colors(IColors):
    # TODO: move to the data/configs/colors.json
    carbon_colors: PlotAtomParams = PlotAtomParams(
        atoms_color=UI_Colors.BLUE200,
        bonds_color=UI_Colors.BLUE100,
    )
    intercalated_atoms_colors_1_layer: PlotAtomParams = PlotAtomParams(
        atoms_color=UI_Colors.RED300,
        bonds_color=UI_Colors.RED100,
    )
    intercalated_atoms_colors_2_layer: PlotAtomParams = PlotAtomParams(
        atoms_color=UI_Colors.GREEN300,
        bonds_color=UI_Colors.GREEN100,
    )
    intercalated_atoms_colors_3_layer: PlotAtomParams = PlotAtomParams(
        atoms_color=UI_Colors.BLUE400,
        bonds_color=UI_Colors.BLUE300,
    )


class VisualizationParams(IVisualizationParams):
    carbon = StructureVisualParams(
        color_atoms=Colors.carbon_colors.atoms_color,
        transparency=0.2,
        as_shaded_3d_spheres=False,
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
        as_shaded_3d_spheres=True,
        size=300,

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
        as_shaded_3d_spheres=True,
        size=300,

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
        as_shaded_3d_spheres=True,
        size=300,

        color_bonds=Colors.intercalated_atoms_colors_3_layer.bonds_color,
        transparency_bonds=1,
        bonds_width=1,

        to_set_equal_scale=False,
        to_show_coordinates=False,
        to_show_indexes=True,
    )
