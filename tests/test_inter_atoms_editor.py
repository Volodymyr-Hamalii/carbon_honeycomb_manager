"""Tests for the intercalated atoms edit primitives."""

import numpy as np
import pytest

from src.entities import Points
from src.interfaces import ICarbonHoneycombChannel, ICarbonHoneycombPlane, IPoints
from src.projects.intercalation_and_sorption import InterAtomsEditor

from .conftest import WALL_0_PLANE_Y, Z_PERIOD


def _points(*coordinates: tuple[float, float, float]) -> Points:
    return Points(points=np.array(coordinates, dtype=np.float64))


### ADD / DELETE ###


def test_add_atoms_appends_and_sorts_by_z() -> None:
    atoms: Points = _points((0.0, 0.0, 5.0))

    result: IPoints = InterAtomsEditor.add_atoms(atoms, np.array([[1.0, 1.0, 1.0]]))

    assert len(result.points) == 2
    # The result is sorted by z, y, x - the order used in the xlsx files.
    assert result.points[0].tolist() == [1.0, 1.0, 1.0]
    assert result.points[1].tolist() == [0.0, 0.0, 5.0]


def test_add_atoms_to_an_empty_set() -> None:
    empty: Points = Points(points=np.array([]).reshape(0, 3))

    result: IPoints = InterAtomsEditor.add_atoms(empty, np.array([[1.0, 2.0, 3.0]]))

    assert result.points.tolist() == [[1.0, 2.0, 3.0]]


def test_delete_atoms_removes_the_given_indexes() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0), (0.0, 0.0, 2.0), (0.0, 0.0, 3.0))

    result: IPoints = InterAtomsEditor.delete_atoms(atoms, [1])

    assert result.points[:, 2].tolist() == [1.0, 3.0]


def test_delete_atoms_rejects_an_out_of_range_index() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0))

    with pytest.raises(IndexError):
        InterAtomsEditor.delete_atoms(atoms, [3])


def test_edit_rejects_duplicated_indexes() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0), (0.0, 0.0, 2.0))

    with pytest.raises(ValueError):
        InterAtomsEditor.delete_atoms(atoms, [0, 0])


def test_edit_does_not_mutate_the_input() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0), (0.0, 0.0, 2.0))

    InterAtomsEditor.move_atoms_on_vector(atoms, [0], np.array([1.0, 2.0, 3.0]))

    assert atoms.points.tolist() == [[0.0, 0.0, 1.0], [0.0, 0.0, 2.0]]


### MOVE ###


def test_move_atoms_on_vector_moves_all_three_axes() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0), (5.0, 5.0, 5.0))

    result: IPoints = InterAtomsEditor.move_atoms_on_vector(
        atoms, [0], np.array([1.0, 2.0, 3.0])
    )

    assert result.points[0].tolist() == [1.0, 2.0, 4.0]
    # The untouched atom keeps its coordinates.
    assert result.points[1].tolist() == [5.0, 5.0, 5.0]


def test_move_atoms_to_channel_center_keeps_the_z_coordinate(
        synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    # The channel axis passes through x = y = 0, so an atom at y = 4 moves along -Oy.
    atoms: Points = _points((0.0, 4.0, 7.0))

    result: IPoints = InterAtomsEditor.move_atoms_to_channel_center(
        atoms, [0], synthetic_channel.channel_center, distance=1.5
    )

    assert result.points[0] == pytest.approx([0.0, 2.5, 7.0], abs=1e-3)


def test_negative_distance_moves_away_from_the_channel_center(
        synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    atoms: Points = _points((0.0, 4.0, 7.0))

    result: IPoints = InterAtomsEditor.move_atoms_to_channel_center(
        atoms, [0], synthetic_channel.channel_center, distance=-1.5
    )

    assert result.points[0] == pytest.approx([0.0, 5.5, 7.0], abs=1e-3)


def test_move_along_plane_normal_moves_away_from_the_wall(
        synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    # Wall 0 lies in the y = 6 plane, so moving away from it means decreasing y.
    plane: ICarbonHoneycombPlane = synthetic_channel.planes[0]
    atoms: Points = _points((0.0, WALL_0_PLANE_Y - 3.0, 5.04))

    result: IPoints = InterAtomsEditor.move_atoms_along_plane_normal(
        atoms, [0], plane, synthetic_channel.channel_center, distance=0.5
    )

    assert result.points[0] == pytest.approx([0.0, WALL_0_PLANE_Y - 3.5, 5.04], abs=1e-3)


def test_move_along_plane_normal_towards_the_wall(
        synthetic_channel: ICarbonHoneycombChannel,
) -> None:
    plane: ICarbonHoneycombPlane = synthetic_channel.planes[0]
    atoms: Points = _points((0.0, WALL_0_PLANE_Y - 3.0, 5.04))

    result: IPoints = InterAtomsEditor.move_atoms_along_plane_normal(
        atoms, [0], plane, synthetic_channel.channel_center, distance=-0.5
    )

    assert result.points[0] == pytest.approx([0.0, WALL_0_PLANE_Y - 2.5, 5.04], abs=1e-3)


### TRANSLATE ALONG Z ###


def test_shift_along_z_moves_the_whole_set() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0), (0.0, 0.0, 2.0))

    result: IPoints = InterAtomsEditor.shift_along_z(atoms, 10.0)

    assert result.points[:, 2].tolist() == [11.0, 12.0]


def test_translate_along_z_replicates_the_set() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0))

    result: IPoints = InterAtomsEditor.translate_along_z(atoms, Z_PERIOD, num_of_periods=2)

    assert result.points[:, 2].tolist() == [1.0, 1.0 + Z_PERIOD, 1.0 + 2 * Z_PERIOD]


def test_translate_along_z_removes_duplicates() -> None:
    # The set already spans one period, so the copies overlap the original.
    atoms: Points = _points((0.0, 0.0, 1.0), (0.0, 0.0, 1.0 + Z_PERIOD))

    result: IPoints = InterAtomsEditor.translate_along_z(atoms, Z_PERIOD, num_of_periods=1)

    assert result.points[:, 2].tolist() == [1.0, 1.0 + Z_PERIOD, 1.0 + 2 * Z_PERIOD]


def test_translate_along_z_with_zero_periods_returns_the_original() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0), (0.0, 0.0, 5.0))

    result: IPoints = InterAtomsEditor.translate_along_z(atoms, Z_PERIOD, num_of_periods=0)

    assert result.points[:, 2].tolist() == [1.0, 5.0]


def test_translate_along_z_rejects_a_non_positive_period() -> None:
    atoms: Points = _points((0.0, 0.0, 1.0))

    with pytest.raises(ValueError):
        InterAtomsEditor.translate_along_z(atoms, 0.0, num_of_periods=2)
