from abc import ABC
from math import sqrt
from pathlib import Path

from .constants import Constants
from .files_manager import FileReader
from .logger import Logger


logger = Logger("ConstantsPhys")


__all__: list[str] = [
    "ConstantsAtomParams",
    "ConstantsAlParams",
    "ConstantsArParams",
    "ATOM_PARAMS_MAP",
]


def _load_constants_from_json(folder_path: Path, file_name: str) -> dict:
    try:
        return FileReader.read_json_file(
            folder_path=folder_path,
            file_name=file_name,
        )

    except Exception as e:
        logger.error(f"Failed to load constants from JSON file: {e}")
        return {}


_phys_constants: dict = _load_constants_from_json(
    folder_path=Constants.path.CONSTANTS_DATA_PATH,
    file_name=Constants.file_names.PHYS_CONSTANTS_JSON_FILE,
)


class ConstantsAtomParams(ABC):
    """ Abstract class for atom params """
    ATOMS_NAME: str
    ATOM_SYMBOL: str

    LATTICE_PARAM: float
    DIST_BETWEEN_ATOMS: float
    DIST_BETWEEN_LAYERS: float

    MIN_RECOMENDED_DIST_BETWEEN_ATOMS: float
    MIN_ALLOWED_DIST_BETWEEN_ATOMS: float
    DIST_TO_REPLACE_NEARBY_ATOMS: float


class ConstantsAlParams(ConstantsAtomParams):
    """ Aluminium params """
    ATOMS_NAME: str = "Aluminium"
    ATOM_SYMBOL: str = "Al"

    LATTICE_PARAM: float = _phys_constants["lattice_params"]["al"]
    DIST_BETWEEN_ATOMS: float = LATTICE_PARAM / sqrt(2)
    DIST_BETWEEN_LAYERS: float = LATTICE_PARAM / sqrt(3)

    MIN_RECOMENDED_DIST_BETWEEN_ATOMS: float = DIST_BETWEEN_ATOMS * 0.92
    MIN_ALLOWED_DIST_BETWEEN_ATOMS: float = DIST_BETWEEN_ATOMS * 0.7
    DIST_TO_REPLACE_NEARBY_ATOMS: float = DIST_BETWEEN_ATOMS / 3


class ConstantsArParams(ConstantsAtomParams):
    """ Argon params """
    ATOMS_NAME: str = "Argon"
    ATOM_SYMBOL: str = "Ar"

    LATTICE_PARAM: float = _phys_constants["lattice_params"]["ar"]
    DIST_BETWEEN_ATOMS: float = LATTICE_PARAM / sqrt(2)
    DIST_BETWEEN_LAYERS: float = LATTICE_PARAM / sqrt(3)

    MIN_RECOMENDED_DIST_BETWEEN_ATOMS: float = DIST_BETWEEN_ATOMS * 0.92
    MIN_ALLOWED_DIST_BETWEEN_ATOMS: float = DIST_BETWEEN_ATOMS * 0.7
    DIST_TO_REPLACE_NEARBY_ATOMS: float = DIST_BETWEEN_ATOMS / 3


ATOM_PARAMS_MAP: dict = {
    "al": ConstantsAlParams,  # Aluminium
    "ar": ConstantsArParams,  # Argon
}
