from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.interfaces import PMvpParams, PCoordinateLimits
from .coordinate_limits import CoordinateLimits


@dataclass
class MvpParams(PMvpParams):
    """Class for MVP parameters with default values."""
    # Application state fields
    current_selection: dict[str, str] = field(
        default_factory=lambda: {"project_dir": "", "subproject_dir": "", "structure_dir": ""}
    )
    application_settings: dict[str, Any] = field(default_factory=dict)
    session_history: list[dict[str, Any]] = field(default_factory=list)
    
    # Plot details
    to_build_bonds: bool = True
    to_show_coordinates: bool = False
    to_show_c_indexes: bool = False
    to_show_inter_atoms_indexes: bool = True

    # Coordinate limits (using individual fields for better serialization)
    x_min: float = -float("inf")
    x_max: float = float("inf")
    y_min: float = -float("inf")
    y_max: float = float("inf")
    z_min: float = -float("inf")
    z_max: float = float("inf")
    
    @property
    def coordinate_limits(self) -> PCoordinateLimits:
        """Get coordinate limits as CoordinateLimits object."""
        return CoordinateLimits(
            x_min=self.x_min,
            x_max=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max,
            z_min=self.z_min,
            z_max=self.z_max,
        )
    
    def set_coordinate_limits(self, limits: PCoordinateLimits) -> None:
        """Set coordinate limits from CoordinateLimits object."""
        self.x_min = limits.x_min
        self.x_max = limits.x_max
        self.y_min = limits.y_min
        self.y_max = limits.y_max
        self.z_min = limits.z_min
        self.z_max = limits.z_max

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
    inter_atoms_lattice_type: str = "FCC"
    
    # Setter methods for compatibility
    def set_to_build_bonds(self, value: bool) -> None:
        """Set build bonds flag."""
        self.to_build_bonds = value
    
    def set_to_show_coordinates(self, value: bool) -> None:
        """Set show coordinates flag."""
        self.to_show_coordinates = value
    
    def set_to_show_c_indexes(self, value: bool) -> None:
        """Set show C indexes flag."""
        self.to_show_c_indexes = value
    
    def set_to_show_inter_atoms_indexes(self, value: bool) -> None:
        """Set show inter atoms indexes flag."""
        self.to_show_inter_atoms_indexes = value
    
    def set_x_min(self, value: float | str) -> None:
        """Set X minimum coordinate."""
        if value == "":
            value = -float("inf")
        self.x_min = float(value)
    
    def set_x_max(self, value: float | str) -> None:
        """Set X maximum coordinate."""
        if value == "":
            value = float("inf")
        self.x_max = float(value)
    
    def set_y_min(self, value: float | str) -> None:
        """Set Y minimum coordinate."""
        if value == "":
            value = -float("inf")
        self.y_min = float(value)
    
    def set_y_max(self, value: float | str) -> None:
        """Set Y maximum coordinate."""
        if value == "":
            value = float("inf")
        self.y_max = float(value)
    
    def set_z_min(self, value: float | str) -> None:
        """Set Z minimum coordinate."""
        if value == "":
            value = -float("inf")
        self.z_min = float(value)
    
    def set_z_max(self, value: float | str) -> None:
        """Set Z maximum coordinate."""
        if value == "":
            value = float("inf")
        self.z_max = float(value)
    
    def set_bonds_num_of_min_distances(self, value: int) -> None:
        """Set bonds number of min distances."""
        self.bonds_num_of_min_distances = value
    
    def set_bonds_skip_first_distances(self, value: int) -> None:
        """Set bonds skip first distances."""
        self.bonds_skip_first_distances = value
    
    def set_to_show_plane_lengths(self, value: bool) -> None:
        """Set show plane lengths flag."""
        self.to_show_plane_lengths = value
    
    def set_to_show_dists_to_plane(self, value: bool) -> None:
        """Set show distances to plane flag."""
        self.to_show_dists_to_plane = value
    
    def set_to_show_dists_to_edges(self, value: bool) -> None:
        """Set show distances to edges flag."""
        self.to_show_dists_to_edges = value
    
    def set_to_show_channel_angles(self, value: bool) -> None:
        """Set show channel angles flag."""
        self.to_show_channel_angles = value
    
    def set_file_name(self, value: str) -> None:
        """Set file name."""
        self.file_name = value
    
    def set_file_format(self, value: str) -> None:
        """Set file format."""
        self.file_format = value
    
    def set_excel_file_name(self, value: str) -> None:
        """Set Excel file name."""
        self.excel_file_name = value
    
    def set_dat_file_name(self, value: str) -> None:
        """Set DAT file name."""
        self.dat_file_name = value
    
    def set_pdb_file_name(self, value: str) -> None:
        """Set PDB file name."""
        self.pdb_file_name = value
    
    def set_number_of_planes(self, value: int) -> None:
        """Set number of planes."""
        self.number_of_planes = value
    
    def set_num_of_inter_atoms_layers(self, value: int) -> None:
        """Set number of inter atoms layers."""
        self.num_of_inter_atoms_layers = value
    
    def set_to_translate_inter(self, value: bool) -> None:
        """Set translate inter atoms flag."""
        self.to_translate_inter = value
    
    def set_to_replace_nearby_atoms(self, value: bool) -> None:
        """Set replace nearby atoms flag."""
        self.to_replace_nearby_atoms = value
    
    def set_to_remove_too_close_atoms(self, value: bool) -> None:
        """Set remove too close atoms flag."""
        self.to_remove_too_close_atoms = value
    
    def set_to_to_try_to_reflect_inter_atoms(self, value: bool) -> None:
        """Set try to reflect inter atoms flag."""
        self.to_to_try_to_reflect_inter_atoms = value
    
    def set_to_equidistant_inter_points(self, value: bool) -> None:
        """Set equidistant inter points flag."""
        self.to_equidistant_inter_points = value
    
    def set_to_filter_inter_atoms(self, value: bool) -> None:
        """Set filter inter atoms flag."""
        self.to_filter_inter_atoms = value
    
    def set_to_remove_inter_atoms_with_min_and_max_x_coordinates(self, value: bool) -> None:
        """Set remove inter atoms with min and max X coordinates flag."""
        self.to_remove_inter_atoms_with_min_and_max_x_coordinates = value
    
    def set_inter_atoms_lattice_type(self, value: str) -> None:
        """Set inter atoms lattice type."""
        self.inter_atoms_lattice_type = value
    
    def set_current_selection(self, selection: dict[str, str]) -> None:
        """Set current selection."""
        self.current_selection = selection
    
    def set_application_settings(self, settings: dict[str, Any]) -> None:
        """Set application settings."""
        self.application_settings = settings
    
    def save_session_state(self, state: dict[str, Any]) -> None:
        """Save session state to history."""
        self.session_history.append(state)
        # Keep only last 50 sessions
        if len(self.session_history) > 50:
            self.session_history = self.session_history[-50:]
