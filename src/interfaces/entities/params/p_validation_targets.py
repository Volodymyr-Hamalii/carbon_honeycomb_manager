from abc import ABC, abstractmethod


class PValidationTargets(ABC):
    """
    Protocol for the target distances and tolerances used to validate an intercalated structure.

    Every value is an explicit parameter: the validator never resolves a target on its own, so the
    same validator serves skills with different sets of rules (and different intercalated elements).
    """

    # Equilibrium distance from an intercalated atom to the nearest carbon atom.
    target_dist_to_carbon: float

    # Equilibrium distance between two intercalated atoms.
    target_dist_between_inter_atoms: float

    # Physical floor: no pair of intercalated atoms may be closer than this.
    hard_min_dist_between_inter_atoms: float

    # Allowed deviation corridor around the equilibrium distances, in percent.
    max_compression_percent: float
    max_expansion_percent: float

    # Z self-repeatability check.
    carbon_z_period: float
    z_period_tolerance: float
    max_z_period_multiplier: int
    required_z_period_multiplier: int | None

    # In-plane offset within which an atom counts as placed opposite a polygon center or an edge hole.
    opposite_position_tolerance: float

    # Distance to the nearest wall plane up to which an atom counts as sitting near a wall. Only
    # those atoms are held to the intercalated-carbon equilibrium distance; the atoms in the middle
    # of a wide channel are legitimately much further from carbon. None resolves to
    # `dist_to_carbon_upper_bound`.
    near_wall_max_dist_to_plane: float | None

    @property
    @abstractmethod
    def near_wall_dist_to_plane_limit(self) -> float:
        ...

    @property
    @abstractmethod
    def dist_to_carbon_lower_bound(self) -> float:
        ...

    @property
    @abstractmethod
    def dist_to_carbon_upper_bound(self) -> float:
        ...

    @property
    @abstractmethod
    def dist_between_inter_atoms_lower_bound(self) -> float:
        ...

    @property
    @abstractmethod
    def dist_between_inter_atoms_upper_bound(self) -> float:
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, float | int]:
        ...
