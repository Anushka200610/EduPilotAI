"""MCP Server and Client package."""

from mcp_server.server import mcp_server, create_mcp_server
from mcp_server.client import EduPilotMCPClient, mcp_client

__all__ = ["mcp_server", "create_mcp_server", "EduPilotMCPClient", "mcp_client"]
