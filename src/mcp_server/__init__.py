"""
MCP (Model Context Protocol) server exposing this project's domain layer to AI agents.

The package depends on the domain layer (`src.projects`, `src.services`, `src.entities`) but nothing
in the domain layer depends on it, so the server can be added, changed or dropped without touching
the application.

The server is rule-agnostic and element-agnostic on purpose: it exposes measurements, metadata and
edit primitives, while the rules a particular structure has to follow live in the Claude skill that
drives it. See `docs/mcp_description.md`.
"""

from .channel_provider import ChannelProvider
from .mvp_params_adapter import MvpParamsAdapter
from .validation_targets_builder import ValidationTargetsBuilder

__all__: list[str] = [
    "ChannelProvider",
    "MvpParamsAdapter",
    "ValidationTargetsBuilder",
]
