"""Interface for polygon-reference extraction, generation and measurement."""

from abc import ABC, abstractmethod

from src.entities.polygon_reference import (
    GeneratedPolygonCandidate,
    PolygonRing,
    PolygonReferenceSite,
    PolygonSiteMeasurementReport,
    PolygonSiteType,
)
from src.interfaces.entities.figures.i_points import IPoints
from src.interfaces.projects.carbon_honeycomb_actions.channel.i_carbon_honeycomb_channel import (
    ICarbonHoneycombChannel,
)


class IPolygonReferenceAnalyzer(ABC):
    """Define the rule-agnostic polygon-reference domain contract."""

    @classmethod
    @abstractmethod
    def get_reference_sites(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        site_types: tuple[PolygonSiteType, ...] | None = None,
        wall_indexes: tuple[int, ...] | None = None,
    ) -> tuple[PolygonReferenceSite, ...]:
        ...

    @classmethod
    @abstractmethod
    def get_rings(
        cls, carbon_channel: ICarbonHoneycombChannel
    ) -> tuple[PolygonRing, ...]:
        ...

    @classmethod
    @abstractmethod
    def generate_candidates(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        center_target: float,
        face_target: float,
        site_types: tuple[PolygonSiteType, ...] | None = None,
        wall_indexes: tuple[int, ...] | None = None,
    ) -> tuple[GeneratedPolygonCandidate, ...]:
        ...

    @classmethod
    @abstractmethod
    def measure(
        cls,
        carbon_channel: ICarbonHoneycombChannel,
        inter_atoms: IPoints,
        center_target: float,
        face_target: float,
        near_wall_max_dist_to_plane: float,
        alignment_tolerance: float,
        corridor_lower_percent: float = -8.0,
        corridor_upper_percent: float = 10.0,
        reference_wall_indexes: tuple[int, ...] | None = None,
    ) -> PolygonSiteMeasurementReport:
        ...
