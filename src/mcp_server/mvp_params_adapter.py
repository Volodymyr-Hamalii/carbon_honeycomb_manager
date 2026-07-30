"""Adapter between explicit MCP tool arguments and the GUI-oriented `MvpParams` dataclass."""

from src.interfaces import PMvpParams
from src.entities import MvpParams


class MvpParamsAdapter:
    """
    Builds `MvpParams` from explicit MCP tool arguments.

    Every domain entry point (`IntercalationAndSorption.*`, `CarbonHoneycombModeller.*`) takes a
    `PMvpParams` - a dataclass shaped around the GUI, holding coordinate limits, a file name and a
    set of flags. Rewriting those signatures would touch every presenter and view, so the MCP layer
    keeps a thin adapter instead: tools accept explicit typed arguments and this class packs them
    into the dataclass the domain layer expects.
    """

    @staticmethod
    def build(
            file_name: str | None = None,
            number_of_planes: int = 6,
            num_of_inter_atoms_layers: int = 2,
            to_replace_nearby_atoms: bool = True,
            to_remove_too_close_atoms: bool = False,
            to_try_to_reflect_inter_atoms: bool = True,
            to_remove_inter_atoms_with_min_and_max_x_coordinates: bool = False,
            inter_atoms_lattice_type: str = "FCC",
            x_min: float | None = None,
            x_max: float | None = None,
            y_min: float | None = None,
            y_max: float | None = None,
            z_min: float | None = None,
            z_max: float | None = None,
    ) -> PMvpParams:
        """Build `MvpParams` from explicit arguments; unset coordinate limits stay infinite."""
        params: MvpParams = MvpParams(
            file_name=file_name,
            file_format=file_name.split(".")[-1].lower() if file_name else None,
            number_of_planes=number_of_planes,
            num_of_inter_atoms_layers=num_of_inter_atoms_layers,
            to_replace_nearby_atoms=to_replace_nearby_atoms,
            to_remove_too_close_atoms=to_remove_too_close_atoms,
            to_to_try_to_reflect_inter_atoms=to_try_to_reflect_inter_atoms,
            to_remove_inter_atoms_with_min_and_max_x_coordinates=(
                to_remove_inter_atoms_with_min_and_max_x_coordinates
            ),
            inter_atoms_lattice_type=inter_atoms_lattice_type,
        )

        if x_min is not None:
            params.x_min = x_min
        if x_max is not None:
            params.x_max = x_max
        if y_min is not None:
            params.y_min = y_min
        if y_max is not None:
            params.y_max = y_max
        if z_min is not None:
            params.z_min = z_min
        if z_max is not None:
            params.z_max = z_max

        return params
