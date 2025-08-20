import customtkinter as ctk
import tkinter as tk
from typing import Callable, Any
import numpy as np
from numpy.typing import NDArray
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # type: ignore

from src.interfaces import (
    IStructureVisualParams,
    IPlotWindow,
    IPlotControls,
    IShowInitDataView,
    IIntercalationAndSorptionView,
    PCoordinateLimits,
)
from src.entities.params.plot_params import PlotParams
from src.services.utils.logger import Logger
from src.ui.styles import SPACING
from src.services import StructureVisualizer


logger = Logger("PlotWindow")
controls_logger = Logger("PlotControls")


class PlotControls(ctk.CTkFrame, IPlotControls):
    """Plot customization controls sidebar."""

    def __init__(self, master: ctk.CTkFrame, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._params_changed_callback: Callable[[PlotParams], None] | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the control panel UI."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Plot Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(SPACING.md, SPACING.sm))

        # Visualization options frame
        viz_frame = ctk.CTkFrame(self)
        viz_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.sm)

        ctk.CTkLabel(viz_frame, text="Visualization", font=ctk.CTkFont(weight="bold")).pack(pady=SPACING.sm)

        # Checkboxes for visualization options
        # Use default values from PlotParams
        self._default_params = PlotParams()
        self.bonds_var = ctk.BooleanVar(value=self._default_params.to_build_bonds)
        self.coords_var = ctk.BooleanVar(value=self._default_params.to_show_coordinates)
        self.indexes_var = ctk.BooleanVar(value=self._default_params.to_show_indexes)
        self.equal_scale_var = ctk.BooleanVar(value=self._default_params.to_set_equal_scale)
        # self.interactive_var = ctk.BooleanVar(value=self._default_params.is_interactive_mode)
        self.additional_lines_var = ctk.BooleanVar(value=self._default_params.to_build_edge_vertical_lines)
        self.grid_var = ctk.BooleanVar(value=self._default_params.to_show_grid)
        self.edge_lines_var = ctk.BooleanVar(value=self._default_params.to_build_edge_vertical_lines)
        self.legend_var = ctk.BooleanVar(value=self._default_params.to_show_legend)

        ctk.CTkCheckBox(viz_frame, text="Show Bonds", variable=self.bonds_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        ctk.CTkCheckBox(viz_frame, text="Show Coordinates", variable=self.coords_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        ctk.CTkCheckBox(viz_frame, text="Show Indexes", variable=self.indexes_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        ctk.CTkCheckBox(viz_frame, text="Show Grid", variable=self.grid_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        ctk.CTkCheckBox(viz_frame, text="Build Edge Vertical Lines", variable=self.edge_lines_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        ctk.CTkCheckBox(viz_frame, text="Show Legend", variable=self.legend_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        ctk.CTkCheckBox(viz_frame, text="Equal Scale", variable=self.equal_scale_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        # ctk.CTkCheckBox(viz_frame, text="Interactive Mode", variable=self.interactive_var,
        #                 command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        ctk.CTkCheckBox(viz_frame, text="Additional Lines", variable=self.additional_lines_var,
                        command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)

        # Bond settings frame
        bonds_frame = ctk.CTkFrame(self)
        bonds_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.sm)

        ctk.CTkLabel(bonds_frame, text="Bond Settings", font=ctk.CTkFont(weight="bold")).pack(pady=SPACING.sm)

        # Min distances
        ctk.CTkLabel(bonds_frame, text="Min Distances:").pack(anchor="w", padx=SPACING.sm)
        self.min_distances_spinbox = ctk.CTkEntry(bonds_frame, width=80)
        self.min_distances_spinbox.insert(0, str(self._default_params.num_of_min_distances))
        self.min_distances_spinbox.pack(anchor="w", padx=SPACING.sm)
        self.min_distances_spinbox.bind("<KeyRelease>", self._on_bond_settings_changed)
        self.min_distances_spinbox.bind("<FocusOut>", self._on_bond_settings_changed)

        # Skip distances
        ctk.CTkLabel(bonds_frame, text="Skip First Distances:").pack(anchor="w", padx=SPACING.sm)
        self.skip_distances_spinbox = ctk.CTkEntry(bonds_frame, width=80)
        self.skip_distances_spinbox.insert(0, str(self._default_params.skip_first_distances))
        self.skip_distances_spinbox.pack(anchor="w", padx=SPACING.sm)
        self.skip_distances_spinbox.bind("<KeyRelease>", self._on_bond_settings_changed)
        self.skip_distances_spinbox.bind("<FocusOut>", self._on_bond_settings_changed)

        # Coordinate limits frame
        limits_frame = ctk.CTkFrame(self)
        limits_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.sm)

        ctk.CTkLabel(limits_frame, text="Coordinate Limits", font=ctk.CTkFont(weight="bold")).pack(pady=SPACING.sm)

        # X limits
        x_frame = ctk.CTkFrame(limits_frame)
        x_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.xs)
        ctk.CTkLabel(x_frame, text="X:").pack(side="left")
        self.x_min_var = ctk.StringVar(value="-inf")
        self.x_max_var = ctk.StringVar(value="inf")
        self.x_min_entry = ctk.CTkEntry(x_frame, textvariable=self.x_min_var, width=60)
        self.x_min_entry.pack(side="left", padx=SPACING.xs)
        ctk.CTkLabel(x_frame, text="to").pack(side="left", padx=SPACING.xs)
        self.x_max_entry = ctk.CTkEntry(x_frame, textvariable=self.x_max_var, width=60)
        self.x_max_entry.pack(side="left", padx=SPACING.xs)

        # Y limits
        y_frame = ctk.CTkFrame(limits_frame)
        y_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.xs)
        ctk.CTkLabel(y_frame, text="Y:").pack(side="left")
        self.y_min_var = ctk.StringVar(value="-inf")
        self.y_max_var = ctk.StringVar(value="inf")
        self.y_min_entry = ctk.CTkEntry(y_frame, textvariable=self.y_min_var, width=60)
        self.y_min_entry.pack(side="left", padx=SPACING.xs)
        ctk.CTkLabel(y_frame, text="to").pack(side="left", padx=SPACING.xs)
        self.y_max_entry = ctk.CTkEntry(y_frame, textvariable=self.y_max_var, width=60)
        self.y_max_entry.pack(side="left", padx=SPACING.xs)

        # Z limits
        z_frame = ctk.CTkFrame(limits_frame)
        z_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.xs)
        ctk.CTkLabel(z_frame, text="Z:").pack(side="left")
        self.z_min_var = ctk.StringVar(value="-inf")
        self.z_max_var = ctk.StringVar(value="inf")
        self.z_min_entry = ctk.CTkEntry(z_frame, textvariable=self.z_min_var, width=60)
        self.z_min_entry.pack(side="left", padx=SPACING.xs)
        ctk.CTkLabel(z_frame, text="to").pack(side="left", padx=SPACING.xs)
        self.z_max_entry = ctk.CTkEntry(z_frame, textvariable=self.z_max_var, width=60)
        self.z_max_entry.pack(side="left", padx=SPACING.xs)

        # Bind coordinate limit events
        for entry in [self.x_min_entry, self.x_max_entry, self.y_min_entry, self.y_max_entry, self.z_min_entry, self.z_max_entry]:
            entry.bind("<KeyRelease>", self._on_coordinate_changed)
            entry.bind("<FocusOut>", self._on_coordinate_changed)

        # Inter atom layers frame
        inter_frame = ctk.CTkFrame(self)
        inter_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.sm)

        ctk.CTkLabel(inter_frame, text="Inter Atom Settings", font=ctk.CTkFont(weight="bold")).pack(pady=SPACING.sm)

        # Number of inter atom layers
        ctk.CTkLabel(inter_frame, text="Number of Inter Atom Layers:").pack(anchor="w", padx=SPACING.sm)
        self.inter_layers_spinbox = ctk.CTkEntry(inter_frame, width=80)
        self.inter_layers_spinbox.insert(0, str(self._default_params.num_of_inter_atoms_layers))
        self.inter_layers_spinbox.pack(anchor="w", padx=SPACING.sm)
        self.inter_layers_spinbox.bind("<KeyRelease>", self._on_inter_settings_changed)
        self.inter_layers_spinbox.bind("<FocusOut>", self._on_inter_settings_changed)

        # # Channel Analysis frame
        # channel_frame = ctk.CTkFrame(self)
        # channel_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.sm)

        # ctk.CTkLabel(channel_frame, text="Channel Analysis", font=ctk.CTkFont(weight="bold")).pack(pady=SPACING.sm)

        # # Channel analysis checkboxes
        # self.show_dists_to_plane_var = ctk.BooleanVar(value=False)
        # self.show_dists_to_edges_var = ctk.BooleanVar(value=False)
        # self.show_channel_angles_var = ctk.BooleanVar(value=False)
        # self.show_plane_lengths_var = ctk.BooleanVar(value=False)

        # ctk.CTkCheckBox(channel_frame, text="Show distances to plane", variable=self.show_dists_to_plane_var,
        #                 command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        # ctk.CTkCheckBox(channel_frame, text="Show distances to edges", variable=self.show_dists_to_edges_var,
        #                 command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        # ctk.CTkCheckBox(channel_frame, text="Show channel angles", variable=self.show_channel_angles_var,
        #                 command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)
        # ctk.CTkCheckBox(channel_frame, text="Show plane lengths", variable=self.show_plane_lengths_var,
        #                 command=self._on_params_changed).pack(anchor="w", padx=SPACING.sm)

        # Action buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=SPACING.sm, pady=SPACING.md)

        refresh_btn = ctk.CTkButton(button_frame, text="Refresh Plot", command=self._on_params_changed)
        refresh_btn.pack(fill="x", pady=SPACING.xs)

    def _on_params_changed(self) -> None:
        """Handle parameter changes."""
        if self._params_changed_callback:
            params: PlotParams = self.load_params_from_ui()
            controls_logger.info(f"UI params changed: x=[{params.x_min}, {params.x_max}], "
                                 f"y=[{params.y_min}, {params.y_max}], z=[{params.z_min}, {params.z_max}], "
                                 f"bonds=[{params.num_of_min_distances}, {params.skip_first_distances}], "
                                 f"inter_layers={params.num_of_inter_atoms_layers}")
            self._params_changed_callback(params)

    def _on_coordinate_changed(self, event=None) -> None:
        """Handle coordinate limit changes."""
        self._on_params_changed()

    def _on_bond_settings_changed(self, event=None) -> None:
        """Handle bond settings changes."""
        self._on_params_changed()

    def _on_inter_settings_changed(self, event=None) -> None:
        """Handle inter atom settings changes."""
        self._on_params_changed()

    def _parse_float(self, value: str, default: float) -> float:
        """Parse float value, handling 'inf' and invalid inputs."""
        controls_logger.debug(f"_parse_float: parsing '{value}' (type: {type(value)}) with default {default}")

        if not value or value.strip() == "":
            controls_logger.debug(f"_parse_float: empty value, returning default {default}")
            return default
        elif value.lower() in ['inf', '+inf']:
            controls_logger.debug(f"_parse_float: positive infinity")
            return float('inf')
        elif value.lower() == '-inf':
            controls_logger.debug(f"_parse_float: negative infinity")
            return -float('inf')
        else:
            try:
                result = float(value)
                controls_logger.debug(f"_parse_float: successfully parsed '{value}' as {result}")
                return result
            except ValueError:
                controls_logger.debug(f"_parse_float: failed to parse '{value}', returning default {default}")
                return default

    def set_on_params_changed_callback(self, callback: Callable[[PlotParams], None]) -> None:
        """Set callback to be called when plot parameters change."""
        self._params_changed_callback = callback

    def load_params_from_ui(self) -> PlotParams:
        """Load plot parameters from UI controls."""
        try:
            num_min_distances = int(self.min_distances_spinbox.get())
        except (ValueError, tk.TclError):
            num_min_distances = 2

        try:
            skip_distances = int(self.skip_distances_spinbox.get())
        except (ValueError, tk.TclError):
            skip_distances = 0

        try:
            inter_layers = int(self.inter_layers_spinbox.get())
        except (ValueError, tk.TclError):
            inter_layers = 2

        # Parse coordinate limits - debug raw UI values
        x_min_raw: str = self.x_min_entry.get()
        x_max_raw: str = self.x_max_entry.get()
        y_min_raw: str = self.y_min_entry.get()
        y_max_raw: str = self.y_max_entry.get()
        z_min_raw: str = self.z_min_entry.get()
        z_max_raw: str = self.z_max_entry.get()

        controls_logger.info(
            f"Raw UI values: x_min='{x_min_raw}', x_max='{x_max_raw}', y_min='{y_min_raw}', y_max='{y_max_raw}', z_min='{z_min_raw}', z_max='{z_max_raw}'")

        x_min: float = self._parse_float(x_min_raw, -float('inf'))
        x_max: float = self._parse_float(x_max_raw, float('inf'))
        y_min: float = self._parse_float(y_min_raw, -float('inf'))
        y_max: float = self._parse_float(y_max_raw, float('inf'))
        z_min: float = self._parse_float(z_min_raw, -float('inf'))
        z_max: float = self._parse_float(z_max_raw, float('inf'))

        controls_logger.info(
            f"Parsed coordinates: x=[{x_min}, {x_max}], y=[{y_min}, {y_max}], z=[{z_min}, {z_max}], inter_layers={inter_layers}")

        return PlotParams(
            to_build_bonds=self.bonds_var.get(),
            to_show_coordinates=self.coords_var.get(),
            to_show_indexes=self.indexes_var.get(),
            to_set_equal_scale=self.equal_scale_var.get(),
            # is_interactive_mode=self.interactive_var.get(),
            to_build_edge_vertical_lines=self.edge_lines_var.get(),
            to_show_grid=self.grid_var.get(),
            to_show_legend=self.legend_var.get(),
            num_of_inter_atoms_layers=inter_layers,
            # to_show_dists_to_plane=self.show_dists_to_plane_var.get(),
            # to_show_dists_to_edges=self.show_dists_to_edges_var.get(),
            # to_show_channel_angles=self.show_channel_angles_var.get(),
            # to_show_plane_lengths=self.show_plane_lengths_var.get(),
            num_of_min_distances=num_min_distances,
            skip_first_distances=skip_distances,
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            z_min=z_min,
            z_max=z_max,
        )

    def load_ui_from_params(self, params: PlotParams) -> None:
        """Load UI controls from plot parameters."""
        self.bonds_var.set(params.to_build_bonds)
        self.coords_var.set(params.to_show_coordinates)
        self.indexes_var.set(params.to_show_indexes)
        self.equal_scale_var.set(params.to_set_equal_scale)
        # self.interactive_var.set(params.is_interactive_mode)
        self.additional_lines_var.set(params.to_build_edge_vertical_lines)
        self.grid_var.set(params.to_show_grid)
        self.edge_lines_var.set(params.to_build_edge_vertical_lines)
        self.legend_var.set(params.to_show_legend)
        # self.show_dists_to_plane_var.set(params.to_show_dists_to_plane)
        # self.show_dists_to_edges_var.set(params.to_show_dists_to_edges)
        # self.show_channel_angles_var.set(params.to_show_channel_angles)
        # self.show_plane_lengths_var.set(params.to_show_plane_lengths)
        self.min_distances_spinbox.delete(0, 'end')
        self.min_distances_spinbox.insert(0, str(params.num_of_min_distances))
        self.skip_distances_spinbox.delete(0, 'end')
        self.skip_distances_spinbox.insert(0, str(params.skip_first_distances))
        self.inter_layers_spinbox.delete(0, 'end')
        self.inter_layers_spinbox.insert(0, str(params.num_of_inter_atoms_layers))

        # Handle infinite values for display
        inf = float('inf')
        self.x_min_var.set("-inf" if params.x_min == -inf else str(params.x_min))
        self.x_max_var.set("inf" if params.x_max == inf else str(params.x_max))
        self.y_min_var.set("-inf" if params.y_min == -inf else str(params.y_min))
        self.y_max_var.set("inf" if params.y_max == inf else str(params.y_max))
        self.z_min_var.set("-inf" if params.z_min == -inf else str(params.z_min))
        self.z_max_var.set("inf" if params.z_max == inf else str(params.z_max))


class PlotWindow(ctk.CTkToplevel, IPlotWindow):
    """Enhanced plot window with structure visualization and customization controls."""

    def __init__(
            self,
            master: ctk.CTk | ctk.CTkToplevel | IShowInitDataView | IIntercalationAndSorptionView | None = None,
            title: str = "Structure Plot",
            plot_params: PlotParams | None = None,
            on_params_changed_callback: Callable[[PlotParams], None] | None = None,
            **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("1400x900")

        # Initialize plot parameters
        self._plot_params = plot_params or PlotParams(title=title)
        self._current_data: dict[str, Any] = {}
        self._last_camera_state: dict[str, float] = {}
        self._on_params_changed_callback = on_params_changed_callback

        self._setup_ui()
        self._setup_plot()

        # Load initial parameters into controls
        self.controls.load_ui_from_params(self._plot_params)

    def _setup_ui(self) -> None:
        """Setup the main UI layout."""
        # Create main container - use regular frame since we're not using ScrollableToplevel
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=SPACING.sm, pady=SPACING.sm)

        # Create horizontal layout
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)

        # Controls sidebar (left)
        self.controls = PlotControls(content_frame, width=280)
        self.controls.pack(side="left", fill="y", padx=(0, SPACING.sm))
        self.controls.set_on_params_changed_callback(self._on_params_changed)

        # Plot area (right)
        self.plot_frame = ctk.CTkFrame(content_frame)
        self.plot_frame.pack(side="right", fill="both", expand=True)

    def _setup_plot(self) -> None:
        """Setup the matplotlib plot area."""
        # Add toolbar frame first (at top)
        toolbar_frame = ctk.CTkFrame(self.plot_frame)
        toolbar_frame.pack(fill="x", pady=(0, SPACING.sm))

        # Create matplotlib figure
        self.figure = Figure(figsize=self._plot_params.figsize, dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Add toolbar to the frame
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # Initial empty plot
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')  # type: ignore
        self.ax.set_title(self._plot_params.title)
        self.canvas.draw()

    def _on_params_changed(self, params: PlotParams) -> None:
        """Handle parameter changes from controls."""
        logger.info(f"PlotWindow updating: x=[{params.x_min}, {params.x_max}], "
                    f"y=[{params.y_min}, {params.y_max}], z=[{params.z_min}, {params.z_max}], "
                    f"bonds=[{params.num_of_min_distances}, {params.skip_first_distances}]")

        self._plot_params = params

        # Notify external callback if set (for MVP parameter synchronization)
        if self._on_params_changed_callback:
            logger.info("Syncing to MVP parameters")
            self._on_params_changed_callback(params)
        else:
            logger.warning("No MVP sync callback available")

        self.refresh_plot()

    def show_structure(
        self,
        coordinates: NDArray[np.float64],
        structure_visual_params: IStructureVisualParams,
        label: str | None = None,
    ) -> None:
        """Display a single structure in the plot window."""
        self._current_data = {
            'type': 'single',
            'coordinates': coordinates,
            'structure_visual_params': structure_visual_params,
            'label': label,
        }
        self._render_plot()

    def show_structures(
        self,
        coordinates_list: list[NDArray[np.float64]],
        structure_visual_params_list: list[IStructureVisualParams],
        labels_list: list[str | None],
    ) -> None:
        """Display multiple structures in the plot window."""
        self._current_data = {
            'type': 'multiple',
            'coordinates_list': coordinates_list,
            'structure_visual_params_list': structure_visual_params_list,
            'labels_list': labels_list,
        }
        self._render_plot()

    def _render_plot(self) -> None:
        """Render the plot based on current data and parameters."""
        if not self._current_data:
            return

        # Save current camera state
        self.save_plot_state()

        # Clear the current plot
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')

        data_type = self._current_data['type']
        # Always pass coordinate limits - let StructureVisualizer handle infinite values
        coordinate_limits: PCoordinateLimits = self._plot_params.coordinate_limits

        try:
            if data_type == 'single':
                StructureVisualizer._plot_atoms_3d(
                    fig=self.figure,
                    ax=self.ax,
                    coordinates=self._current_data['coordinates'],
                    structure_visual_params=self._current_data['structure_visual_params'],
                    label=self._current_data['label'],
                    to_build_bonds=self._plot_params.to_build_bonds,
                    to_set_equal_scale=self._plot_params.to_set_equal_scale,
                    to_show_coordinates=self._plot_params.to_show_coordinates,
                    to_show_indexes=self._plot_params.to_show_indexes,
                    to_show_grid=self._plot_params.to_show_grid,
                    num_of_min_distances=self._plot_params.num_of_min_distances,
                    skip_first_distances=self._plot_params.skip_first_distances,
                    is_interactive_mode=self._plot_params.is_interactive_mode,
                    coordinate_limits=coordinate_limits,
                    to_build_edge_vertical_lines=self._plot_params.to_build_edge_vertical_lines,
                    to_show_dists_to_plane=self._plot_params.to_show_dists_to_plane,
                    to_show_dists_to_edges=self._plot_params.to_show_dists_to_edges,
                    to_show_channel_angles=self._plot_params.to_show_channel_angles,
                    to_show_plane_lengths=self._plot_params.to_show_plane_lengths,
                )

            elif data_type == 'multiple':
                coordinates_list: list[NDArray[np.float64]] = self._current_data['coordinates_list']
                structure_visual_params_list: list[IStructureVisualParams] = (
                    self._current_data['structure_visual_params_list'][:len(coordinates_list)]
                )
                labels_list: list[str | None] = self._current_data['labels_list']

                for i, (coordinates, visual_params, label) in enumerate(
                        zip(coordinates_list, structure_visual_params_list, labels_list)):

                    to_show_grid: bool | None = (
                        self._plot_params.to_show_grid if i == len(coordinates_list) - 1 else None
                    )

                    StructureVisualizer._plot_atoms_3d(
                        fig=self.figure,
                        ax=self.ax,
                        coordinates=coordinates,
                        structure_visual_params=visual_params,
                        label=label,
                        to_build_bonds=self._plot_params.to_build_bonds if i == 0 else False,
                        to_set_equal_scale=self._plot_params.to_set_equal_scale if i == 0 else False,
                        to_show_coordinates=self._plot_params.to_show_coordinates,
                        to_show_indexes=self._plot_params.to_show_indexes,
                        to_show_grid=to_show_grid,
                        num_of_min_distances=self._plot_params.num_of_min_distances,
                        skip_first_distances=self._plot_params.skip_first_distances,
                        is_interactive_mode=self._plot_params.is_interactive_mode if label != "Carbon" else False,
                        coordinate_limits=coordinate_limits,
                        to_build_edge_vertical_lines=self._plot_params.to_build_edge_vertical_lines,
                        to_show_dists_to_plane=self._plot_params.to_show_dists_to_plane,
                        to_show_dists_to_edges=self._plot_params.to_show_dists_to_edges,
                        to_show_channel_angles=self._plot_params.to_show_channel_angles,
                        to_show_plane_lengths=self._plot_params.to_show_plane_lengths,
                    )

            # Set labels and title
            self.ax.set_xlabel('X')
            self.ax.set_ylabel('Y')
            self.ax.set_zlabel('Z')  # type: ignore
            self.ax.set_title(self._plot_params.title)

            # Add legend if enabled and there are multiple structures or labels
            if self._plot_params.to_show_legend and data_type in ['multiple']:
                self.ax.legend(labelspacing=1.1)

            # Restore camera state
            self.restore_plot_state()

            # Refresh the canvas
            self.canvas.draw()

        except Exception as e:
            logger.error(f"Error rendering plot: {e}")
            # Show error in plot
            self.ax.text(0.5, 0.5, 0.5, f"Error: {str(e)}", ha="center", va="center")  # type: ignore
            self.canvas.draw()

    def refresh_plot(self) -> None:
        """Refresh the plot with current parameters while maintaining camera position."""
        self._render_plot()

    def get_plot_params(self) -> PlotParams:
        """Get current plot parameters."""
        return self._plot_params.copy()

    def set_plot_params(self, params: PlotParams) -> None:
        """Set plot parameters and refresh display."""
        self._plot_params: PlotParams = params
        self.controls.load_ui_from_params(params)
        self.refresh_plot()

    def save_plot_state(self) -> None:
        """Save current plot state (camera position, scale, etc.)."""
        try:
            self._last_camera_state = {  # type: ignore
                'elevation': self.ax.elev,  # type: ignore
                'azimuth': self.ax.azim,  # type: ignore
                'xlim': self.ax.get_xlim(),
                'ylim': self.ax.get_ylim(),
                'zlim': self.ax.get_zlim(),  # type: ignore
            }
            # Update plot params with camera state
            self._plot_params.camera_elevation = self.ax.elev  # type: ignore
            self._plot_params.camera_azimuth = self.ax.azim  # type: ignore
        except Exception as e:
            logger.warning(f"Could not save plot state: {e}")

    def restore_plot_state(self) -> None:
        """Restore saved plot state."""
        try:
            if self._last_camera_state:
                self.ax.view_init(  # type: ignore
                    elev=self._last_camera_state['elevation'],
                    azim=self._last_camera_state['azimuth']
                )
                # Only restore limits if auto_scale_to_data is False
                # When auto_scale_to_data is True, always fit to current data
                if not self._plot_params.auto_scale_to_data and 'xlim' in self._last_camera_state:
                    self.ax.set_xlim(self._last_camera_state['xlim'])
                    self.ax.set_ylim(self._last_camera_state['ylim'])
                    self.ax.set_zlim(self._last_camera_state['zlim'])  # type: ignore
            else:
                # Use parameters if no saved state
                self.ax.view_init(  # type: ignore
                    elev=self._plot_params.camera_elevation,
                    azim=self._plot_params.camera_azimuth
                )
        except Exception as e:
            logger.warning(f"Could not restore plot state: {e}")
