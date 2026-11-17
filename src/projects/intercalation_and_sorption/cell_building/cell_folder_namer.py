"""Naming of the folder with a cut cell: `cell_{type}_v{i}` with a `_{j}` suffix on collisions."""

import re
from pathlib import Path


class CellFolderNamer:
    """Build unique `cell_{type}_v{i}` folder names from the name of the intercalated structure file."""

    _VERSION_PATTERN: re.Pattern[str] = re.compile(r"^v(\d+)$")
    _TYPE_PATTERN: re.Pattern[str] = re.compile(r"^[A-D]{2,}$")

    @classmethod
    def parse_file_name(cls, file_name: str) -> tuple[str | None, int | None]:
        """Return (stacking type, version) found in a file name like `final_one_ch-polygon-ABAB-v3.csv`."""
        tokens: list[str] = Path(file_name).stem.split("-")

        structure_type: str | None = None
        version: int | None = None

        for token in tokens:
            if version is None:
                version_match: re.Match[str] | None = cls._VERSION_PATTERN.match(token)
                if version_match:
                    version = int(version_match.group(1))
                    continue
            if structure_type is None and cls._TYPE_PATTERN.match(token):
                structure_type = token

        return structure_type, version

    @classmethod
    def build_base_name(cls, file_name: str) -> str:
        """Folder name without a collision suffix."""
        structure_type, version = cls.parse_file_name(file_name)

        name: str = "cell"
        if structure_type:
            name += f"_{structure_type}"
        if version is not None:
            name += f"_v{version}"

        return name

    @classmethod
    def create_unique_dir(cls, parent_dir: Path, file_name: str) -> Path:
        """Create a new cell folder in `parent_dir`, never reusing an existing one."""
        base_name: str = cls.build_base_name(file_name)
        parent_dir.mkdir(parents=True, exist_ok=True)

        candidate: Path = parent_dir / base_name
        suffix: int = 0
        while True:
            try:
                candidate.mkdir()
                return candidate
            except FileExistsError:
                suffix += 1
                candidate = parent_dir / f"{base_name}_{suffix}"
