"""Tests for read-only two-panel intercalated-channel schemes."""

from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, cast

from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import pytest

from src.entities import IntercalatedChannelSchemeData, Points
from src.interfaces import (
    ICarbonHoneycombChannel,
    IIntercalationAndSorptionModel,
    IIntercalationAndSorptionView,
)
from src.mvp.intercalation_and_sorption.intercalation_and_sorption_presenter import (
    IntercalationAndSorptionPresenter,
)
from src.projects.intercalation_and_sorption import (
    InterAtomsFileManager,
    InterAtomsParser,
    IntercalatedChannelSchemeBuilder,
)
from src.services import ATOM_PARAMS_MAP, Constants, IntercalatedChannelSchemeRenderer


def _build_abab_data(
    synthetic_channel: ICarbonHoneycombChannel,
) -> IntercalatedChannelSchemeData:
    """Build a simple ABAB fixture with a periodic seam neighbour."""
    atoms = Points(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [5.0, 0.0, 2.0],
                [0.0, 0.0, 4.0],
                [5.0, 0.0, 6.0],
            ],
            dtype=np.float64,
        ),
        atom_ids=("a", "b", "a-next", "b-next"),
    )
    return IntercalatedChannelSchemeBuilder().build(
        synthetic_channel,
        atoms,
        ATOM_PARAMS_MAP["ar"],
        "one_ch-ABAB-v1-Test.csv",
    )


def test_builder_preserves_indexes_and_detects_geometry_repeat(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Use file-order indexes while detecting the shortest repeated layer pattern."""
    original = np.array(
        [
            [5.0, 0.0, 2.0],
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 6.0],
            [0.0, 0.0, 4.0],
        ],
        dtype=np.float64,
    )
    atoms = Points(points=original.copy(), atom_ids=("b", "a", "b-next", "a-next"))

    data = IntercalatedChannelSchemeBuilder().build(
        synthetic_channel,
        atoms,
        ATOM_PARAMS_MAP["ar"],
        "one_ch-ABAB-v1-Test.csv",
    )

    assert data.periodicity_source == "geometry-confirmed"
    assert data.stacking_type == "ABAB"
    assert data.repeat_length == pytest.approx(4.0)
    assert data.representative_indexes == (1, 0)
    assert tuple(atom.source_index for atom in data.atoms) == (0, 1, 2, 3)
    assert tuple(atom.atom_id for atom in data.atoms) == ("b", "a", "b-next", "a-next")
    np.testing.assert_array_equal(atoms.points, original)


def test_builder_matches_multi_atom_layers_independently_of_row_order(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Treat each layer as an unordered multiset of xOy positions."""
    atoms = Points(
        points=np.array(
            [
                [-1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 3.0],
                [-1.0, 0.0, 3.0],
            ],
            dtype=np.float64,
        )
    )

    data = IntercalatedChannelSchemeBuilder().build(
        synthetic_channel, atoms, ATOM_PARAMS_MAP["ar"], "model.csv"
    )

    assert data.periodicity_source == "geometry-confirmed"
    assert data.stacking_type == "AA"
    assert data.representative_indexes == (0, 1)


def test_source_indexes_follow_post_parser_rows(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Match table indexes after the shared parser removes an incomplete raw row."""
    raw = pd.DataFrame(
        {
            "atom_id": ["first", "dropped", "second"],
            "x_inter": [0.0, np.nan, 1.0],
            "y_inter": [0.0, 0.0, 0.0],
            "z_inter": [0.0, 1.0, 2.0],
        }
    )
    parsed = InterAtomsParser.parse_inter_atoms_coordinates_df(raw)

    data = IntercalatedChannelSchemeBuilder().build(
        synthetic_channel, parsed, ATOM_PARAMS_MAP["ar"], "model.csv"
    )

    assert tuple(atom.source_index for atom in data.atoms) == (0, 1)
    assert tuple(atom.atom_id for atom in data.atoms) == ("first", "second")


def test_builder_uses_periodic_self_images_for_nearest_inter(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Include neighbours across both boundaries of a reliable repeat cell."""
    data: IntercalatedChannelSchemeData = _build_abab_data(synthetic_channel)
    representative_atoms = [atom for atom in data.atoms if atom.is_representative]

    assert len(representative_atoms) == 2
    assert all(atom.min_distance_to_inter == pytest.approx(4.0) for atom in representative_atoms)
    assert all(abs(atom.nearest_inter_periodic_shift) == 1 for atom in representative_atoms)
    assert all(
        atom.nearest_inter_source_index == atom.source_index
        for atom in representative_atoms
    )


def test_builder_keeps_exact_duplicate_as_zero_distance(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Exclude only the same row, not a distinct row at identical coordinates."""
    atoms = Points(
        points=np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]], dtype=np.float64),
        atom_ids=("duplicate-a", "duplicate-b"),
    )

    data = IntercalatedChannelSchemeBuilder().build(
        synthetic_channel, atoms, ATOM_PARAMS_MAP["ar"], "model.csv"
    )

    assert data.periodicity_source == "unknown"
    assert tuple(atom.min_distance_to_inter for atom in data.atoms) == (0.0, 0.0)
    assert tuple(atom.nearest_inter_source_index for atom in data.atoms) == (1, 0)


def test_builder_handles_single_atom_without_repeat(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Represent a missing finite neighbour as None instead of failing."""
    data = IntercalatedChannelSchemeBuilder().build(
        synthetic_channel,
        Points(points=np.array([[0.0, 0.0, 1.0]], dtype=np.float64)),
        ATOM_PARAMS_MAP["ar"],
        "model.dat",
    )

    assert data.atoms[0].min_distance_to_inter is None
    assert data.atoms[0].nearest_inter_source_index is None


def test_builder_supports_filename_derived_fragment(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Use a single complete named fragment while marking it unverified."""
    atoms = Points(
        points=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 2.0], [2.0, 0.0, 4.0]],
            dtype=np.float64,
        )
    )

    data = IntercalatedChannelSchemeBuilder().build(
        synthetic_channel,
        atoms,
        ATOM_PARAMS_MAP["ar"],
        "one_ch-ABCABC-v1-Test.csv",
    )

    assert data.periodicity_source == "filename-derived"
    assert data.stacking_type == "ABCABC"
    assert data.repeat_length == pytest.approx(6.0)
    assert data.representative_indexes == (0, 1, 2)
    assert data.warnings


def test_builder_prefers_geometry_over_filename_hint(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Report a name conflict while using the actual shortest repeat."""
    atoms = Points(
        points=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 2.0]], dtype=np.float64)
    )

    data = IntercalatedChannelSchemeBuilder().build(
        synthetic_channel,
        atoms,
        ATOM_PARAMS_MAP["ar"],
        "one_ch-ABAB-v1-Test.csv",
    )

    assert data.periodicity_source == "geometry-confirmed"
    assert data.stacking_type == "AA"
    assert data.repeat_length == pytest.approx(2.0)
    assert "conflicts" in data.warnings[0]


def test_builder_calculates_edge_and_boundary_dimensions(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Include vertex levels, nearest vertices, and exact directional boundary gaps."""
    data: IntercalatedChannelSchemeData = _build_abab_data(synthetic_channel)
    representative_atoms = [atom for atom in data.atoms if atom.is_representative]
    coordinate_dimensions = [
        segment for segment in data.dimension_segments if segment.kind == "coordinate_level"
    ]
    boundary_dimensions = [
        segment for segment in data.dimension_segments if segment.kind == "boundary_gap"
    ]

    assert len(data.channel_boundary) == 6
    assert all(atom.distance_to_edge_vertex_xy is not None for atom in representative_atoms)
    assert {segment.orientation for segment in coordinate_dimensions} == {"x", "y"}
    assert {segment.orientation for segment in boundary_dimensions} == {"x", "y"}
    assert all(segment.value > 0.0 for segment in data.dimension_segments)


def test_builder_rejects_non_one_channel_inputs(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Reject all-channel names and projections outside the first channel."""
    inside = Points(points=np.array([[0.0, 0.0, 0.0]], dtype=np.float64))
    outside = Points(points=np.array([[20.0, 0.0, 0.0]], dtype=np.float64))
    builder = IntercalatedChannelSchemeBuilder()

    for file_name in ("all_ch-AA-v1-Test.csv", "final_all_ch-v1-ABAB-Test.dat"):
        with pytest.raises(ValueError, match="All-channel"):
            builder.build(synthetic_channel, inside, ATOM_PARAMS_MAP["ar"], file_name)
    with pytest.raises(ValueError, match="outside row indexes: 0"):
        builder.build(synthetic_channel, outside, ATOM_PARAMS_MAP["ar"], "model.csv")


def test_scheme_data_is_frozen_and_renderer_builds_two_axes(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Keep the DTO immutable and render exactly two readable panels."""
    data: IntercalatedChannelSchemeData = _build_abab_data(synthetic_channel)

    with pytest.raises(FrozenInstanceError):
        data.file_name = "changed.csv"  # type: ignore[misc]

    figure: Figure = IntercalatedChannelSchemeRenderer().render(data)
    all_text: str = " ".join(text.get_text() for axis in figure.axes for text in axis.texts)

    assert len(figure.axes) == 2
    assert all(axis.get_aspect() == 1.0 for axis in figure.axes)
    assert "#0" in all_text
    assert "E_xy=" in all_text
    assert any("ΔX=" in text.get_text() for text in figure.axes[1].texts)
    assert any("ΔY=" in text.get_text() for text in figure.axes[1].texts)
    figure.clear()


@pytest.mark.parametrize("file_format", ["csv", "xlsx", "dat"])
def test_file_manager_reads_supported_scheme_formats(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    file_format: str,
) -> None:
    """Keep CSV-first and legacy XLSX/DAT reads on the shared parser path."""
    monkeypatch.setattr(Constants.path, "PROJECTS_DATA_PATH", tmp_path)
    result_dir = (
        tmp_path / "intercalation_and_sorption" / "ar" / "result_data" / "S"
    )
    result_dir.mkdir(parents=True)
    file_name: str = f"one_ch-AA-v1-Test.{file_format}"
    path: Path = result_dir / file_name
    coordinates = pd.DataFrame(
        {"atom_id": ["a"], "x_inter": [1.0], "y_inter": [2.0], "z_inter": [3.0]}
    )
    if file_format == "csv":
        coordinates.to_csv(path, index=False)
    elif file_format == "xlsx":
        coordinates.to_excel(path, index=False)
    else:
        path.write_text("header\nheader\n1.0 2.0 3.0\n", encoding="utf-8")

    restored = InterAtomsFileManager.read_inter_atoms(
        "intercalation_and_sorption", "ar", "S", file_name
    )

    assert restored.points.tolist() == [[1.0, 2.0, 3.0]]


class _SchemeView:
    """Capture presenter interactions for the new read-only action."""

    def __init__(self) -> None:
        self.callbacks: dict[str, Callable[..., None]] = {}
        self.displayed: tuple[IntercalatedChannelSchemeData, str] | None = None

    def set_operation_callbacks(self, callbacks: dict[str, Callable[..., None]]) -> None:
        self.callbacks = callbacks

    def get_selected_file(self) -> str:
        return "one_ch-AA-v1-Test.csv"

    def display_intercalated_channel_scheme(
        self, data: IntercalatedChannelSchemeData, selected_file: str
    ) -> None:
        self.displayed = data, selected_file


class _SchemeModel:
    """Return prepared data and retain the selected filename."""

    def __init__(self, data: IntercalatedChannelSchemeData) -> None:
        self.params = SimpleNamespace(file_name=None)
        self.data: IntercalatedChannelSchemeData = data

    def get_mvp_params(self) -> Any:
        return self.params

    def set_mvp_params(self, params: Any) -> None:
        self.params = params

    def get_intercalated_channel_scheme_data(
        self, **_kwargs: str
    ) -> IntercalatedChannelSchemeData:
        return self.data


def test_presenter_registers_and_displays_scheme(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Route selected-file state through model and view without writing data."""
    data: IntercalatedChannelSchemeData = _build_abab_data(synthetic_channel)
    view = _SchemeView()
    model = _SchemeModel(data)
    presenter = object.__new__(IntercalationAndSorptionPresenter)
    presenter.view = cast(IIntercalationAndSorptionView, view)
    presenter.model = cast(IIntercalationAndSorptionModel, model)
    presenter._current_context = {
        "project_dir": "intercalation_and_sorption",
        "subproject_dir": "ar",
        "structure_dir": "S",
    }
    completed: list[str] = []
    presenter.on_operation_completed = lambda operation, _result: completed.append(operation)
    presenter.on_operation_failed = lambda operation, error: pytest.fail(f"{operation}: {error}")

    presenter._initialize()
    view.callbacks["show_2d_intercalated_channel_scheme"]()

    assert model.params.file_name == "one_ch-AA-v1-Test.csv"
    assert view.displayed == (data, "one_ch-AA-v1-Test.csv")
    assert completed == ["show_2d_intercalated_channel_scheme"]
