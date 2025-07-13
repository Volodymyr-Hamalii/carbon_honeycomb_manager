from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox

import pandas as pd

from src.utils import Logger, PathBuilder, FileReader, ConstantsAtomParams, ATOM_PARAMS_MAP

from ..viewmodels import VMIntercalationAndSorption
from ..components import (
    Button,
    CheckBox,
    DropdownList,
    InputField,
    InputFieldCoordLimits,
    Table,
)
from .windows_template import WindowsTemplate


__all__: list[str] = [
    "UpdateInterCoordinatesTableWindow",
    "TranslateInterToOtherPlanesWindow",
    "TranslateInterToAllChannelsWindow",
    "GetInterChcDetailsTblWindow",
    "GetInterChcConstantsWindow",
]


logger = Logger("IntercalationAndSorptionWindow")


class _IntercalationAndSorptionUtils:
    def __init__(
            self,
            view_model: VMIntercalationAndSorption,
            structure_dir: str,
            project_dir: str,
            subproject_dir: str,
    ) -> None:
        self.view_model: VMIntercalationAndSorption = view_model
        self.structure_dir: str = structure_dir
        self.project_dir: str = project_dir
        self.subproject_dir: str = subproject_dir

        self.file_names: list[str] = []
        self._refresh_file_name_lists()

    def _refresh_file_name_lists(
            self,
            dropdown_list: DropdownList | None = None,
    ) -> None:
        path: Path = PathBuilder.build_path_to_result_data_dir(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )
        self.file_names: list[str] = FileReader.read_list_of_files(
            path, format=".xlsx", to_include_nested_files=True) or ["None"]

        if (not self.view_model.file_name) or (
                self.view_model.file_name == "None") or (
                self.view_model.file_name not in self.file_names):
            self.view_model.set_file_name(self.file_names[0])

        if dropdown_list:
            file_name: str = self.view_model.file_name
            dropdown_list.set_options(
                self.file_names,
                default_value=file_name if (file_name and file_name != "None") else None,
            )


class UpdateInterCoordinatesTableWindow(_IntercalationAndSorptionUtils, WindowsTemplate):
    """ Update intercalated to CHC atoms coordinates table """

    def __init__(
            self,
            view_model: VMIntercalationAndSorption,
            structure_dir: str,
            project_dir: str,
            subproject_dir: str,
    ) -> None:
        super().__init__(view_model, structure_dir, project_dir, subproject_dir)
        self.create_window(
            title=f"Update coordinates table ({self.structure_dir})",
            description=(
                "Allows to plot the selected structure, or update the Excel file with intercalated "
                "atoms coordinates (to remove the empty rows and rebuild the dist matrix). "
                "If the file is not found, the program will build "
                "the intercalated atoms for the provided number of planes."
            ),
        )
        self.create_ui()

    def create_ui(self) -> None:
        # Create a frame to hold the columns
        columns_frame = ctk.CTkFrame(self.window)
        columns_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create frames for left and right columns inside the columns_frame
        left_frame = ctk.CTkFrame(columns_frame)
        right_frame = ctk.CTkFrame(columns_frame)

        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Left column inputs

        self.file_names_dropdown: DropdownList = self.pack_dropdown_list(
            left_frame,
            options=self.file_names,
            command=self.view_model.set_file_name,
            title="Select the file to plot/update",
        )

        self.number_of_planes_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Number of planes",
            command=self.update_number_of_planes,
            default_value=self.view_model.number_of_planes,
        )

        self.num_of_min_distances_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Number of min distances for bonds",
            command=self.update_num_of_min_distances,
            default_value=self.view_model.bonds_num_of_min_distances,
        )

        self.bonds_skip_first_distances_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Skip first distances for bonds",
            command=self.update_bonds_skip_first_distances,
            default_value=self.view_model.bonds_skip_first_distances,
        )

        # Label for the parameters to generate the Excel file
        self.label_for_checkboxes: ctk.CTkLabel = self.pack_label(
            left_frame,
            text="Parameters to generate the base Excel file\nwith intercalated atoms coordinates",
            pady=(10, 0),
        )

        self.to_replace_nearby_atoms_checkbox: CheckBox = self.pack_check_box(
            left_frame,
            text="Replace nearby atoms",
            command=self.update_to_replace_nearby_atoms,
            default=self.view_model.to_replace_nearby_atoms,
        )

        self.to_remove_too_close_atoms_checkbox: CheckBox = self.pack_check_box(
            left_frame,
            text="Remove too close atoms",
            command=self.update_to_remove_too_close_atoms,
            default=self.view_model.to_remove_too_close_atoms,
        )

        # Right column inputs

        self.num_of_inter_atoms_layers_input_field: InputField = self.pack_input_field(
            right_frame,
            text="Number of intercalated layers on the plot",
            command=self.update_num_of_inter_atoms_layers,
            default_value=self.view_model.num_of_inter_atoms_layers,
        )

        self.coord_x_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="X plot limits",
            command=self.update_x_coord_limits,
            default_min=self.view_model.x_min,
            default_max=self.view_model.x_max,
        )

        self.coord_y_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="Y plot limits",
            command=self.update_y_coord_limits,
            default_min=self.view_model.y_min,
            default_max=self.view_model.y_max,
        )

        self.coord_z_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="Z plot limits",
            command=self.update_z_coord_limits,
            default_min=self.view_model.z_min,
            default_max=self.view_model.z_max,
        )

        self.to_show_inter_atoms_indexes_checkbox: CheckBox = self.pack_check_box(
            right_frame,
            text="Show atom's indexes on the plot",
            command=self.update_to_show_inter_atoms_indexes,
            default=self.view_model.to_show_inter_atoms_indexes,
        )

        # Remaining widgets below the columns
        self.plot_btn: Button = self.pack_button(
            self.window,
            text="Plot the model",
            command=self.plot_inter_in_c_structure,
        )

        self.btn: Button = self.pack_button(
            self.window,
            text="Update the Excel file",
            command=self.update_inter_plane_coordinates_file,
        )

        self.generate_tbl_btn: Button = self.pack_button(
            self.window,
            text="Generate the Excel file with intercalated atoms coordinates for plane",
            command=self.generate_inter_plane_coordinates_file,
            pady=(10, 25),
        )

    def plot_inter_in_c_structure(self) -> None:
        try:
            self.view_model.plot_inter_in_c_structure(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_inter_plane_coordinates_file(self) -> None:
        try:
            path_to_file: Path = self.view_model.update_inter_plane_coordinates_file(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
            self._refresh_file_name_lists(dropdown_list=self.file_names_dropdown)
            messagebox.showinfo("Success", f"Intercalated atoms plane coordinates file saved to\n{path_to_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_inter_plane_coordinates_file(self) -> None:
        try:
            path_to_file: Path = self.view_model.generate_inter_plane_coordinates_file(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
            self._refresh_file_name_lists(dropdown_list=self.file_names_dropdown)
            messagebox.showinfo("Success", f"Intercalated atoms plane coordinates file saved to\n{path_to_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_to_show_inter_atoms_indexes(self) -> None:
        value = bool(self.to_show_inter_atoms_indexes_checkbox.get())
        self.view_model.set_to_show_inter_atoms_indexes(value)

    def update_number_of_planes(self) -> None:
        value = int(self.number_of_planes_input_field.entry.get())
        self.view_model.set_number_of_planes(value)

    def update_num_of_min_distances(self) -> None:
        value = int(self.num_of_min_distances_input_field.entry.get())
        self.view_model.set_bonds_num_of_min_distances(value)

    def update_bonds_skip_first_distances(self) -> None:
        value = int(self.bonds_skip_first_distances_input_field.entry.get())
        self.view_model.set_bonds_skip_first_distances(value)

    def update_to_replace_nearby_atoms(self) -> None:
        value = bool(self.to_replace_nearby_atoms_checkbox.get())
        self.view_model.set_to_replace_nearby_atoms(value)

    def update_to_remove_too_close_atoms(self) -> None:
        value = bool(self.to_remove_too_close_atoms_checkbox.get())
        self.view_model.set_to_remove_too_close_atoms(value)

    def update_num_of_inter_atoms_layers(self) -> None:
        value = int(self.num_of_inter_atoms_layers_input_field.entry.get())

        if value > 3:
            messagebox.showerror("Error", "The number of intercalated layers cannot be greater than 3.")
            return

        self.view_model.set_num_of_inter_atoms_layers(value)

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


class TranslateInterToOtherPlanesWindow(_IntercalationAndSorptionUtils, WindowsTemplate):
    """ Translate intercalated to CHC atoms to other planes """

    def __init__(
            self,
            view_model: VMIntercalationAndSorption,
            structure_dir: str,
            project_dir: str,
            subproject_dir: str,
    ) -> None:
        super().__init__(view_model, structure_dir, project_dir, subproject_dir)
        self.create_window(
            title=f"Translate intercalated atoms to other planes ({self.structure_dir})",
            description=(
                "Read the selected file with coordinates for N planes "
                "and translate intercalated atoms to other planes."
            ),
        )
        self.create_ui()

    def create_ui(self) -> None:
        self.file_names_dropdown: DropdownList = self.pack_dropdown_list(
            self.window,
            options=self.file_names,
            command=self.view_model.set_file_name,
            title="Intercalated atoms coordinates table to translate",
        )

        # Create a frame to hold the columns
        columns_frame = ctk.CTkFrame(self.window)
        columns_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create frames for left and right columns inside the columns_frame
        left_frame = ctk.CTkFrame(columns_frame)
        right_frame = ctk.CTkFrame(columns_frame)

        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Left column inputs
        self.to_try_to_reflect_inter_atoms_checkbox: CheckBox = self.pack_check_box(
            left_frame,
            text="Try to reflect intercalated atoms to fit the plane",
            command=self.update_to_to_try_to_reflect_inter_atoms,
            default=self.view_model.to_to_try_to_reflect_inter_atoms,
        )

        self.number_of_planes_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Number of planes",
            command=self.update_number_of_planes,
            default_value=self.view_model.number_of_planes,
        )

        self.num_of_min_distances_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Number of min distances for bonds",
            command=self.update_num_of_min_distances,
            default_value=self.view_model.bonds_num_of_min_distances,
        )

        self.bonds_skip_first_distances_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Skip first distances for bonds",
            command=self.update_bonds_skip_first_distances,
            default_value=self.view_model.bonds_skip_first_distances,
        )

        self.num_of_inter_atoms_layers_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Number ofintercalated atoms layers on the plot",
            command=self.update_num_of_inter_atoms_layers,
            default_value=self.view_model.num_of_inter_atoms_layers,
        )

        # Right column inputs
        self.coord_x_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="X plot limits",
            command=self.update_x_coord_limits,
            default_min=self.view_model.x_min,
            default_max=self.view_model.x_max,
        )

        self.coord_y_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="Y plot limits",
            command=self.update_y_coord_limits,
            default_min=self.view_model.y_min,
            default_max=self.view_model.y_max,
        )

        self.coord_z_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="Z plot limits",
            command=self.update_z_coord_limits,
            default_min=self.view_model.z_min,
            default_max=self.view_model.z_max,
        )

        self.to_show_inter_atoms_indexes_checkbox: CheckBox = self.pack_check_box(
            right_frame,
            text="Show atom's indexes on the plot",
            command=self.update_to_show_inter_atoms_indexes,
            default=self.view_model.to_show_inter_atoms_indexes,
        )

        self.translate_btn: Button = self.pack_button(
            self.window,
            text="Build the model",
            command=self.translate_inter_atoms_to_other_planes,
        )

        self.btn: Button = self.pack_button(
            self.window,
            text="Update the Excel file",
            command=self.update_file,
            pady=(10, 25),
        )

    def translate_inter_atoms_to_other_planes(self) -> None:
        try:
            atom_params: ConstantsAtomParams = ATOM_PARAMS_MAP[self.subproject_dir.lower()]
            self.view_model.translate_inter_atoms_to_other_planes(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_file(self) -> None:
        try:
            path_to_file: Path = self.view_model.update_inter_channel_coordinates(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
            self._refresh_file_name_lists(dropdown_list=self.file_names_dropdown)
            messagebox.showinfo("Success", f"Intercalated atoms coordinates table saved to\n{path_to_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_to_show_inter_atoms_indexes(self) -> None:
        value = bool(self.to_show_inter_atoms_indexes_checkbox.get())
        self.view_model.set_to_show_inter_atoms_indexes(value)

    def update_number_of_planes(self) -> None:
        value = int(self.number_of_planes_input_field.entry.get())
        self.view_model.set_number_of_planes(value)

    def update_num_of_min_distances(self) -> None:
        value = int(self.num_of_min_distances_input_field.entry.get())
        self.view_model.set_bonds_num_of_min_distances(value)

    def update_bonds_skip_first_distances(self) -> None:
        value = int(self.bonds_skip_first_distances_input_field.entry.get())
        self.view_model.set_bonds_skip_first_distances(value)

    def update_to_to_try_to_reflect_inter_atoms(self) -> None:
        value = bool(self.to_try_to_reflect_inter_atoms_checkbox.get())
        self.view_model.set_to_to_try_to_reflect_inter_atoms(value)

    def update_num_of_inter_atoms_layers(self) -> None:
        value = int(self.num_of_inter_atoms_layers_input_field.entry.get())

        if value > 3:
            self.num_of_inter_atoms_layers_input_field.label.configure(
                text="The number of AL layers cannot be greater than 3.")
            return

        self.view_model.set_num_of_inter_atoms_layers(value)

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


class TranslateInterToAllChannelsWindow(_IntercalationAndSorptionUtils, WindowsTemplate):
    """ Translate intercalated to CHC atoms to all channels """

    def __init__(
            self,
            view_model: VMIntercalationAndSorption,
            structure_dir: str,
            project_dir: str,
            subproject_dir: str,
    ) -> None:
        super().__init__(view_model, structure_dir, project_dir, subproject_dir)
        self.create_window(
            title=f"Translate intercalated atoms to all channels ({self.structure_dir})",
            description=(
                "Translate intercalated atoms to all channels."
            ),
        )
        self.create_ui()

    def create_ui(self) -> None:
        self.file_names_dropdown: DropdownList = self.pack_dropdown_list(
            self.window,
            options=self.file_names,
            command=self.view_model.set_file_name,
            title="Intercalated atoms coordinates table to translate",
        )

        # Create a frame to hold the columns
        columns_frame = ctk.CTkFrame(self.window)
        columns_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create frames for left and right columns inside the columns_frame
        left_frame = ctk.CTkFrame(columns_frame)
        right_frame = ctk.CTkFrame(columns_frame)

        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Left column inputs
        self.num_of_min_distances_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Number of min distances for bonds",
            command=self.update_num_of_min_distances,
            default_value=self.view_model.bonds_num_of_min_distances,
        )

        self.bonds_skip_first_distances_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Skip first distances for bonds",
            command=self.update_bonds_skip_first_distances,
            default_value=self.view_model.bonds_skip_first_distances,
        )

        self.num_of_inter_atoms_layers_input_field: InputField = self.pack_input_field(
            left_frame,
            text="Number ofintercalated atoms layers on the plot",
            command=self.update_num_of_inter_atoms_layers,
            default_value=self.view_model.num_of_inter_atoms_layers,
        )

        self.to_try_to_reflect_inter_atoms_checkbox: CheckBox = self.pack_check_box(
            left_frame,
            text="Try to reflect intercalated atoms to fit the plane\n"
            "(if no init file and the intercalated atoms will be calculated)",
            command=self.update_to_to_try_to_reflect_inter_atoms,
            default=self.view_model.to_to_try_to_reflect_inter_atoms,
        )

        self.to_remove_inter_atoms_with_min_and_max_x_coordinates_checkbox: CheckBox = self.pack_check_box(
            left_frame,
            text="Remove intercalated atoms with min and max X coordinates",
            command=self.update_to_remove_inter_atoms_with_min_and_max_x_coordinates,
            default=self.view_model.to_remove_inter_atoms_with_min_and_max_x_coordinates,
        )

        # Right column inputs
        self.coord_x_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="X plot limits",
            command=self.update_x_coord_limits,
            default_min=self.view_model.x_min,
            default_max=self.view_model.x_max,
        )

        self.coord_y_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="Y plot limits",
            command=self.update_y_coord_limits,
            default_min=self.view_model.y_min,
            default_max=self.view_model.y_max,
        )

        self.coord_z_limits_input_field: InputFieldCoordLimits = self.pack_input_field_coord_limits(
            right_frame,
            text="Z plot limits",
            command=self.update_z_coord_limits,
            default_min=self.view_model.z_min,
            default_max=self.view_model.z_max,
        )

        self.to_show_inter_atoms_indexes_checkbox: CheckBox = self.pack_check_box(
            right_frame,
            text="Show atom's indexes on the plot",
            command=self.update_to_show_inter_atoms_indexes,
            default=self.view_model.to_show_inter_atoms_indexes,
        )

        self.translate_btn: Button = self.pack_button(
            self.window,
            text="Generate output files",
            command=self.translate_inter_atoms_to_all_channels_generate_files,
        )

        self.plot_btn: Button = self.pack_button(
            self.window,
            text="Plot structure",
            command=self.plot_inter_atoms_in_c_structure,
            pady=(10, 25),
        )

    def plot_inter_atoms_in_c_structure(self) -> None:
        try:
            self.view_model.translate_inter_to_all_channels_plot(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def translate_inter_atoms_to_all_channels_generate_files(self) -> None:
        try:
            paths: tuple[Path, Path, Path] = self.view_model.translate_inter_to_all_channels_generate_files(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
            self._refresh_file_name_lists(dropdown_list=self.file_names_dropdown)
            messagebox.showinfo("Success", f"Generated files:\n{paths[0].name}\n{paths[1].name}\n{paths[2].name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_file_name(self, value: str) -> None:
        self.view_model.set_file_name(value)

    def update_to_show_inter_atoms_indexes(self) -> None:
        value = bool(self.to_show_inter_atoms_indexes_checkbox.get())
        self.view_model.set_to_show_inter_atoms_indexes(value)

    def update_num_of_min_distances(self) -> None:
        value = int(self.num_of_min_distances_input_field.entry.get())
        self.view_model.set_bonds_num_of_min_distances(value)

    def update_bonds_skip_first_distances(self) -> None:
        value = int(self.bonds_skip_first_distances_input_field.entry.get())
        self.view_model.set_bonds_skip_first_distances(value)

    def update_to_to_try_to_reflect_inter_atoms(self) -> None:
        value = bool(self.to_try_to_reflect_inter_atoms_checkbox.get())
        self.view_model.set_to_to_try_to_reflect_inter_atoms(value)

    def update_to_remove_inter_atoms_with_min_and_max_x_coordinates(self) -> None:
        value = bool(self.to_remove_inter_atoms_with_min_and_max_x_coordinates_checkbox.get())
        self.view_model.set_to_remove_inter_atoms_with_min_and_max_x_coordinates(value)

    def update_num_of_inter_atoms_layers(self) -> None:
        value = int(self.num_of_inter_atoms_layers_input_field.entry.get())
        self.view_model.set_num_of_inter_atoms_layers(value)

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


### Model analysis windows ###


class GetInterChcDetailsTblWindow(_IntercalationAndSorptionUtils, WindowsTemplate):
    """ Get intercalated CH channel details table """

    def __init__(
            self,
            view_model: VMIntercalationAndSorption,
            structure_dir: str,
            project_dir: str,
            subproject_dir: str,
    ) -> None:
        super().__init__(view_model, structure_dir, project_dir, subproject_dir)
        self.create_window(
            title=f"Get intercalated CH channel details ({self.structure_dir})",
            description=(
                "Build a table with intercalated CH channel details (intercalated atoms coordinates, "
                "distances to the plane, distances to the carbon atoms, distances to the other intercalated atoms)."
            ),
        )
        self.create_ui()

    def create_ui(self) -> None:
        self.file_names_dropdown: DropdownList = self.pack_dropdown_list(
            self.window,
            options=self.file_names,
            command=self.view_model.set_file_name,
            title="Intercalated atoms coordinates to analyze",
        )

        self.btn_show_table: Button = self.pack_button(
            self.window,
            text="Show table",
            command=self.show_inter_atoms_in_channel_details,
        )

        self.btn_save_file: Button = self.pack_button(
            self.window,
            text="Save Excel file",
            command=self.get_inter_atoms_in_channel_details,
            pady=(10, 25),
        )

    def get_inter_atoms_in_channel_details(self) -> None:
        try:
            path_to_file: Path = self.view_model.save_inter_in_channel_details(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )
            messagebox.showinfo("Success", f"Intercalated atoms in channel details saved to\n{path_to_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_inter_atoms_in_channel_details(self) -> None:
        try:
            df: pd.DataFrame = self.view_model.get_inter_in_channel_details(
                project_dir=self.project_dir,
                subproject_dir=self.subproject_dir,
                structure_dir=self.structure_dir,
            )

            # Create a new window
            new_window = ctk.CTkToplevel(self.window)
            new_window.title(f"Intercalated CH channel details ({self.structure_dir})")

            width: int = min(len(df.columns) * 50 + 100, 1000)
            height: int = min(len(df) * 20 + 100, 1000)
            new_window.geometry(f"{width}x{height}")

            # Create and display the table in the new window
            self.table_window: Table = self.pack_table(
                new_window,
                df,
                title=self.view_model.file_name,
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))


class GetInterChcConstantsWindow(_IntercalationAndSorptionUtils, WindowsTemplate):
    """ Get intercalated CH channel constants """

    def __init__(
            self,
            view_model: VMIntercalationAndSorption,
            structure_dir: str,
            project_dir: str,
            subproject_dir: str,
    ) -> None:
        super().__init__(view_model, structure_dir, project_dir, subproject_dir)

        try:
            self.create_window(
                title=f"Get intercalated CH channel constants for {subproject_dir.title()} ({structure_dir})",
                geometry=(450, 200),
            )
            self.create_ui()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_ui(self) -> None:
        df: pd.DataFrame = self.view_model.get_inter_chc_constants(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

        # Pack the table to the current window
        self.table_window: Table = self.pack_table(
            self.window,
            df,
            # title=self.view_model.file_name,
            to_show_index=False,
        )
