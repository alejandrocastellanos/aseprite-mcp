"""Aseprite MCP - Model Context Protocol implementation for Aseprite."""

from mcp.server.fastmcp import FastMCP

from .core.skills import SERVER_INSTRUCTIONS

mcp = FastMCP("aseprite", instructions=SERVER_INSTRUCTIONS)

__version__ = "0.1.0"
__author__ = "Divyansh Singh"
__maintainer__ = "Alejandro Castellanos"
