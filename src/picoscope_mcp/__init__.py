"""PicoScope MCP Server - STDIO MCP server for PicoScope oscilloscopes."""

from .server import mcp, main
from .device_manager import device_manager

__version__ = "0.1.0"
__all__ = ["mcp", "main", "device_manager"]
