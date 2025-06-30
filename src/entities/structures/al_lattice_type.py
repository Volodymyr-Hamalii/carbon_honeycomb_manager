from ..lattice_type import LatticeType


class AlLatticeType(LatticeType):
    def __init__(self, al_structure: str = "cell") -> None:
        """AL structure to fill (can be 'cell' for cubic cell, 'FCC' or 'HCP' for planes)."""
        super().__init__(al_structure)

        self.is_cell: bool = al_structure.lower() == "cell"  # Cubic cell
        self.is_fcc: bool = al_structure.lower() == "fcc"  # Face-centered cubic
        self.is_hcp: bool = al_structure.lower() == "hcp"  # Hexagonal close-packed

    # @staticmethod
    # def get_info() -> str:
    #     return "AL structure to fill (can be 'cell' for cubic cell, 'FCC' or 'HCP' for planes)"

    @staticmethod
    def get_available_types() -> list[str]:
        """ 'cell', 'FCC', 'HCP' """
        return ["cell", "FCC", "HCP"]
