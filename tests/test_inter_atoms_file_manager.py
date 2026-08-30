"""Tests for the final structure file naming convention."""

import pytest

from src.projects.intercalation_and_sorption import InterAtomsFileManager


def test_build_final_file_name_with_stacking_and_author() -> None:
    assert InterAtomsFileManager.build_final_file_name(
        version=3, stacking="ABCABC", author="Claude"
    ) == "one_ch-ABCABC-v3-Claude.csv"


def test_build_final_file_name_supports_the_polygon_family() -> None:
    assert InterAtomsFileManager.build_final_file_name(
        version=2,
        stacking="ABAB",
        model_family="polygon",
        author="Codex",
    ) == "one_ch-polygon-ABAB-v2-Codex.csv"


def test_build_final_file_name_requires_an_ordered_layer_type() -> None:
    with pytest.raises(ValueError):
        InterAtomsFileManager.build_final_file_name(version=1, stacking="ABC")


def test_build_final_file_name_supports_all_channels() -> None:
    assert InterAtomsFileManager.build_final_file_name(
        version=2, stacking="ABAB", author="Claude", num_of_channels="all"
    ) == "all_ch-ABAB-v2-Claude.csv"


def test_build_final_file_name_rejects_an_invalid_version() -> None:
    with pytest.raises(ValueError):
        InterAtomsFileManager.build_final_file_name(version=0, stacking="AA")


def test_build_final_file_name_rejects_an_invalid_channel_count() -> None:
    with pytest.raises(ValueError):
        InterAtomsFileManager.build_final_file_name(
            version=1, stacking="AA", num_of_channels="two"
        )


@pytest.mark.parametrize(
    ("file_name", "expected_version", "expected_stacking", "expected_author"),
    [
        ("one_ch-AA-v1.xlsx", "1", "AA", None),
        ("one_ch-ABCABC-v3.xlsx", "3", "ABCABC", None),
        ("one_ch-ABAB-v1-Volod.xlsx", "1", "ABAB", "Volod"),
        ("all_ch-ABCDABCD-v2-NV.xlsx", "2", "ABCDABCD", "NV"),
        ("one_ch-AA-v4-Claude.xlsx", "4", "AA", "Claude"),
        ("one_ch-ABCABC-v5-Codex.csv", "5", "ABCABC", "Codex"),
        ("one_ch-polygon-ABAB-v2-Codex.csv", "2", "ABAB", "Codex"),
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
        "one_ch.xlsx",
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


def test_next_version_is_independent_for_each_layer_type(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_list_result_files(*args: object, **kwargs: object) -> list[str]:
        del args, kwargs
        return [
            "one_ch-ABAB-v1-Codex.csv",
            "one_ch-ABAB-v3-Claude.csv",
            "one_ch-ABCABC-v7-Codex.csv",
            "one_ch-polygon-ABAB-v8-Codex.csv",
            "final_one_ch-v12-ABAB-Volod.xlsx",
        ]

    monkeypatch.setattr(
        InterAtomsFileManager,
        "list_result_files",
        fake_list_result_files,
    )

    assert InterAtomsFileManager.get_next_final_version("p", "e", "s", "ABAB") == 4
    assert InterAtomsFileManager.get_next_final_version(
        "p", "e", "s", "ABAB", model_family="polygon"
    ) == 9
    assert InterAtomsFileManager.get_next_final_version("p", "e", "s", "ABCABC") == 8
    assert InterAtomsFileManager.get_next_final_version("p", "e", "s", "AA") == 1


def test_legacy_final_name_pattern_remains_available_for_legacy_files() -> None:
    match = InterAtomsFileManager.LEGACY_FINAL_FILE_NAME_PATTERN.match(
        "final_one_ch-v3-ABC-Volod.xlsx"
    )

    assert match is not None
    assert match.group("version") == "3"
    assert match.group("stacking") == "ABC"


def test_final_name_pattern_exposes_the_polygon_family() -> None:
    match = InterAtomsFileManager.FINAL_FILE_NAME_PATTERN.match(
        "one_ch-polygon-ABCABC-v4-Claude.csv"
    )

    assert match is not None
    assert match.group("model_family") == "polygon"
