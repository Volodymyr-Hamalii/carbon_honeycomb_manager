from pathlib import Path

import pytest

from src.mcp_server.run_checkpoint_store import RunCheckpointStore
from src.services import Constants


def test_checkpoint_round_trip(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Constants.path, "PROJECTS_DATA_PATH", tmp_path)
    state: dict[str, object] = {"candidate": 2, "iterations_without_improvement": 1}

    RunCheckpointStore.save("intercalation_and_sorption", "ar", "A1-7_h3", "run-1", state)

    assert RunCheckpointStore.load(
        "intercalation_and_sorption", "ar", "A1-7_h3", "run-1"
    ) == state
    assert RunCheckpointStore.list_run_ids(
        "intercalation_and_sorption", "ar", "A1-7_h3"
    ) == ["run-1"]


def test_checkpoint_rejects_unsafe_run_id() -> None:
    with pytest.raises(ValueError):
        RunCheckpointStore.load(
            "intercalation_and_sorption", "ar", "A1-7_h3", "../escape"
        )
