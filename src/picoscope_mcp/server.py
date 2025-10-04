"""FastMCP server for PicoScope oscilloscope control."""

from fastmcp import FastMCP

from .tools.discovery import register_discovery_tools
from .tools.configuration import register_configuration_tools
from .tools.acquisition import register_acquisition_tools
from .tools.analysis import register_analysis_tools
from .tools.advanced import register_advanced_tools

# Create FastMCP server instance
mcp = FastMCP("PicoScope MCP Server")

# Register all tool categories
register_discovery_tools(mcp)
register_configuration_tools(mcp)
register_acquisition_tools(mcp)
register_analysis_tools(mcp)
register_advanced_tools(mcp)


def main():
    """Run the MCP server."""
    # Run with STDIO transport (default for MCP)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
