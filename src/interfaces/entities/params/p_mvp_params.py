from typing import Protocol
from pathlib import Path


from .p_coordinate_limits import PCoordinateLimits


class PMvpParams(Protocol):
    """Protocol for MVP parameters."""
    to_build_bonds: bool
    to_show_coordinates: bool
    to_show_c_indexes: bool
    to_show_inter_atoms_indexes: bool

    coordinate_limits: PCoordinateLimits

    bonds_num_of_min_distances: int
    bonds_skip_first_distances: int

    to_show_dists_to_plane: bool
    to_show_dists_to_edges: bool
    to_show_channel_angles: bool
    to_show_plane_lengths: bool

    data_dir: Path
    file_name: str
    file_format: str
    available_formats: list[str]
    excel_file_name: str
    dat_file_name: str
    pdb_file_name: str

    number_of_planes: int
    num_of_inter_atoms_layers: int
    to_translate_inter: bool
    to_replace_nearby_atoms: bool
    to_remove_too_close_atoms: bool
    to_to_try_to_reflect_inter_atoms: bool
    to_equidistant_inter_points: bool
    to_filter_inter_atoms: bool
    to_remove_inter_atoms_with_min_and_max_x_coordinates: bool
    inter_atoms_lattice_type: str
