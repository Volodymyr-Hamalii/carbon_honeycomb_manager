from abc import ABC, abstractmethod
from typing import Callable, Any
import numpy as np
from numpy.typing import NDArray

from src.entities.params.plot_params import PlotParams
from ...services import IStructureVisualParams


class IPlotWindow(ABC):
    """Interface for the enhanced plot window with structure visualization."""
    
    @abstractmethod
    def show_structure(
        self,
        coordinates: NDArray[np.float64],
        structure_visual_params: IStructureVisualParams,
        label: str | None = None,
    ) -> None:
        """Display a single structure in the plot window."""
        ...
    
    @abstractmethod
    def show_two_structures(
        self,
        coordinates_first: NDArray[np.float64],
        coordinates_second: NDArray[np.float64],
        structure_visual_params_first: IStructureVisualParams,
        structure_visual_params_second: IStructureVisualParams,
        label_first: str | None = None,
        label_second: str | None = None,
    ) -> None:
        """Display two structures in the plot window."""
        ...
    
    @abstractmethod
    def show_structures(
        self,
        coordinates_list: list[NDArray[np.float64]],
        structure_visual_params_list: list[IStructureVisualParams],
        labels_list: list[str | None],
    ) -> None:
        """Display multiple structures in the plot window."""
        ...
    
    @abstractmethod
    def refresh_plot(self) -> None:
        """Refresh the plot with current parameters while maintaining camera position."""
        ...
    
    @abstractmethod
    def get_plot_params(self) -> PlotParams:
        """Get current plot parameters."""
        ...
    
    @abstractmethod
    def set_plot_params(self, params: PlotParams) -> None:
        """Set plot parameters and refresh display."""
        ...
    
    @abstractmethod
    def save_plot_state(self) -> None:
        """Save current plot state (camera position, scale, etc.)."""
        ...
    
    @abstractmethod
    def restore_plot_state(self) -> None:
        """Restore saved plot state."""
        ...


class IPlotControls(ABC):
    """Interface for plot customization controls."""
    
    @abstractmethod
    def set_on_params_changed_callback(self, callback: Callable[[PlotParams], None]) -> None:
        """Set callback to be called when plot parameters change."""
        ...
    
    @abstractmethod
    def load_params_from_ui(self) -> PlotParams:
        """Load plot parameters from UI controls."""
        ...
    
    @abstractmethod
    def load_ui_from_params(self, params: PlotParams) -> None:
        """Load UI controls from plot parameters."""
        ...


class IPlot(ABC):
    """Legacy interface - kept for backward compatibility."""
    pass
