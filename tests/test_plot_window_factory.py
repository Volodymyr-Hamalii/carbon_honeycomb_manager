"""Tests for the default plot parameters chosen by the plot window factory."""

from types import SimpleNamespace
from typing import Any

import pytest

from src.ui.components.plot_window_factory import PlotWindowFactory


def _mvp_params(selection: dict[str, str]) -> Any:
    return SimpleNamespace(
        current_selection=selection,
        bonds_num_of_min_distances=3,
        bonds_skip_first_distances=0,
        to_build_bonds=True,
        to_show_coordinates=False,
        to_show_c_indexes=False,
        x_min=float("-inf"), x_max=float("inf"),
        y_min=float("-inf"), y_max=float("inf"),
        z_min=float("-inf"), z_max=float("inf"),
        file_name="final_all_ch-v1.csv",
        num_of_inter_atoms_layers=2,
    )


@pytest.mark.parametrize(
    ("structure_dir", "expected"),
    [("B1-7_h7", 2), ("b4-7_h7", 2), ("A2-7_h3", 3), ("C2-7_h3", 3)],
)
def test_min_distances_default_depends_on_structure_type(structure_dir: str, expected: int) -> None:
    plot_params = PlotWindowFactory._convert_mvp_to_plot_params(_mvp_params({}), "title", structure_dir)

    assert plot_params.num_of_min_distances == expected


def test_structure_from_the_selection_is_used_when_not_passed_explicitly() -> None:
    plot_params = PlotWindowFactory._convert_mvp_to_plot_params(_mvp_params({"structure_dir": "B3-7_h7"}), "title")

    assert plot_params.num_of_min_distances == 2
