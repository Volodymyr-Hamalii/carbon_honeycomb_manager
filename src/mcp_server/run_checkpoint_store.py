import json
import re
from pathlib import Path
from typing import Any

from src.services import PathBuilder


class RunCheckpointStore:
    """Persist explicit, resumable agent-loop checkpoints beside structure results."""

    RUNS_DIR_NAME: str = ".agent-runs"
    RUN_ID_PATTERN: re.Pattern[str] = re.compile(r"^[A-Za-z0-9_-]{1,80}$")

    @classmethod
    def save(
            cls,
            project_dir: str,
            element: str,
            structure: str,
            run_id: str,
            state: dict[str, Any],
    ) -> Path:
        """Atomically save one JSON checkpoint."""
        path: Path = cls._path(project_dir, element, structure, run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path = path.with_suffix(".json.tmp")
        temporary_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        temporary_path.replace(path)
        return path

    @classmethod
    def load(
            cls,
            project_dir: str,
            element: str,
            structure: str,
            run_id: str,
    ) -> dict[str, Any]:
        """Load one JSON checkpoint."""
        path: Path = cls._path(project_dir, element, structure, run_id)
        if not path.exists():
            raise FileNotFoundError(f"Run checkpoint not found: {run_id}")
        loaded: Any = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"Run checkpoint {run_id!r} must contain a JSON object.")
        return loaded

    @classmethod
    def list_run_ids(cls, project_dir: str, element: str, structure: str) -> list[str]:
        """List saved checkpoint IDs for one element and structure."""
        runs_dir: Path = PathBuilder.build_path_to_result_data_file(
            project_dir, element, structure, cls.RUNS_DIR_NAME
        )
        if not runs_dir.exists():
            return []
        return sorted(path.stem for path in runs_dir.glob("*.json") if path.is_file())

    @classmethod
    def _path(
            cls,
            project_dir: str,
            element: str,
            structure: str,
            run_id: str,
    ) -> Path:
        """Build a contained checkpoint path after validating its identifier."""
        if cls.RUN_ID_PATTERN.fullmatch(run_id) is None:
            raise ValueError("run_id may contain only letters, digits, underscores and hyphens.")
        return PathBuilder.build_path_to_result_data_file(
            project_dir,
            element,
            structure,
            f"{cls.RUNS_DIR_NAME}/{run_id}.json",
        )
