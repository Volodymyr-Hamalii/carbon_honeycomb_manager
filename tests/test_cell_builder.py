"""Tests for the cell warnings/file output and the `cut_intercalated_cell` MCP tool."""

from pathlib import Path

import numpy as np
import pytest

from src.entities import Points
from src.mcp_server import server as mcp_server
from src.mcp_server.server import cut_intercalated_cell
from src.projects.intercalation_and_sorption.cell_builder import CellBuilder
from src.projects.intercalation_and_sorption.cell_building import CellParams, ZCellResult
from src.projects.intercalation_and_sorption.intercalared_structure_cell_cutter import CellCutResult
from src.services import PathBuilder


def _result(verified: bool = True) -> CellCutResult:
    carbon: np.ndarray = np.array([[0.0, 0.0, 0.0], [1.0, 0.5, 0.7]])
    inter: np.ndarray = np.array([[0.5, 0.2, 0.5]])
    return CellCutResult(
        carbon=Points(carbon),
        intercalated=Points(inter),
        cell_params=CellParams(x=3.99266, y=2.305125, c=4.32),
        z_cell=ZCellResult(
            carbon=carbon,
            intercalated=inter,
            carbon_z_period=4.32,
            num_of_periods=1,
            cell_height=4.32,
            z_start=0.0,
            verified=verified,
        ),
    )


class TestCollectWarnings:
    def test_clean_all_ch_cell_has_no_warnings(self) -> None:
        assert CellBuilder.collect_warnings("final_all_ch-polygon-ABAB-v3.csv", _result()) == []

    def test_one_ch_file_is_reported_case_insensitively(self) -> None:
        warnings: list[str] = CellBuilder.collect_warnings("final_ONE_CH-v1.csv", _result())

        assert len(warnings) == 1
        assert "one_ch" in warnings[0]

    def test_unconfirmed_repeat_is_reported(self) -> None:
        warnings: list[str] = CellBuilder.collect_warnings("final_all_ch-v1.csv", _result(verified=False))

        assert len(warnings) == 1
        assert "not confirmed" in warnings[0]


class TestWriteCell:
    def test_files_go_to_a_new_folder_and_nothing_is_overwritten(
            self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(PathBuilder, "build_path_to_result_data_dir", lambda *_args: tmp_path)
        file_name: str = "final_all_ch-polygon-ABAB-v3.csv"

        first = CellBuilder.write_cell("project", "ar", "A1-7_h3", file_name, _result())
        second = CellBuilder.write_cell("project", "ar", "A1-7_h3", file_name, _result())

        assert first.cell_dir.name == "cell_ABAB_v3"
        assert second.cell_dir.name == "cell_ABAB_v3_1"
        for files in (first, second):
            assert files.carbon_path.name == "A1-7_h3_cell_carbon.dat"
            assert files.intercalated_path.name == "A1-7_h3_cell_ar_intercalated.dat"
            assert files.params_path.read_text(encoding="utf-8").startswith("a=4.61\nc=4.32\n")
            assert files.carbon_path.exists()
            assert files.intercalated_path.exists()


class TestCutIntercalatedCellTool:
    def test_tool_returns_a_summary_and_writes_only_on_request(
            self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        result: CellCutResult = _result(verified=False)
        monkeypatch.setattr(
            mcp_server.IntercalationAndSorption, "get_carbon_coords", lambda *_args: np.zeros((1, 3))
        )
        monkeypatch.setattr(
            mcp_server.InterAtomsFileManager, "read_inter_atoms", lambda *_args: Points(np.zeros((1, 3)))
        )
        monkeypatch.setattr(
            mcp_server.IntercalatedStructureCellCutter, "cut_cell", lambda *_args, **_kwargs: result
        )
        monkeypatch.setattr(PathBuilder, "build_path_to_result_data_dir", lambda *_args: tmp_path)

        summary = cut_intercalated_cell("ar", "A1-7_h3", "final_all_ch-v1.xlsx")

        assert summary["cell_height"] == 4.32
        assert summary["z_repeat_verified"] is False
        assert summary["num_of_carbon_atoms"] == 2
        assert summary["cell_params"]["is_hexagonal"] is True
        assert summary["cell_params"]["gamma"] is None
        assert summary["cell_params"]["basis"]["a"] == [-3.993, 2.305, 0.0]
        assert len(summary["warnings"]) == 1
        assert summary["files"] is None
        assert "carbon_coordinates" not in summary
        assert not list(tmp_path.iterdir())

        written = cut_intercalated_cell(
            "ar", "A1-7_h3", "final_all_ch-v1.xlsx", write_files=True, include_coordinates=True
        )

        assert Path(written["files"]["cell_params"]).exists()
        assert len(written["carbon_coordinates"]) == 2
        assert len(written["intercalated_coordinates"]) == 1
