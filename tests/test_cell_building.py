"""Tests for the elementary cell building: Oz cut, cell_params.txt and the cell folder naming."""

from math import acos, degrees
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
import pytest

from src.projects.intercalation_and_sorption.cell_building import (
    CellFolderNamer,
    CellParams,
    CellParamsBuilder,
    CellZCutter,
)


CARBON_PERIOD: float = 2.0


def _carbon(period: float = CARBON_PERIOD, num_of_periods: int = 5) -> NDArray[np.float64]:
    """Two carbon columns with two atoms per period."""
    rows: list[list[float]] = []
    for k in range(num_of_periods):
        for x, y, z_offset in ((0.0, 0.0, 0.0), (0.0, 0.0, 0.7), (1.0, 0.5, 0.3), (1.0, 0.5, 1.2)):
            rows.append([x, y, k * period + z_offset])
    return np.array(rows)


def _inter(spacing: float, num_of_layers: int, stacking: int, z_start: float = 0.5) -> NDArray[np.float64]:
    """One intercalated atom per layer; the xy position cycles with the given stacking length."""
    return np.array([
        [0.3 * (layer % stacking), 0.2, z_start + layer * spacing] for layer in range(num_of_layers)
    ])


class TestCarbonPeriod:
    def test_exact_period_is_not_rounded(self) -> None:
        carbon: NDArray[np.float64] = _carbon(period=2.0003)

        assert CellZCutter.find_exact_carbon_period(carbon) == pytest.approx(2.0003, abs=1e-6)


class TestCheckShift:
    def test_matching_overlap_is_confirmed(self) -> None:
        inter: NDArray[np.float64] = _inter(spacing=1.0, num_of_layers=8, stacking=2)

        assert CellZCutter.check_shift(inter, 2.0) is True

    def test_mismatching_overlap_is_rejected(self) -> None:
        inter: NDArray[np.float64] = _inter(spacing=1.0, num_of_layers=8, stacking=2)

        assert CellZCutter.check_shift(inter, 1.0) is False

    def test_single_atom_overlap_is_confirmed_when_the_file_spans_exactly_one_shift(self) -> None:
        inter: NDArray[np.float64] = _inter(spacing=1.0, num_of_layers=3, stacking=1)

        assert CellZCutter.check_shift(inter, 2.0) is True

    def test_two_layers_one_carbon_period_apart_give_one_period(self) -> None:
        inter: NDArray[np.float64] = np.array([[1.0, 1.0, 3.6], [1.0, 1.0, 7.92]])

        assert CellZCutter.find_num_of_periods(inter, 4.32) == 1

    def test_no_overlap_cannot_be_checked(self) -> None:
        inter: NDArray[np.float64] = _inter(spacing=1.0, num_of_layers=3, stacking=1)

        assert CellZCutter.check_shift(inter, 10.0) is None


class TestBuildCell:
    def test_one_carbon_period_when_inter_repeats_with_it(self) -> None:
        carbon: NDArray[np.float64] = _carbon()
        inter: NDArray[np.float64] = _inter(spacing=1.0, num_of_layers=9, stacking=2)

        result = CellZCutter.build_cell(carbon, carbon, inter)

        assert result.num_of_periods == 1
        assert result.cell_height == pytest.approx(CARBON_PERIOD)
        assert result.verified is True
        assert len(result.carbon) == 4
        assert len(result.intercalated) == 2

    def test_height_is_a_multiple_of_the_carbon_period(self) -> None:
        # Layers every 1.5 with an AB stacking repeat after 3.0; together with carbon (2.0) that is 6.0.
        carbon: NDArray[np.float64] = _carbon(num_of_periods=8)
        inter: NDArray[np.float64] = _inter(spacing=1.5, num_of_layers=11, stacking=2)

        result = CellZCutter.build_cell(carbon, carbon, inter)

        assert result.num_of_periods == 3
        assert result.cell_height == pytest.approx(6.0)
        assert result.verified is True
        assert len(result.carbon) == 12
        assert len(result.intercalated) == 4

    def test_carbon_is_built_beyond_the_height_of_the_initial_structure(self) -> None:
        carbon: NDArray[np.float64] = _carbon(num_of_periods=3)
        inter: NDArray[np.float64] = _inter(spacing=1.5, num_of_layers=11, stacking=2)

        result = CellZCutter.build_cell(carbon, carbon, inter)

        assert result.cell_height == pytest.approx(6.0)
        assert len(result.carbon) == 12
        assert result.carbon[:, 2].max() == pytest.approx(2 * CARBON_PERIOD + 1.2)

    def test_short_inter_file_falls_back_to_its_height(self) -> None:
        carbon: NDArray[np.float64] = _carbon(num_of_periods=8)
        inter: NDArray[np.float64] = _inter(spacing=1.5, num_of_layers=4, stacking=2)

        result = CellZCutter.build_cell(carbon, carbon, inter)

        assert result.verified is False
        assert result.num_of_periods == 3
        assert len(result.intercalated) == 4

    def test_upper_boundary_copy_is_not_included(self) -> None:
        carbon: NDArray[np.float64] = _carbon()
        carbon[carbon[:, 2] == pytest.approx(0.0)] += 0.0
        inter: NDArray[np.float64] = _inter(spacing=1.0, num_of_layers=9, stacking=2, z_start=0.0)

        result = CellZCutter.build_cell(carbon, carbon, inter)

        assert result.intercalated[:, 2].max() < CARBON_PERIOD
        assert result.carbon[:, 2].max() < CARBON_PERIOD

    def test_inter_atoms_are_not_clipped_by_the_carbon_height(self) -> None:
        carbon: NDArray[np.float64] = _carbon(num_of_periods=2)
        inter: NDArray[np.float64] = _inter(spacing=1.5, num_of_layers=11, stacking=2)

        result = CellZCutter.build_cell(carbon, carbon, inter)

        assert result.cell_height == pytest.approx(6.0)
        assert len(result.intercalated) == 4

    def test_empty_inter_atoms_are_an_error(self) -> None:
        carbon: NDArray[np.float64] = _carbon()

        with pytest.raises(ValueError):
            CellZCutter.build_cell(carbon, carbon, np.empty((0, 3)))


# Regular hexagon channel (A1-like): P1=(0, 0), P2=(3.993, 2.305).
_A_HEXAGON: NDArray[np.float64] = np.array([
    [0.0, 0.0], [2.662, 0.0], [3.993, 2.305], [2.662, 4.61], [0.0, 4.61], [-1.331, 2.305],
])


def _with_z(xy: NDArray[np.float64]) -> NDArray[np.float64]:
    return np.column_stack([xy, np.zeros(len(xy))])


class TestLatticeVector:
    def test_regular_hexagon(self) -> None:
        x_value, y_value = CellParamsBuilder.find_lattice_vector(_with_z(_A_HEXAGON))

        assert x_value == pytest.approx(3.993)
        assert y_value == pytest.approx(2.305)

    def test_bottom_edge_does_not_have_to_start_at_zero(self) -> None:
        # B1-like channel shifted along x: the bottom edge starts at x=-4.32.
        hexagon: NDArray[np.ndarray] = np.array([
            [-4.32, 0.0], [-1.249, 0.0], [2.133, 4.786], [-1.249, 9.571], [-4.32, 9.571], [-7.702, 4.786],
        ])

        x_value, y_value = CellParamsBuilder.find_lattice_vector(_with_z(hexagon))

        assert x_value == pytest.approx(6.453)
        assert y_value == pytest.approx(4.786)

    def test_channel_below_the_axis_gives_a_positive_y(self) -> None:
        # B2-like channel: its bottom edge is at y=-6.043.
        hexagon: NDArray[np.ndarray] = np.array([
            [0.0, -6.043], [5.231, -6.043], [7.366, -3.022], [5.231, 0.0], [0.0, 0.0], [-2.135, -3.022],
        ])

        x_value, y_value = CellParamsBuilder.find_lattice_vector(_with_z(hexagon))

        assert x_value == pytest.approx(7.366)
        assert y_value == pytest.approx(3.021)

    def test_intermediate_vertices_on_the_hull_are_ignored(self) -> None:
        hexagon: NDArray[np.ndarray] = np.vstack([_A_HEXAGON, [[1.331, 0.0], [3.3, 3.5]]])

        x_value, y_value = CellParamsBuilder.find_lattice_vector(_with_z(hexagon))

        assert x_value == pytest.approx(3.993)
        assert y_value == pytest.approx(2.305)


class TestFormatParams:
    def test_hexagonal_lattice_has_no_angles(self) -> None:
        params: CellParams = CellParams(x=3.99266, y=2.305125, c=4.32)

        assert params.is_hexagonal
        assert CellParamsBuilder.format_params(params) == (
            "a=4.61\n"
            "c=4.32\n"
            "\n"
            "Basis:\n"
            "a = (-3.993, 2.305, 0)\n"
            "b = (3.993, 2.305, 0)\n"
            "c = (0, 0, 4.32)\n"
        )

    def test_non_hexagonal_lattice_has_angles_and_equal_sides(self) -> None:
        params: CellParams = CellParams(x=6.453, y=4.786, c=4.988)
        expected_gamma: float = degrees(acos((4.786 ** 2 - 6.453 ** 2) / (4.786 ** 2 + 6.453 ** 2)))

        lines: list[str] = CellParamsBuilder.format_params(params).splitlines()

        assert not params.is_hexagonal
        assert lines[0] == "α=β=90"
        assert float(lines[1].removeprefix("γ=")) == pytest.approx(expected_gamma, abs=1e-3)
        assert float(lines[1].removeprefix("γ=")) > 90
        assert lines[3] == "a=b=8.034"
        assert lines[4] == "c=4.988"
        assert lines[7:] == ["a = (-6.453, 4.786, 0)", "b = (6.453, 4.786, 0)", "c = (0, 0, 4.988)"]

    def test_gamma_is_the_angle_between_the_written_vectors(self) -> None:
        params: CellParams = CellParams(x=10.773, y=4.786, c=4.988)
        a_vector: NDArray[np.float64] = np.array([-params.x, params.y])
        b_vector: NDArray[np.float64] = np.array([params.x, params.y])
        angle: float = degrees(acos(
            float(a_vector @ b_vector) / float(np.linalg.norm(a_vector) * np.linalg.norm(b_vector))
        ))

        assert params.gamma == pytest.approx(angle)

    def test_trailing_zeros_are_stripped(self) -> None:
        assert CellParamsBuilder._format_number(14.18) == "14.18"
        assert CellParamsBuilder._format_number(0.0) == "0"
        assert CellParamsBuilder._format_number(-0.0001) == "0"
        assert CellParamsBuilder._format_number(44.894772) == "44.895"


class TestCellFolderNamer:
    @pytest.mark.parametrize(
        ("file_name", "expected"),
        [
            ("final_one_ch-polygon-ABAB-v3.csv", ("ABAB", 3)),
            ("final_all_ch-polygon-ABCABC-v2-Claude.csv", ("ABCABC", 2)),
            ("final_one_ch-v6-ABC-Codex.csv", ("ABC", 6)),
            ("final_one_ch-v1-AA-transl-Oz.xlsx", ("AA", 1)),
            ("final_all_ch-v2-ABAB-NV.xlsx", ("ABAB", 2)),
            ("final_all_ch-v1.xlsx", (None, 1)),
            ("final_one_ch-v2-Claude.xlsx", (None, 2)),
            ("final_all_ch.csv", (None, None)),
            ("some_folder/final_all_ch-polygon-AA-v1.csv", ("AA", 1)),
        ],
    )
    def test_parse_file_name(self, file_name: str, expected: tuple[str | None, int | None]) -> None:
        assert CellFolderNamer.parse_file_name(file_name) == expected

    @pytest.mark.parametrize(
        ("file_name", "expected"),
        [
            ("final_one_ch-polygon-ABAB-v3.csv", "cell_ABAB_v3"),
            ("final_all_ch-v1.xlsx", "cell_v1"),
            ("final_all_ch-polygon-ABC.csv", "cell_ABC"),
            ("final_all_ch.csv", "cell"),
        ],
    )
    def test_build_base_name(self, file_name: str, expected: str) -> None:
        assert CellFolderNamer.build_base_name(file_name) == expected

    def test_existing_folders_are_never_reused(self, tmp_path: Path) -> None:
        file_name: str = "final_all_ch-polygon-ABAB-v3.csv"
        (tmp_path / "cell_ABAB_v3").mkdir()
        marker: Path = tmp_path / "cell_ABAB_v3" / "keep.txt"
        marker.write_text("keep")

        first: Path = CellFolderNamer.create_unique_dir(tmp_path, file_name)
        second: Path = CellFolderNamer.create_unique_dir(tmp_path, file_name)

        assert first.name == "cell_ABAB_v3_1"
        assert second.name == "cell_ABAB_v3_2"
        assert marker.read_text() == "keep"

    def test_first_folder_has_no_suffix(self, tmp_path: Path) -> None:
        created: Path = CellFolderNamer.create_unique_dir(tmp_path, "final_one_ch-polygon-ABAB-v3.csv")

        assert created.name == "cell_ABAB_v3"
        assert created.is_dir()
