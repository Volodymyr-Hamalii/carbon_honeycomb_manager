"""Cached access to the carbon channel model of a structure."""

from functools import lru_cache

from src.interfaces import ICarbonHoneycombChannel
from src.services import ATOM_PARAMS_MAP, Constants, ConstantsAtomParams
from src.projects.carbon_honeycomb_actions import CarbonHoneycombModeller


class ChannelProvider:
    """
    Cached access to the carbon channel model and to the per-element physical constants.

    Building a channel is expensive: the planes, polygons and edge holes are derived geometrically
    from the raw `.dat` coordinates and take seconds for the larger structures. Because
    `CarbonHoneycombChannel` is a frozen dataclass whose derived properties are cached on the
    instance, caching the instance itself also caches the whole geometry - which matters a lot for
    an MCP session where a single structure is queried and edited dozens of times.
    """

    DEFAULT_PROJECT_DIR: str = "intercalation_and_sorption"

    CACHE_SIZE: int = 16

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def get_channel(
            project_dir: str,
            subproject_dir: str,
            structure_dir: str,
    ) -> ICarbonHoneycombChannel:
        """Build (or return the cached) carbon channel of the structure."""
        return CarbonHoneycombModeller.build_carbon_channel(
            project_dir=project_dir,
            subproject_dir=subproject_dir,
            structure_dir=structure_dir,
            file_name=Constants.file_names.INIT_DAT_FILE,
        )

    @staticmethod
    def get_atom_params(element: str) -> ConstantsAtomParams:
        """Return the physical constants of the intercalated element."""
        key: str = element.lower()

        if key not in ATOM_PARAMS_MAP:
            raise ValueError(
                f"Unknown element {element!r}. Available elements: {sorted(ATOM_PARAMS_MAP)}."
            )

        return ATOM_PARAMS_MAP[key]

    @classmethod
    def clear_cache(cls) -> None:
        """Drop the cached channels (e.g. after the init data files changed on disk)."""
        cls.get_channel.cache_clear()
