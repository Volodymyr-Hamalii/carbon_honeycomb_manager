"""Contract tests for polygon-reference MCP tools and synchronized skills."""

from pathlib import Path
import asyncio

import numpy as np
import pytest

from src.entities import Points, ValidationTargets
from src.interfaces import ICarbonHoneycombChannel
from src.mcp_server.channel_provider import ChannelProvider
from src.mcp_server.server import (
    generate_atoms_at_polygon_sites,
    get_polygon_reference_sites,
    measure_polygon_site_distances,
    server,
)
from src.mcp_server.validation_targets_builder import ValidationTargetsBuilder
from src.projects.intercalation_and_sorption import InterAtomsFileManager


def test_reference_site_mcp_supports_compact_and_filtered_payloads(
    monkeypatch: pytest.MonkeyPatch,
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Keep discovery payloads bounded while retaining full counts."""
    monkeypatch.setattr(ChannelProvider, "get_channel", lambda *_args: synthetic_channel)
    compact = get_polygon_reference_sites("ar", "synthetic", include_details=False)
    detailed = get_polygon_reference_sites(
        "ar", "synthetic", site_types=["vertex"], wall_indexes=[0], limit=2
    )
    assert "sites" not in compact
    assert detailed["returned"] == 2
    assert len(detailed["sites"]) == 2
    assert all(site["site_type"] == "vertex" for site in detailed["sites"])
    assert all(
        any(association["wall_index"] == 0 for association in site["associations"])
        for site in detailed["sites"]
    )


def test_polygon_generator_mcp_is_pure_and_has_stable_ids(
    monkeypatch: pytest.MonkeyPatch,
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Return candidates and provenance without requiring an output path."""
    monkeypatch.setattr(ChannelProvider, "get_channel", lambda *_args: synthetic_channel)
    result = generate_atoms_at_polygon_sites(
        "ar", "synthetic", site_types=["edge_midpoint"], wall_indexes=[0], limit=4
    )
    assert result["returned"] == 4
    assert len({candidate["atom_id"] for candidate in result["candidates"]}) == 4
    assert all(candidate["site_type"] == "edge_midpoint" for candidate in result["candidates"])
    assert all("site_id" in candidate and "inward_normal" in candidate for candidate in result["candidates"])


def test_polygon_site_type_validation_rejects_unknown_values(
    monkeypatch: pytest.MonkeyPatch,
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Reject invalid public enum values before returning an ambiguous payload."""
    monkeypatch.setattr(ChannelProvider, "get_channel", lambda *_args: synthetic_channel)
    with pytest.raises(ValueError, match="Unknown site_types"):
        get_polygon_reference_sites("ar", "synthetic", site_types=["face"])
    with pytest.raises(IndexError, match="out of range"):
        get_polygon_reference_sites("ar", "synthetic", wall_indexes=[99])


def test_measurement_mcp_accepts_inline_and_file_inputs(
    monkeypatch: pytest.MonkeyPatch,
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Use the same atomic measurement contract for inline and selected-file data."""
    monkeypatch.setattr(ChannelProvider, "get_channel", lambda *_args: synthetic_channel)
    targets = ValidationTargets(
        target_dist_to_carbon=3.0,
        target_dist_between_inter_atoms=4.0,
        hard_min_dist_between_inter_atoms=2.0,
        carbon_z_period=4.32,
        opposite_position_tolerance=0.1,
        near_wall_max_dist_to_plane=3.3,
    )
    monkeypatch.setattr(ValidationTargetsBuilder, "build", lambda *_args, **_kwargs: targets)
    candidate = generate_atoms_at_polygon_sites(
        "ar", "synthetic", site_types=["vertex"], wall_indexes=[0], limit=1
    )["candidates"][0]
    coordinates = [candidate["coordinates"]]
    atom_ids = [candidate["atom_id"]]
    stored = Points(points=np.asarray(coordinates), atom_ids=tuple(atom_ids))
    monkeypatch.setattr(InterAtomsFileManager, "read_inter_atoms", lambda *_args: stored)

    inline = measure_polygon_site_distances(
        "ar", "synthetic", atoms=coordinates, atom_ids=atom_ids,
        reference_wall_index=0,
    )
    from_file = measure_polygon_site_distances(
        "ar", "synthetic", file_name="candidate.csv", reference_wall_indexes=[0]
    )
    assert inline == from_file
    assert inline["rows"][0]["atom_id"] == atom_ids[0]
    assert inline["rows"][0]["wall_selection_mode"] == "explicit_reference"


def test_mcp_tool_list_and_documented_count_are_current() -> None:
    """Advertise all three tools and keep the documented total synchronized."""
    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}
    assert len(tools) == 30
    assert {
        "get_polygon_reference_sites",
        "generate_atoms_at_polygon_sites",
        "measure_polygon_site_distances",
    } <= names
    docs = (Path(__file__).resolve().parent.parent / "docs/mcp_description.md").read_text(
        encoding="utf-8"
    )
    assert "30 tools" in docs


def test_codex_and_claude_polygon_skills_are_behaviorally_synchronized() -> None:
    """Allow only the expected agent author/output-name difference."""
    root = Path(__file__).resolve().parent.parent
    codex_path = root / ".agents/skills/calculate-intercalation-structure-related-carbon-polygon-points/SKILL.md"
    claude_path = root / ".claude/skills/calculate-intercalation-structure-related-carbon-polygon-points/SKILL.md"
    codex = codex_path.read_text(encoding="utf-8")
    claude = claude_path.read_text(encoding="utf-8")
    assert codex.replace("Codex", "AGENT") == claude.replace("Claude", "AGENT")
    for required in (
        "at most 5 structurally distinct candidate branches",
        "4 consecutive validation rounds",
        "save_run_checkpoint",
        "compare_structures",
        "rebuild",
        "write_final_structure",
        "atom_id",
    ):
        assert required in codex
    assert "author=\"Codex\"" in codex
    assert "author=\"Claude\"" in claude
    assert "one_ch-polygon-{type}-v{i}-Codex.csv" in codex
    assert 'model_family="polygon"' in codex
    assert "ABCABC" in codex
    assert "ABCDABCD" in codex


def test_codex_and_claude_carbon_atom_skills_are_behaviorally_synchronized() -> None:
    """Keep ordered-layer and output naming rules identical for both agents."""
    root = Path(__file__).resolve().parent.parent
    codex_path = root / ".agents/skills/calculate-intercalation-structure-related-carbon-atoms/SKILL.md"
    claude_path = root / ".claude/skills/calculate-intercalation-structure-related-carbon-atoms/SKILL.md"
    codex = codex_path.read_text(encoding="utf-8")
    claude = claude_path.read_text(encoding="utf-8")

    assert codex.replace("Codex", "AGENT") == claude.replace("Claude", "AGENT")
    assert "one_ch-{type}-v{i}-Codex.csv" in codex
    assert "at most four unique" in codex
