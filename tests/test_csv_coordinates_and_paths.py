from pathlib import Path

import numpy as np
import pytest

from src.entities import Points
from src.projects.intercalation_and_sorption import InterAtomsFileManager
from src.services import Constants, PathBuilder


def test_csv_coordinate_round_trip_preserves_atom_ids(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Constants.path, "PROJECTS_DATA_PATH", tmp_path)
    atoms: Points = Points(
        points=np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
        atom_ids=("wall-1", "center-1"),
    )

    path: Path = InterAtomsFileManager.write_inter_atoms(
        "intercalation_and_sorption", "ar", "A1-7_h3", "candidate.csv", atoms
    )
    restored = InterAtomsFileManager.read_inter_atoms(
        "intercalation_and_sorption", "ar", "A1-7_h3", "candidate.csv"
    )

    assert path.suffix == ".csv"
    assert restored.points.tolist() == atoms.points.tolist()
    assert restored.atom_ids == atoms.atom_ids


def test_result_file_path_cannot_escape_project_data() -> None:
    with pytest.raises(ValueError):
        PathBuilder.build_path_to_result_data_file(
            "intercalation_and_sorption", "ar", "A1-7_h3", "../../../../escape.csv"
        )
