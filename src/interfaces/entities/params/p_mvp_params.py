from typing import Protocol, Any
from pathlib import Path


from .p_coordinate_limits import PCoordinateLimits


class PMvpParams(Protocol):
    """Protocol for MVP parameters."""
    # Application state fields
    current_selection: dict[str, str]
    application_settings: dict[str, Any]
    session_history: list[dict[str, Any]]
    
    to_build_bonds: bool
    to_show_coordinates: bool
    to_show_c_indexes: bool
    to_show_inter_atoms_indexes: bool

    x_min: float = -float("inf")
    x_max: float = float("inf")
    y_min: float = -float("inf")
    y_max: float = float("inf")
    z_min: float = -float("inf")
    z_max: float = float("inf")
    coordinate_limits: PCoordinateLimits

    bonds_num_of_min_distances: int
    bonds_skip_first_distances: int

    to_show_dists_to_plane: bool
    to_show_dists_to_edges: bool
    to_show_channel_angles: bool
    to_show_plane_lengths: bool

    data_dir: Path
    file_name: str | None
    file_format: str | None
    available_formats: list[str]
    excel_file_name: str | None
    dat_file_name: str | None
    pdb_file_name: str | None

    number_of_planes: int
    num_of_inter_atoms_layers: int
    to_translate_inter: bool
    to_replace_nearby_atoms: bool
    to_remove_too_close_atoms: bool
    to_to_try_to_reflect_inter_atoms: bool
    to_equidistant_inter_points: bool
    to_filter_inter_atoms: bool
    to_remove_inter_atoms_with_min_and_max_x_coordinates: bool

    to_set_equal_scale: bool
    is_interactive_mode: bool
    to_build_edge_vertical_lines: bool
    to_show_grid: bool
    to_show_legend: bool

    inter_atoms_lattice_type: str

    def set_coordinate_limits(self, limits: PCoordinateLimits) -> None:
        ...

    def set_to_build_bonds(self, value: bool) -> None:
        ...

    def set_to_show_coordinates(self, value: bool) -> None:
        ...

    def set_to_show_c_indexes(self, value: bool) -> None:
        ...

    def set_to_show_inter_atoms_indexes(self, value: bool) -> None:
        ...

    def set_x_min(self, value: float | str) -> None:
        ...

    def set_x_max(self, value: float | str) -> None:
        ...

    def set_y_min(self, value: float | str) -> None:
        ...

    def set_y_max(self, value: float | str) -> None:
        ...

    def set_z_min(self, value: float | str) -> None:
        ...

    def set_z_max(self, value: float | str) -> None:
        ...

    def set_bonds_num_of_min_distances(self, value: int) -> None:
        ...

    def set_bonds_skip_first_distances(self, value: int) -> None:
        ...

    def set_to_show_plane_lengths(self, value: bool) -> None:
        ...

    def set_to_show_dists_to_plane(self, value: bool) -> None:
        ...

    def set_to_show_dists_to_edges(self, value: bool) -> None:
        ...

    def set_to_show_channel_angles(self, value: bool) -> None:
        ...

    def set_file_name(self, value: str) -> None:
        ...

    def set_file_format(self, value: str) -> None:
        ...

    def set_excel_file_name(self, value: str) -> None:
        ...

    def set_dat_file_name(self, value: str) -> None:
        ...

    def set_pdb_file_name(self, value: str) -> None:
        ...

    def set_number_of_planes(self, value: int) -> None:
        ...

    def set_num_of_inter_atoms_layers(self, value: int) -> None:
        ...

    def set_to_translate_inter(self, value: bool) -> None:
        ...

    def set_to_replace_nearby_atoms(self, value: bool) -> None:
        ...

    def set_to_remove_too_close_atoms(self, value: bool) -> None:
        ...

    def set_to_to_try_to_reflect_inter_atoms(self, value: bool) -> None:
        ...

    def set_to_equidistant_inter_points(self, value: bool) -> None:
        ...

    def set_to_filter_inter_atoms(self, value: bool) -> None:
        ...

    def set_to_remove_inter_atoms_with_min_and_max_x_coordinates(self, value: bool) -> None:
        ...

    def set_inter_atoms_lattice_type(self, value: str) -> None:
        ...

    # Setter methods for application state
    def set_current_selection(self, selection: dict[str, str]) -> None:
        ...

    def set_application_settings(self, settings: dict[str, Any]) -> None:
        ...

    def save_session_state(self, state: dict[str, Any]) -> None:
        ...
