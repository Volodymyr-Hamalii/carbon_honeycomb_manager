"""Tests for the final structure file naming convention."""

import pytest

from src.projects.intercalation_and_sorption import InterAtomsFileManager


def test_build_final_file_name_with_stacking_and_author() -> None:
    assert InterAtomsFileManager.build_final_file_name(
        version=3, stacking="ABC", author="Claude"
    ) == "final_one_ch-v3-ABC-Claude.csv"


def test_build_final_file_name_skips_the_stacking_suffix_when_undefined() -> None:
    assert InterAtomsFileManager.build_final_file_name(
        version=1, stacking=None, author="Claude"
    ) == "final_one_ch-v1-Claude.csv"


def test_build_final_file_name_supports_all_channels() -> None:
    assert InterAtomsFileManager.build_final_file_name(
        version=2, stacking="ABAB", author="Claude", num_of_channels="all"
    ) == "final_all_ch-v2-ABAB-Claude.csv"


def test_build_final_file_name_rejects_an_invalid_version() -> None:
    with pytest.raises(ValueError):
        InterAtomsFileManager.build_final_file_name(version=0)


def test_build_final_file_name_rejects_an_invalid_channel_count() -> None:
    with pytest.raises(ValueError):
        InterAtomsFileManager.build_final_file_name(version=1, num_of_channels="two")


@pytest.mark.parametrize(
    ("file_name", "expected_version", "expected_stacking", "expected_author"),
    [
        ("final_one_ch-v1.xlsx", "1", None, None),
        ("final_one_ch-v3-ABC.xlsx", "3", "ABC", None),
        ("final_one_ch-v1-ABAB-Volod.xlsx", "1", "ABAB", "Volod"),
        ("final_all_ch-v2-ABCD-NV.xlsx", "2", "ABCD", "NV"),
        ("final_one_ch-v4-Claude.xlsx", "4", None, "Claude"),
        ("final_one_ch-v5-ABC-Codex.csv", "5", "ABC", "Codex"),
        ("final_one_ch-v1-AA-transl-Oz.xlsx", "1", "AA", "transl-Oz"),
    ],
)
def test_final_file_name_pattern_parses_the_existing_conventions(
        file_name: str,
        expected_version: str,
        expected_stacking: str | None,
        expected_author: str | None,
) -> None:
    match = InterAtomsFileManager.FINAL_FILE_NAME_PATTERN.match(file_name)

    assert match is not None
    assert match.group("version") == expected_version
    assert match.group("stacking") == expected_stacking
    assert match.group("author") == expected_author


@pytest.mark.parametrize(
    "file_name",
    [
        "sorbed-plane-coordinates.xlsx",
        "intercalated-channel-coordinates.xlsx",
        "final_one_ch.xlsx",
        "built-structure-details.xlsx",
        "final_one_ch-v2.json",
    ],
)
def test_final_file_name_pattern_ignores_other_files(file_name: str) -> None:
    assert InterAtomsFileManager.FINAL_FILE_NAME_PATTERN.match(file_name) is None


def test_written_and_generated_names_round_trip() -> None:
    file_name: str = InterAtomsFileManager.build_final_file_name(
        version=7, stacking="ABAB", author="Claude"
    )
    match = InterAtomsFileManager.FINAL_FILE_NAME_PATTERN.match(file_name)

    assert match is not None
    assert int(match.group("version")) == 7
    assert match.group("stacking") == "ABAB"
    assert match.group("author") == "Claude"
