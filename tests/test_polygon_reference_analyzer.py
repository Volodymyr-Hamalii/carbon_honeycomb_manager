"""Unit tests for polygon-reference extraction, generation and measurement."""

import numpy as np

from src.entities import Points
from src.interfaces import ICarbonHoneycombChannel
from src.projects.intercalation_and_sorption import PolygonReferenceAnalyzer


def test_reference_sites_cover_vertices_edges_and_rings(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Extract every physical source category with deterministic unique IDs."""
    sites = PolygonReferenceAnalyzer.get_reference_sites(synthetic_channel)
    vertices = [site for site in sites if site.site_type == "vertex"]
    edges = [site for site in sites if site.site_type == "edge_midpoint"]
    centers = [site for site in sites if site.site_type == "center"]

    assert len(vertices) == len(np.unique(synthetic_channel.points, axis=0))
    assert edges
    assert centers
    assert len({site.site_id for site in sites}) == len(sites)
    assert all(site.associations for site in sites)
    assert all(len(site.carbon_atom_ids) == 2 for site in edges)
    assert all(len(site.ring_vertex_ids) in (5, 6) for site in centers)


def test_bond_definition_is_strictly_below_1_65_angstrom(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Every emitted midpoint comes from a unique qualifying 3D carbon pair."""
    sites = PolygonReferenceAnalyzer.get_reference_sites(
        synthetic_channel, site_types=("edge_midpoint",)
    )
    unique_points = np.unique(synthetic_channel.points, axis=0)
    coordinate_by_id = {
        PolygonReferenceAnalyzer._stable_id("carbon", point): point for point in unique_points
    }
    pairs: set[tuple[str, str]] = set()
    for site in sites:
        first_id, second_id = site.carbon_atom_ids
        assert np.linalg.norm(coordinate_by_id[first_id] - coordinate_by_id[second_id]) < 1.65
        ordered_pair: tuple[str, str] = (
            (first_id, second_id) if first_id <= second_id else (second_id, first_id)
        )
        pairs.add(ordered_pair)
    assert len(pairs) == len(sites)


def test_generator_preserves_site_wall_provenance(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Generate one stable unmerged candidate for each selected association."""
    sites = PolygonReferenceAnalyzer.get_reference_sites(
        synthetic_channel, site_types=("vertex",), wall_indexes=(0,)
    )
    candidates = PolygonReferenceAnalyzer.generate_candidates(
        synthetic_channel,
        center_target=3.0,
        face_target=2.5,
        site_types=("vertex",),
        wall_indexes=(0,),
    )
    expected_count = sum(
        association.wall_index == 0 for site in sites for association in site.associations
    )
    assert len(candidates) == expected_count
    assert len({candidate.atom_id for candidate in candidates}) == len(candidates)
    assert all(candidate.wall_index == 0 for candidate in candidates)
    assert {candidate.site_id for candidate in candidates} <= {site.site_id for site in sites}


def test_measurement_handles_exact_face_and_central_exemption(
    synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    """Apply the face endpoint exactly and exempt a channel-center atom explicitly."""
    candidate = PolygonReferenceAnalyzer.generate_candidates(
        synthetic_channel,
        center_target=3.0,
        face_target=2.5,
        site_types=("vertex",),
        wall_indexes=(0,),
    )[0]
    points = Points(
        points=np.asarray((candidate.coordinates, synthetic_channel.channel_center), dtype=np.float64),
        atom_ids=(candidate.atom_id, "central"),
    )
    report = PolygonReferenceAnalyzer.measure(
        synthetic_channel,
        points,
        center_target=3.0,
        face_target=2.5,
        near_wall_max_dist_to_plane=3.3,
        alignment_tolerance=0.1,
    )
    exact, central = (row.to_dict() for row in report.rows)
    assert exact["alignment_type"] == "vertex"
    assert exact["target_normal_distance"] == 2.5
    assert abs(exact["normal_deviation"]) < 1e-9
    assert central["is_near_wall"] is False
    assert central["target_normal_distance"] is None
    assert central["corridor_status"] == "exempt_central"


def test_interpolation_formula_and_endpoints_are_stable() -> None:
    """Match the specified center/face interpolation and exact endpoint behavior."""
    assert PolygonReferenceAnalyzer._interpolated_target(0.0, 2.0, 3.2, 2.8) == 3.2
    assert PolygonReferenceAnalyzer._interpolated_target(2.0, 0.0, 3.2, 2.8) == 2.8
    expected = (3.0 / 4.0) * 3.2 + (1.0 / 4.0) * 2.8
    assert PolygonReferenceAnalyzer._interpolated_target(1.0, 3.0, 3.2, 2.8) == expected
