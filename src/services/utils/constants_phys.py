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

    @property
    def LATTICE_PARAM(self) -> float:
        return _phys_constants["lattice_params"][self.ATOM_SYMBOL.lower()]

    @property
    def DIST_BETWEEN_ATOMS(self) -> float:
        return self.LATTICE_PARAM / sqrt(2)

    @property
    def DIST_BETWEEN_LAYERS(self) -> float:
        return self.LATTICE_PARAM / sqrt(3)

    @property
    def MIN_RECOMENDED_DIST_BETWEEN_ATOMS(self) -> float:
        return self.DIST_BETWEEN_ATOMS * 0.92

    @property
    def MIN_ALLOWED_DIST_BETWEEN_ATOMS(self) -> float:
        return self.DIST_BETWEEN_ATOMS * 0.7

    @property
    def DIST_TO_REPLACE_NEARBY_ATOMS(self) -> float:
        return self.DIST_BETWEEN_ATOMS / 3


class ConstantsAlParams(ConstantsAtomParams):
    """ Aluminium params """
    ATOMS_NAME: str = "Aluminium"
    ATOM_SYMBOL: str = "Al"


class ConstantsArParams(ConstantsAtomParams):
    """ Argon params """
    ATOMS_NAME: str = "Argon"
    ATOM_SYMBOL: str = "Ar"


class ConstantsXeParams(ConstantsAtomParams):
    """ Xenon params """
    ATOMS_NAME: str = "Xenon"
    ATOM_SYMBOL: str = "Xe"


ATOM_PARAMS_MAP: dict = {
    ConstantsAlParams.ATOM_SYMBOL.lower(): ConstantsAlParams(),  # Aluminium
    ConstantsArParams.ATOM_SYMBOL.lower(): ConstantsArParams(),  # Argon
    ConstantsXeParams.ATOM_SYMBOL.lower(): ConstantsXeParams(),  # Xenon
}
