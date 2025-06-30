from pathlib import Path
import logging
import dotenv
import sys
import os


def _clear_env_cache() -> None:
    env_vars_to_clear: list[str] = [
        "DEFAULT_ACTION",
        "DEFAULT_STRUCTURE_FOLDER",
        "open_calculated_atoms",
        "set_equidistant",
        "al_lattice_type",
        "number_of_planes",
        "number_of_layers",
        "number_of_min_distances",
        "to_try_to_reflect_inter_atoms",
        "show_inter_atoms_layers",
        "interactive_mode",
    ]

    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]


# Remove cached env vars and load .env file
_clear_env_cache()
dotenv.load_dotenv()


class _ConstantsSettings:
    MULTI_THREADED: bool = False
    DEV_MODE: bool = os.environ.get("DEV_MODE", "false") == "true"  # False by default


class _ConstantsFilenames:
    # Dir names
    DATA_DIR: str = "data"
    CONFIGS_DIR: str = "configs"
    CONSTANTS_DIR: str = "constants"
    PROJECTS_DIR: str = "projects"

    INIT_DATA_DIR: str = "init_data"
    RESULT_DATA_DIR: str = "result_data"

    # File names
    INIT_DAT_FILE: str = "ljout.dat"
    PHYS_CONSTANTS_JSON_FILE: str = "phys_constants.json"

    # Intercalation and sorption paths
    PLANE_COORDINATES_XLSX_FILE: str = "sorbed-plane-coordinates.xlsx"
    CHANNEL_COORDINATES_XLSX_FILE: str = "sorbed-channel-coordinates.xlsx"
    FULL_CHANNEL_COORDINATES_XLSX_FILE: str = "intercalated-channel-coordinates.xlsx"
    ALL_CHANNELS_COORDINATES_XLSX_FILE: str = "intercalated-all-channels-coordinates.xlsx"
    CHANNEL_DETAILS_XLSX_FILE: str = "built-structure-details.xlsx"

    # Intercalation and sorption files
    C_ALL_CHANNELS_COORDINATES_DAT_FILE: str = "C.dat"
    # AL_ALL_CHANNELS_COORDINATES_DAT_FILE: str = "Al.dat"
    # AR_ALL_CHANNELS_COORDINATES_DAT_FILE: str = "Ar.dat"
    # XE_ALL_CHANNELS_COORDINATES_DAT_FILE: str = "Xe.dat"


class _ConstantsPath:
    if getattr(sys, 'frozen', False):
        # If the application is frozen (e.g., packaged with PyInstaller)
        UTILS_DIR_PATH: Path = Path(sys.executable).resolve().parent
        ROOT_DIR_PATH: Path = UTILS_DIR_PATH
    else:
        # If running in a normal Python environment
        UTILS_DIR_PATH: Path = Path(__file__).resolve().parent
        ROOT_DIR_PATH: Path = UTILS_DIR_PATH.parent.parent.parent

    # INIT_DATA_PATH: Path = ROOT_DIR_PATH / _ConstantsFilenames.INIT_DATA_DIR
    # RESULT_DATA_PATH: Path = ROOT_DIR_PATH / _ConstantsFilenames.RESULT_DATA_DIR

    DATA_DIR_PATH: Path = ROOT_DIR_PATH / _ConstantsFilenames.DATA_DIR
    CONFIGS_DATA_PATH: Path = DATA_DIR_PATH / _ConstantsFilenames.CONFIGS_DIR
    CONSTANTS_DATA_PATH: Path = DATA_DIR_PATH / _ConstantsFilenames.CONSTANTS_DIR
    PROJECTS_DATA_PATH: Path = DATA_DIR_PATH / _ConstantsFilenames.PROJECTS_DIR


class _ConstantsLogger:
    LEVELS: dict[str, int] = {
        "debug": logging.DEBUG,  # 10
        "info": logging.INFO,  # 20
        "performance": 25,
        "metrics": 27,
        "warning": logging.WARNING,  # 30
        "error": logging.ERROR,  # 40
    }
    DEFAULT_LEVEL: str = "info"  # set 'warning' as default
    LEVEL: int = int(os.environ.get("LEVEL", 0)) or LEVELS[DEFAULT_LEVEL]


class _ConstantsMath:
    COORDINATE_INDEX_MAP: dict[str, int] = {
        "x": 0,
        "y": 1,
        "z": 2,
    }

    INDEX_COORDINATE_MAP: dict[int, str] = {
        i: c for c, i in COORDINATE_INDEX_MAP.items()
    }


class Constants:
    path = _ConstantsPath
    logger = _ConstantsLogger
    file_names = _ConstantsFilenames
    math = _ConstantsMath
    settings = _ConstantsSettings

    DEFAULT_ACTION: str = os.environ.get("DEFAULT_ACTION") or "full_flow"
    DEFAULT_STRUCTURE_FOLDER: str = os.environ.get("DEFAULT_STRUCTURE_FOLDER") or "A1-7_h3"
