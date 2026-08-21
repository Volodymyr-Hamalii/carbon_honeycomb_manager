"""Opt-in polygon-reference smoke tests against expensive real channel geometry."""

import os

import numpy as np
import pytest

from src.entities import Points
from src.interfaces import ICarbonHoneycombChannel
from src.mcp_server.channel_provider import ChannelProvider
from src.projects.intercalation_and_sorption import PolygonReferenceAnalyzer


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_REAL_DATA_SMOKE") != "1",
    reason="Set RUN_REAL_DATA_SMOKE=1 to build the real A1 and C0 channel geometries.",
)


@pytest.mark.parametrize("structure", ("A1-7_h3", "C0-7_h3"))
def test_real_ar_polygon_reference_workflow(structure: str) -> None:
    """Extract, cache, generate, and measure stable sites for the Ar smoke structures."""
    channel: ICarbonHoneycombChannel = ChannelProvider.get_channel(
        "intercalation_and_sorption", "ar", structure
    )
    first = PolygonReferenceAnalyzer.get_reference_sites(channel)
    second = PolygonReferenceAnalyzer.get_reference_sites(channel)
    assert first is second
    assert any(site.site_type == "vertex" for site in first)
    assert any(site.site_type == "edge_midpoint" for site in first)
    if structure == "C0-7_h3":
        assert PolygonReferenceAnalyzer.get_rings(channel)

    atom_params = ChannelProvider.get_atom_params("ar")
    candidate = PolygonReferenceAnalyzer.generate_candidates(
        channel,
        center_target=atom_params.PLACE_OPPOSITE_CENTERS_DIST,
        face_target=atom_params.PLACE_OPPOSITE_FACES_DIST,
        wall_indexes=(0,),
    )[0]
    atoms = Points(
        points=np.asarray((candidate.coordinates,), dtype=np.float64),
        atom_ids=(candidate.atom_id,),
    )
    report = PolygonReferenceAnalyzer.measure(
        channel,
        atoms,
        center_target=atom_params.PLACE_OPPOSITE_CENTERS_DIST,
        face_target=atom_params.PLACE_OPPOSITE_FACES_DIST,
        near_wall_max_dist_to_plane=max(
            atom_params.PLACE_OPPOSITE_CENTERS_DIST,
            atom_params.PLACE_OPPOSITE_FACES_DIST,
        ) * 1.1,
        alignment_tolerance=0.8,
    )
    assert report.rows[0].to_dict()["atom_id"] == candidate.atom_id
