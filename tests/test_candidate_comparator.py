import numpy as np

from src.entities import Points
from src.projects.intercalation_and_sorption import CandidateComparator


def test_comparison_is_invariant_to_atom_order() -> None:
    candidate_a: Points = Points(points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 2.0]]))
    candidate_b: Points = Points(points=np.array([[1.0, 0.0, 2.0], [0.0, 0.0, 0.0]]))

    result: dict = CandidateComparator.compare(candidate_a, candidate_b, 0.4)

    assert result["min_assignment_rmsd"] == 0.0
    assert result["distinct"] is False


def test_comparison_can_ignore_a_periodic_z_shift() -> None:
    candidate_a: Points = Points(points=np.array([[0.0, 0.0, 1.0], [2.0, 0.0, 3.0]]))
    candidate_b: Points = Points(points=np.array([[0.0, 0.0, 5.0], [2.0, 0.0, 7.0]]))

    result: dict = CandidateComparator.compare(candidate_a, candidate_b, 0.4, z_period=4.0)

    assert result["min_assignment_rmsd"] == 0.0
    assert result["distinct"] is False


def test_different_atom_counts_are_distinct() -> None:
    candidate_a: Points = Points(points=np.array([[0.0, 0.0, 0.0]]))
    candidate_b: Points = Points(points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]))

    result: dict = CandidateComparator.compare(candidate_a, candidate_b, 0.4)

    assert result["distinct"] is True
    assert result["min_assignment_rmsd"] is None
