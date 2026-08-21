"""UI presenter contract tests for read-only polygon-site measurements."""

from types import SimpleNamespace
from typing import Any, Callable, cast

import pandas as pd
import pytest

from src.interfaces import IIntercalationAndSorptionModel, IIntercalationAndSorptionView
from src.mvp.intercalation_and_sorption.intercalation_and_sorption_presenter import (
    IntercalationAndSorptionPresenter,
)
from src.projects.intercalation_and_sorption import IntercalationAndSorption


class _FakeView:
    """Capture only the presenter interactions exercised by this operation."""

    def __init__(self) -> None:
        self.callbacks: dict[str, Callable[..., None]] = {}
        self.displayed: tuple[pd.DataFrame, str] | None = None
        self.errors: list[str] = []

    def set_operation_callbacks(self, callbacks: dict[str, Callable[..., None]]) -> None:
        self.callbacks = callbacks

    def get_selected_file(self) -> str:
        return "model.csv"

    def display_polygon_site_distances(
        self, measurements: pd.DataFrame, selected_file: str
    ) -> None:
        self.displayed = measurements, selected_file

    def show_operation_error(self, message: str) -> None:
        self.errors.append(message)


class _FakeModel:
    """Return mutable file-selection parameters to the presenter."""

    def __init__(self) -> None:
        self.params = SimpleNamespace(file_name=None)

    def get_mvp_params(self) -> Any:
        return self.params


def test_polygon_measurement_table_selects_and_formats_ui_columns() -> None:
    """Keep the requested UI fields in order and render measurements to two decimals."""
    row: dict[str, object] = {
        "atom_id": "atom-0001",
        "coordinates": (1.303, 3.27, 1.44),
        "is_near_wall": True,
        "Min distance to plane": 2.763,
        "Min distance to C": 2.883,
        "Min distance to inter": 4.32,
        "actual_normal_distance": 3.269,
        "projection_coordinates": (1.303, 0.0, 1.44),
        "nearest_center_coordinates": (1.303, 0.0, 1.44),
        "nearest_vertex_coordinates": (1.331, 0.0, 1.44),
        "nearest_edge_midpoint_coordinates": None,
        "d_center": 0.004,
        "d_vertex": 0.028,
        "d_edge_midpoint": 1.247,
        "exemption_reason": None,
        "normal_deviation": -0.001,
    }

    table: pd.DataFrame = IntercalationAndSorption._polygon_site_measurements_ui_df([row])

    assert tuple(table.columns) == IntercalationAndSorption.POLYGON_SITE_UI_COLUMNS
    assert table.loc[0, "coordinates"] == "[1.30, 3.27, 1.44]"
    assert table.loc[0, "projection_coordinates"] == "[1.30, 0.00, 1.44]"
    assert table.loc[0, "nearest_edge_midpoint_coordinates"] is None
    assert table.loc[0, "Min distance to plane"] == "2.76"
    assert table.loc[0, "Min distance to C"] == "2.88"
    assert table.loc[0, "Min distance to inter"] == "4.32"
    assert table.loc[0, "actual_normal_distance"] == "3.27"
    assert table.loc[0, "d_center"] == "0.00"
    assert table.loc[0, "d_vertex"] == "0.03"
    assert table.loc[0, "d_edge_midpoint"] == "1.25"


def test_polygon_ui_recovers_reference_walls_from_candidate_atom_ids() -> None:
    """Use source-wall provenance when every atom ID carries a generated wall suffix."""
    assert IntercalationAndSorption._polygon_reference_walls_from_atom_ids(
        ("candidate-center-a-w0", "candidate-edge-b-w4")
    ) == (0, 4)
    assert IntercalationAndSorption._polygon_reference_walls_from_atom_ids(
        ("candidate-center-a-w0", "atom-0002")
    ) is None
    assert IntercalationAndSorption._polygon_reference_walls_from_atom_ids(None) is None


def test_presenter_registers_and_runs_selected_file_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Display the selected file's DataFrame without invoking any write operation."""
    view = _FakeView()
    model = _FakeModel()
    presenter = object.__new__(IntercalationAndSorptionPresenter)
    presenter.view = cast(IIntercalationAndSorptionView, view)
    presenter.model = cast(IIntercalationAndSorptionModel, model)
    presenter._current_context = {
        "project_dir": "project",
        "subproject_dir": "ar",
        "structure_dir": "A1-7_h3",
    }
    completed: list[tuple[str, Any]] = []
    presenter.on_operation_completed = lambda operation_type, result: completed.append(
        (operation_type, result)
    )
    presenter.on_operation_failed = lambda operation_type, error: pytest.fail(
        f"{operation_type}: {error}"
    )
    expected = pd.DataFrame([{"atom_id": "atom-0001", "normal_deviation": 0.0}])
    monkeypatch.setattr(
        IntercalationAndSorption,
        "get_polygon_site_distances",
        lambda **_kwargs: expected,
    )

    presenter._initialize()
    assert "get_polygon_site_distances" in view.callbacks
    view.callbacks["get_polygon_site_distances"]()
    assert model.params.file_name == "model.csv"
    assert view.displayed is not None
    pd.testing.assert_frame_equal(view.displayed[0], expected)
    assert view.displayed[1] == "model.csv"
    assert completed[0][0] == "get_polygon_site_distances"
