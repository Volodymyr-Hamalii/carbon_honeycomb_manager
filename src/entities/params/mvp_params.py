from dataclasses import dataclass, field
from pathlib import Path

from src.interfaces import PMvpParams
from .coordinate_limits import CoordinateLimits


@dataclass
class MvpParams(PMvpParams):
    """Class for MVP parameters with default values."""
    to_build_bonds: bool = True
    to_show_coordinates: bool = False
    to_show_c_indexes: bool = False
    to_show_inter_atoms_indexes: bool = True

    coordinate_limits = CoordinateLimits(
        x_min=-float("inf"),
        x_max=float("inf"),
        y_min=-float("inf"),
        y_max=float("inf"),
        z_min=-float("inf"),
        z_max=float("inf"),
    )

    bonds_num_of_min_distances: int = 2
    bonds_skip_first_distances: int = 0

    to_show_dists_to_plane: bool = False
    to_show_dists_to_edges: bool = False
    to_show_channel_angles: bool = True
    to_show_plane_lengths: bool = True

    data_dir: Path = Path()  # Default to an empty Path
    file_name: str | None = None
    file_format: str | None = None  # "xlsx", "dat", "pdb"
    available_formats: list[str] = field(default_factory=lambda: ["xlsx", "dat", "pdb"])
    excel_file_name: str | None = None
    dat_file_name: str | None = None
    pdb_file_name: str | None = None

    number_of_planes: int = 6
    num_of_inter_atoms_layers: int = 2
    to_translate_inter: bool = True
    to_replace_nearby_atoms: bool = True
    to_remove_too_close_atoms: bool = False
    to_to_try_to_reflect_inter_atoms: bool = True
    to_equidistant_inter_points: bool = True
    to_filter_inter_atoms: bool = True
    to_remove_inter_atoms_with_min_and_max_x_coordinates: bool = False
    inter_atoms_lattice_type: str | None = None
