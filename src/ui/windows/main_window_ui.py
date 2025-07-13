from src.ui.components import (
    Button,
    CheckBox,
    DropdownList,
    InputField,
    InputFieldCoordLimits,
)
from src.interfaces.ui import (
    IWindowGeneralTemplate,
    IButton,
    ICheckBox,
    IDropdownList,
    IInputField,
    IInputFieldCoordLimits,
)


class MainWindowUI:
    @classmethod
    def set_ui(cls, view: IWindowGeneralTemplate) -> None:
        view.file_names_dropdown: DropdownList = view.pack_dropdown_list(
            view.window,
            options=view.file_names,
            command=view.view_model.set_file_name,
            title="Select the file to plot",
            pady=(0, 10),
        )

        # Checkbox for to_build_bonds
        view.to_build_bonds_checkbox: CheckBox = view.pack_check_box(
            view.window, text="Build bonds",
            command=view.update_to_build_bonds,
            default=view.view_model.to_build_bonds,
        )

        # Checkbox for to_show_coordinates
        view.to_show_coordinates_checkbox: CheckBox = view.pack_check_box(
            view.window, text="Show coordinates",
            command=view.update_to_show_coordinates,
            default=view.view_model.to_show_coordinates,
        )

        # Checkbox for to_show_indexes
        view.to_show_c_indexes_checkbox: CheckBox = view.pack_check_box(
            view.window, text="Show C atoms indexes",
            command=view.update_to_show_c_indexes,
            default=view.view_model.to_show_c_indexes,
        )

        # Input field for bonds_num_of_min_distances
        view.bonds_num_of_min_distances_input_field: InputField = view.pack_input_field(
            view.window, text="Number of min distances for bonds",
            command=view.update_bonds_num_of_min_distances,
            default_value=view.view_model.bonds_num_of_min_distances,
        )

        # Input field for bonds_skip_first_distances
        view.bonds_skip_first_distances_input_field: InputField = view.pack_input_field(
            view.window, text="Skip first distances for bonds",
            command=view.update_bonds_skip_first_distances,
            default_value=view.view_model.bonds_skip_first_distances,
        )

        # Input field for coord_limits
        view.coord_x_limits_input_field: InputFieldCoordLimits = view.pack_input_field_coord_limits(
            view.window, text="X plot limits",
            command=view.update_x_coord_limits,
            default_min=view.view_model.x_min,
            default_max=view.view_model.x_max,
        )

        view.coord_y_limits_input_field: InputFieldCoordLimits = view.pack_input_field_coord_limits(
            view.window, text="Y plot limits",
            command=view.update_y_coord_limits,
            default_min=view.view_model.y_min,
            default_max=view.view_model.y_max,
        )

        view.coord_z_limits_input_field: InputFieldCoordLimits = view.pack_input_field_coord_limits(
            view.window, text="Z plot limits",
            command=view.update_z_coord_limits,
            default_min=view.view_model.z_min,
            default_max=view.view_model.z_max,
        )

        # Button to show initial structure
        view.init_structure_btn: Button = view.pack_button(
            view.window, text="Show initial structure",
            command=view.show_init_structure,
        )

        # Button to show initial structure
        view.one_channel_structure_btn: Button = view.pack_button(
            view.window, text="Show one channel",
            command=view.show_one_channel_structure,
            pady=(10, 25),
        )
