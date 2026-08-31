"""Tests for filename-derived plot defaults."""

import pytest

from src.ui.components.plot_window_factory import PlotWindowFactory


@pytest.mark.parametrize(
    ("file_name", "expected_num_of_layers"),
    [
        ("one_ch-AA-v1.csv", 1),
        ("one_ch-ABAB-v1.csv", 2),
        ("one_ch-ABC-v1.csv", 3),
        ("one_ch-ABCD-v1.csv", 4),
        ("one_ch-abcd-v1.csv", 4),
    ],
)
def test_get_default_num_of_inter_atoms_layers_from_file_name(
    file_name: str,
    expected_num_of_layers: int,
) -> None:
    """Derive the layer count from the longest matching layer pattern."""
    actual_num_of_layers: int = PlotWindowFactory._get_default_num_of_inter_atoms_layers(
        file_name,
        fallback=2,
    )

    assert actual_num_of_layers == expected_num_of_layers


def test_get_default_num_of_inter_atoms_layers_uses_fallback_without_pattern() -> None:
    """Keep the supplied default when the filename has no layer pattern."""
    actual_num_of_layers: int = PlotWindowFactory._get_default_num_of_inter_atoms_layers(
        "carbon-channel.csv",
        fallback=5,
    )

    assert actual_num_of_layers == 5
