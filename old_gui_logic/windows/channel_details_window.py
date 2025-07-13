import pandas as pd
from ..viewmodels import VMShowInitData
from ..components import Button, CheckBox, Table
from .windows_template import WindowsTemplate


class ChannelDetailsWindow(WindowsTemplate):
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
        self.create_window(
            title=f"Show channel parameters ({self.structure_dir})",
        )
        self.create_ui()

    def create_ui(self) -> None:
        # Checkbox for to_show_plane_lengths
        self.to_show_plane_lengths_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Show plane lengths",
            command=self.update_to_show_plane_lengths,
            default=self.view_model.to_show_plane_lengths,
        )

        # Checkbox for to_show_channel_angles
        self.to_show_channel_angles_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Show channel angles",
            command=self.update_to_show_channel_angles,
            default=self.view_model.to_show_channel_angles,
        )

        # Checkbox for to_show_dists_to_plane
        self.to_show_dists_to_plane_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Show distances to plane",
            command=self.update_to_show_dists_to_plane,
            default=self.view_model.to_show_dists_to_plane,
        )

        # Checkbox for to_show_dists_to_edges
        self.to_show_dists_to_edges_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Show distances to edges",
            command=self.update_to_show_dists_to_edges,
            default=self.view_model.to_show_dists_to_edges,
        )

        # Checkbox for to_show_coordinates
        self.to_show_coordinates_checkbox: CheckBox = self.pack_check_box(
            self.window, text="Show coordinates",
            command=self.update_to_show_coordinates,
            default=self.view_model.to_show_coordinates,
        )

        # Button to proceed to the next step
        self.show_2d_channel_scheme_btn: Button = self.pack_button(
            self.window, text="Show 2D channel scheme",
            command=self.show_2d_channel_scheme,
        )

        self.get_channel_params_btn: Button = self.pack_button(
            self.window, text="Get channel parameters",
            command=self.get_channel_params,
            pady=(10, 25),
        )

    def show_2d_channel_scheme(self) -> None:
        self.view_model.show_2d_channel_scheme(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )
        # self.show_plot_window()

    def get_channel_params(self) -> None:
        ChannelParamsWindow(
            view_model=self.view_model,
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )

    def update_to_show_plane_lengths(self) -> None:
        value = bool(self.to_show_plane_lengths_checkbox.get())
        self.view_model.set_to_show_plane_lengths(value)

    def update_to_show_coordinates(self) -> None:
        value = bool(self.to_show_coordinates_checkbox.get())
        self.view_model.set_to_show_coordinates(value)

    def update_to_show_dists_to_plane(self) -> None:
        value = bool(self.to_show_dists_to_plane_checkbox.get())
        self.view_model.set_to_show_dists_to_plane(value)

    def update_to_show_dists_to_edges(self) -> None:
        value = bool(self.to_show_dists_to_edges_checkbox.get())
        self.view_model.set_to_show_dists_to_edges(value)

    def update_to_show_channel_angles(self) -> None:
        value = bool(self.to_show_channel_angles_checkbox.get())
        self.view_model.set_to_show_channel_angles(value)

    # def show_plot_window(self) -> None:
    #     plot_window: PlotWindow = PlotWindow(self.window, title="Channel Details")
    #     plot_window.destroy()


class ChannelParamsWindow(WindowsTemplate):
    def __init__(self, view_model: VMShowInitData, project_dir: str, subproject_dir: str, structure_dir: str) -> None:
        super().__init__()
        self.view_model: VMShowInitData = view_model
        self.project_dir: str = project_dir
        self.subproject_dir: str = subproject_dir
        self.structure_dir: str = structure_dir
        self.create_window(
            title=f"Channel parameters for {self.subproject_dir.title()}",
            geometry=(500, 100),
        )
        self.create_ui()

    def create_ui(self) -> None:
        df: pd.DataFrame = self.view_model.get_channel_params(
            project_dir=self.project_dir,
            subproject_dir=self.subproject_dir,
            structure_dir=self.structure_dir,
        )
        self.table_window: Table = self.pack_table(
            self.window,
            # title=f"Channel parameters for {self.subproject_dir.title()}",
            df=df,
        )
