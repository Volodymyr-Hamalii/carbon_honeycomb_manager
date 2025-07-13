from pathlib import Path

from src.services.utils import Constants, FileReader, PathBuilder
from src.ui.components import (
    Button,
    CheckBox,
    DropdownList,
    InputField,
    InputFieldCoordLimits,
)
from .windows_template import WindowsTemplate


class InitDataWindow(WindowsTemplate):
    def __init__(
            self,
            view_model: VMShowInitData,
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> None:
        super().__init__()
        self.project_dir: str = project_dir
        self.subproject_dir: str = subproject_dir
        self.structure_dir: str = structure_dir

        self.view_model: VMShowInitData = view_model
        self.view_model.set_data_dir(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
            structure_data_dir=Constants.file_names.INIT_DATA_DIR,
        )

        self.file_names: list[str] = []
        self._refresh_file_name_lists()

        self.create_window(
            title=f"Show initial CH structure ({self.structure_dir}) ",
            # description=(
            #     "Write an Excel file withintercalated atoms in channel details (Intercalated atoms coordinates, "
            #     "Intercalated atoms indexes,intercalated atoms distances from the C atoms, etc.)"
            # ),
        )
        self.create_ui()

    def _refresh_file_name_lists(self) -> None:
        path: Path = PathBuilder.build_path_to_init_data_dir(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )
        self.file_names: list[str] = FileReader.read_list_of_files(path, to_include_nested_files=True) or ["None"]
        if (not self.view_model.file_name) or (
                self.view_model.file_name == "None") or (
                self.view_model.file_name not in self.file_names):
            self.view_model.set_file_name(self.file_names[0])

    def create_ui(self) -> None:
        self.file_names_dropdown: DropdownList = self.pack_dropdown_list(
            self.window,
            options=self.file_names,
            command=self.view_model.set_file_name,
            title="Select the file to plot",
            pady=(0, 10),
        )

        # Checkbox for to_build_bonds
        self.to_build_bonds_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Build bonds",
            command=self.update_to_build_bonds,
            default=self.view_model.to_build_bonds,
        )

        # Checkbox for to_show_coordinates
        self.to_show_coordinates_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Show coordinates",
            command=self.update_to_show_coordinates,
            default=self.view_model.to_show_coordinates,
        )

        # Checkbox for to_show_indexes
        self.to_show_c_indexes_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Show C atoms indexes",
            command=self.update_to_show_c_indexes,
            default=self.view_model.to_show_c_indexes,
        )

        # Input field for bonds_num_of_min_distances
        self.bonds_num_of_min_distances_input_field: InputField = self.pack_input_field(
            self.window, text="Number of min distances for bonds",
            command=self.update_bonds_num_of_min_distances,
            default_value=self.view_model.bonds_num_of_min_distances,
        )

        # Input field for bonds_skip_first_distances
        self.bonds_skip_first_distances_input_field: InputField = self.pack_input_field(
            self.window, text="Skip first distances for bonds",
            command=self.update_bonds_skip_first_distances,
            default_value=self.view_model.bonds_skip_first_distances,
        )

        # Input field for coord_limits
        self.coord_x_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            self.window, text="X plot limits",
            command=self.update_x_coord_limits,
            default_min=self.view_model.x_min,
            default_max=self.view_model.x_max,
        )

        self.coord_y_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            self.window, text="Y plot limits",
            command=self.update_y_coord_limits,
            default_min=self.view_model.y_min,
            default_max=self.view_model.y_max,
        )

        self.coord_z_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            self.window, text="Z plot limits",
            command=self.update_z_coord_limits,
            default_min=self.view_model.z_min,
            default_max=self.view_model.z_max,
        )

        # Button to show initial structure
        self.init_structure_btn: Button = self.pack_button(
            self.window, text="Show initial structure",
            command=self.show_init_structure,
        )

        # Button to show initial structure
        self.one_channel_structure_btn: Button = self.pack_button(
            self.window, text="Show one channel",
            command=self.show_one_channel_structure,
            pady=(10, 25),
        )

    def show_init_structure(self) -> None:
        self.view_model.show_init_structure(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def show_one_channel_structure(self) -> None:
        self.view_model.show_one_channel_structure(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def update_to_build_bonds(self) -> None:
        value = bool(self.to_build_bonds_checkbox.get())
        self.view_model.set_to_build_bonds(value)

    def update_to_show_coordinates(self) -> None:
        value = bool(self.to_show_coordinates_checkbox.get())
        self.view_model.set_to_show_coordinates(value)

    def update_to_show_c_indexes(self) -> None:
        value = bool(self.to_show_c_indexes_checkbox.get())
        self.view_model.set_to_show_c_indexes(value)

    def update_bonds_num_of_min_distances(self) -> None:
        value = int(self.bonds_num_of_min_distances_input_field.entry.get())
        self.view_model.set_bonds_num_of_min_distances(value)

    def update_bonds_skip_first_distances(self) -> None:
        value = int(self.bonds_skip_first_distances_input_field.entry.get())
        self.view_model.set_bonds_skip_first_distances(value)

    def update_x_coord_limits(self) -> None:
        value_min: str = self.coord_x_limits_input_field.min_entry.get()
        value_max: str = self.coord_x_limits_input_field.max_entry.get()
        self.view_model.set_x_min(value_min)
        self.view_model.set_x_max(value_max)

    def update_y_coord_limits(self) -> None:
        value_min: str = self.coord_y_limits_input_field.min_entry.get()
        value_max: str = self.coord_y_limits_input_field.max_entry.get()
        self.view_model.set_y_min(value_min)
        self.view_model.set_y_max(value_max)

    def update_z_coord_limits(self) -> None:
        value_min: str = self.coord_z_limits_input_field.min_entry.get()
        value_max: str = self.coord_z_limits_input_field.max_entry.get()
        self.view_model.set_z_min(value_min)
        self.view_model.set_z_max(value_max)
