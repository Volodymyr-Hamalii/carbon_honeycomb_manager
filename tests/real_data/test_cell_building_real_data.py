"""Opt-in checks of the cell building against the hand-made reference cells in `data/projects`."""

import os
import re
from pathlib import Path

import pytest

from src.entities import Points
from src.projects.intercalation_and_sorption import IntercalationAndSorption
from src.projects.intercalation_and_sorption.cell_building import CellParamsBuilder
from src.projects.intercalation_and_sorption.intercalared_structure_cell_cutter import (
    CellCutResult,
    IntercalatedStructureCellCutter,
)


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_REAL_DATA_SMOKE") != "1",
    reason="Set RUN_REAL_DATA_SMOKE=1 to run the cell building on real structures.",
)

PROJECT: str = "intercalation_and_sorption"
SUBPROJECT: str = "ar"
AR_DIR: Path = Path(__file__).resolve().parents[2] / "data" / "projects" / "intercalation_and_sorption" / "ar"
BASIS_DIR: Path = AR_DIR / "ar-cells-with-basis"
RESULT_DIR: Path = AR_DIR / "result_data"


def _read_params(path: Path) -> dict[str, float]:
    """Parse `a`, `c`, `gamma` and the basis vectors from a cell_params file."""
    text: str = path.read_text(encoding="utf-8")
    values: dict[str, float] = {}
    for key, pattern in (("a", r"^a(?:=b)?=([\d.]+)"), ("c", r"^c=([\d.]+)"), ("gamma", r"^γ=([\d.]+)")):
        match: re.Match[str] | None = re.search(pattern, text, re.M)
        if match:
            values[key] = float(match.group(1))
    basis: re.Match[str] | None = re.search(r"^b = \(([-\d.]+), ([-\d.]+), 0\)", text, re.M)
    assert basis is not None
    values["x"], values["y"] = float(basis.group(1)), float(basis.group(2))

    return values


# structure, inter file, reference cell folder, expected carbon atoms, expected z repeat confirmed
CUT_CASES: list[tuple[str, str, Path, int, bool]] = [
    ("C2-7_h3", "final_all_ch-polygon-ABAB-v3.csv", BASIS_DIR / "C2-7_h3", 40, True),
    ("C0-7_h3", "final_all_ch-v2-ABAB.xlsx", BASIS_DIR / "C0-7_h3" / "cell_ABAB", 48, False),
    ("C0-7_h3", "final_one_ch-v6-ABC-Codex.csv", BASIS_DIR / "C0-7_h3" / "cell_ABC", 144, False),
    ("A1-7_h3", "final_all_ch-v1.xlsx", BASIS_DIR / "A1-7_h3", 14, True),
    ("B1-7_h7", "final_all_ch-v2-ABAB-NV.xlsx", RESULT_DIR / "B1-7_h7" / "cell_ABAB_v2_NV", 24, True),
]


@pytest.mark.parametrize(("structure", "file_name", "reference_dir", "num_of_carbon", "verified"), CUT_CASES)
def test_cell_height_and_carbon_match_the_reference(
        structure: str,
        file_name: str,
        reference_dir: Path,
        num_of_carbon: int,
        verified: bool,
) -> None:
    carbon = IntercalationAndSorption.get_carbon_coords(PROJECT, SUBPROJECT, structure)
    inter = IntercalationAndSorption.get_inter_coords(PROJECT, SUBPROJECT, structure, file_name)
    assert inter is not None

    result: CellCutResult = IntercalatedStructureCellCutter.cut_cell(Points(carbon), Points(inter))

    reference_file: Path = next(reference_dir.glob("cell_params*.txt"))
    assert result.cell_params.c == pytest.approx(_read_params(reference_file)["c"], abs=1e-3)
    assert len(result.carbon.points) == num_of_carbon
    assert result.z_cell.verified is verified


# structure, reference cell folder; gamma is compared only where the reference stores the obtuse angle
PARAMS_CASES: list[tuple[str, Path]] = [
    ("A1-7_h3", BASIS_DIR / "A1-7_h3"),
    ("A1.5-7_h3_sym", BASIS_DIR / "A1.5-7_h3_sym"),
    ("A2-7_h3", BASIS_DIR / "A2-7_h3"),
    ("A2.5-7_h3_sym", BASIS_DIR / "A2.5-7_h3_sym"),
    ("A3-7_h3", BASIS_DIR / "A3-7_h3"),
    ("B1-7_h7", BASIS_DIR / "B1-7_h7" / "cell_ABAB_1"),
    ("B2-7_h7", BASIS_DIR / "B2-7_h7" / "cell_ABAB"),
    ("B3-7_h7", RESULT_DIR / "B3-7_h7" / "cell_ABAB_v2_NV"),
    ("B4-7_h7", BASIS_DIR / "B4-7_h7"),
    ("C0-7_h3", BASIS_DIR / "C0-7_h3" / "cell_AA"),
    ("C1-7_h3", BASIS_DIR / "C1-7_h3"),
    ("C2-7_h3", BASIS_DIR / "C2-7_h3"),
]


@pytest.mark.parametrize(("structure", "reference_dir"), PARAMS_CASES)
def test_cell_params_match_the_reference(structure: str, reference_dir: Path) -> None:
    carbon = IntercalationAndSorption.get_carbon_coords(PROJECT, SUBPROJECT, structure)
    channels = IntercalatedStructureCellCutter._split_into_channels(Points(carbon))
    reference: dict[str, float] = _read_params(next(reference_dir.glob("cell_params*.txt")))

    params = CellParamsBuilder.build(channels[0], reference["c"])

    assert round(params.x, 3) == pytest.approx(abs(reference["x"]), abs=1e-3)
    assert round(params.y, 3) == pytest.approx(reference["y"], abs=1e-3)
    assert round(params.a_length, 3) == pytest.approx(reference["a"], abs=1e-3)
    assert ("gamma" in reference) is (not params.is_hexagonal)

    # B4 stores the acute angle (the supplement of the written a/b angle), which is not reproduced.
    if "gamma" in reference and reference["gamma"] > 90:
        assert params.gamma == pytest.approx(reference["gamma"], abs=0.05)
