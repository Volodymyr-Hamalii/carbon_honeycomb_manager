from pathlib import Path
from src.services import Constants, PathBuilder


class VMParamsSetter:
    def __init__(self) -> None:
        # Plot details
        self.to_build_bonds: bool = True
        self.to_show_coordinates: bool = False
        self.to_show_c_indexes: bool = False
        self.to_show_inter_atoms_indexes: bool = True

        self.x_min: float = -float("inf")
        self.x_max: float = float("inf")
        self.y_min: float = -float("inf")
        self.y_max: float = float("inf")
        self.z_min: float = -float("inf")
        self.z_max: float = float("inf")

        self.bonds_num_of_min_distances: int = 2
        self.bonds_skip_first_distances: int = 0

        # Channel details
        self.to_show_dists_to_plane: bool = False
        self.to_show_dists_to_edges: bool = False
        self.to_show_channel_angles: bool = True
        self.to_show_plane_lengths: bool = True

        # Files and paths
        self.data_dir: Path = Constants.path.PROJECTS_DATA_PATH
        self.file_name: str = ""
        self.file_format: str = ""  # "xlsx", "dat", "pdb"
        self.available_formats: list[str] = ["xlsx", "dat", "pdb"]
        self.excel_file_name: str = ""
        self.dat_file_name: str = ""
        self.pdb_file_name: str = ""

        # Intercalation and sorption
        self.number_of_planes: int = 6
        self.num_of_inter_atoms_layers: int = 2
        self.to_translate_inter: bool = True
        self.to_replace_nearby_atoms: bool = True
        self.to_remove_too_close_atoms: bool = False
        self.to_to_try_to_reflect_inter_atoms: bool = True
        self.to_equidistant_inter_points: bool = True
        self.to_filter_inter_atoms: bool = True
        self.to_remove_inter_atoms_with_min_and_max_x_coordinates: bool = False
        self.inter_atoms_lattice_type: str = "FCC"

    ######### Plot details #########

    def set_to_build_bonds(self, value: bool) -> None:
        self.to_build_bonds: bool = value

    def set_to_show_coordinates(self, value: bool) -> None:
        self.to_show_coordinates: bool = value

    def set_to_show_c_indexes(self, value: bool) -> None:
        self.to_show_c_indexes: bool = value

    def set_to_show_inter_atoms_indexes(self, value: bool) -> None:
        self.to_show_inter_atoms_indexes: bool = value

    def set_x_min(self, value: float | str) -> None:
        if value == "":
            value = -float("inf")
        self.x_min = float(value)

    def set_x_max(self, value: float | str) -> None:
        if value == "":
            value = float("inf")
        self.x_max = float(value)

    def set_y_min(self, value: float | str) -> None:
        if value == "":
            value = -float("inf")
        self.y_min = float(value)

    def set_y_max(self, value: float | str) -> None:
        if value == "":
            value = float("inf")
        self.y_max = float(value)

    def set_z_min(self, value: float | str) -> None:
        if value == "":
            value = -float("inf")
        self.z_min = float(value)

    def set_z_max(self, value: float | str) -> None:
        if value == "":
            value = float("inf")
        self.z_max = float(value)

    def set_bonds_num_of_min_distances(self, value: int) -> None:
        self.bonds_num_of_min_distances: int = value

    def set_bonds_skip_first_distances(self, value: int) -> None:
        self.bonds_skip_first_distances: int = value

    ######### Channel details #########

    def set_to_show_plane_lengths(self, value: bool) -> None:
        self.to_show_plane_lengths: bool = value

    def set_to_show_dists_to_plane(self, value: bool) -> None:
        self.to_show_dists_to_plane: bool = value

    def set_to_show_dists_to_edges(self, value: bool) -> None:
        self.to_show_dists_to_edges: bool = value

    def set_to_show_channel_angles(self, value: bool) -> None:
        self.to_show_channel_angles: bool = value

    ######### Files and paths #########

    def set_data_dir(
            self,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
            structure_data_dir: str,
    ) -> None:
        if structure_data_dir == Constants.file_names.INIT_DATA_DIR:
            self.data_dir: Path = PathBuilder.build_path_to_init_data_dir(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
            )
        elif structure_data_dir == Constants.file_names.RESULT_DATA_DIR:
            self.data_dir: Path = PathBuilder.build_path_to_result_data_dir(
                project_dir=project_dir,
                subproject_dir=subproject_dir,
                structure_dir=structure_dir,
            )
        else:
            raise ValueError(f"Invalid data directory: {structure_data_dir}")

    def set_file_name(self, value: str) -> None:
        self.file_name: str = value

    def set_file_format(self, value: str) -> None:
        self.file_format: str = value

    def set_excel_file_name(self, value: str) -> None:
        self.excel_file_name: str = value

    def set_dat_file_name(self, value: str) -> None:
        self.dat_file_name: str = value

    def set_pdb_file_name(self, value: str) -> None:
        self.pdb_file_name: str = value

    ######### Intercalation and sorption #########

    def set_number_of_planes(self, value: int) -> None:
        self.number_of_planes: int = value

    def set_num_of_inter_atoms_layers(self, value: int) -> None:
        self.num_of_inter_atoms_layers: int = value

    def set_to_translate_inter(self, value: bool) -> None:
        self.to_translate_inter: bool = value

    def set_to_replace_nearby_atoms(self, value: bool) -> None:
        self.to_replace_nearby_atoms: bool = value

    def set_to_remove_too_close_atoms(self, value: bool) -> None:
        self.to_remove_too_close_atoms: bool = value

    def set_to_to_try_to_reflect_inter_atoms(self, value: bool) -> None:
        self.to_to_try_to_reflect_inter_atoms: bool = value

    def set_to_equidistant_inter_points(self, value: bool) -> None:
        self.to_equidistant_inter_points: bool = value

    def set_to_filter_inter_atoms(self, value: bool) -> None:
        self.to_filter_inter_atoms: bool = value

    def set_to_remove_inter_atoms_with_min_and_max_x_coordinates(self, value: bool) -> None:
        self.to_remove_inter_atoms_with_min_and_max_x_coordinates: bool = value

    def set_inter_atoms_lattice_type(self, value: str) -> None:
        self.inter_atoms_lattice_type: str = value
