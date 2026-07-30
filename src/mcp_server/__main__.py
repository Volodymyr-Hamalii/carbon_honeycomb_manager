"""
Entry point of the MCP server: `python -m src.mcp_server` from the repository root.

The stdio transport uses stdout for the protocol itself, so everything else must stay off it:
logging is forced to stderr and matplotlib is switched to the headless Agg backend before the domain
layer - which imports `pyplot` - is loaded.
"""

import logging
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

# Make the repository root importable regardless of the working directory the client starts us in.
_ROOT_DIR_PATH: Path = Path(__file__).resolve().parent.parent.parent
if str(_ROOT_DIR_PATH) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR_PATH))


def _force_logging_to_stderr() -> None:
    """Move any root logging handler that writes to stdout over to stderr."""
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream is sys.stdout:
            handler.setStream(sys.stderr)


def main() -> None:
    """Run the MCP server over the stdio transport."""
    from src.mcp_server.server import server

    _force_logging_to_stderr()

    server.run(transport="stdio")


if __name__ == "__main__":
    main()
