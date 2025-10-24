"""Zettelkasten MCP Server - Simplified workflow implementation."""

import os
import re
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import Config
from .handlers import dispatch_tool_call


# Initialize server and config
server = Server("zettelkasten-mcp")
config: Optional[Config] = None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and invalid characters."""
    filename = filename.replace('/', '-').replace('\\', '-').replace('..', '')
    filename = re.sub(r'[<>:"|?*]', '', filename)
    if not filename.endswith('.md'):
        filename += '.md'
    return filename


def validate_output_path(filepath: Path, allowed_dir: Path) -> bool:
    """Validate that output path is within allowed directory."""
    try:
        filepath_resolved = filepath.resolve()
        allowed_dir_resolved = allowed_dir.resolve()
        return str(filepath_resolved).startswith(str(allowed_dir_resolved))
    except Exception:
        return False


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools for Zettelkasten card creation."""
    return [
        # Stage 1: Draft Generation (Simplified)
        Tool(
            name="start_draft_generation",
            description="Call this at first while the user wants to build a card. This starts the draft generation workflow.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user query."
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="title_thinker",
            description="Use this tool before creating or refining the title. This creates a deliberate pause in the generation workflow for quality writing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "reasoning": {
                        "type": "string",
                        "description": "Your reasoning progress about the main topic of the conversation, or analysis of the user's proposed title"
                    }
                },
                "required": ["reasoning"]
            }
        ),
        Tool(
            name="generate_title",
            description="Generate a title based on the title_thinker result.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title for the card."
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="content_thinker",
            description="Use this tool before generating the card body.This creates a deliberate pause in the generation workflow for quality writing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title that was generated for this card."
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "The detailed reasoning about the card content given the title."
                    }
                },
                "required": ["title", "reasoning"]
            }
        ),
        Tool(
            name="generate_content",
            description="Generate the card body content by synthesizing the dialogue into an atomic, narrative article",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The card content"
                    }
                },
                "required": ["content"]
            }
        ),
        # Stage 2: Card Generation (same as before)
        Tool(
            name="start_card_generation",
            description="Start the card generation workflow with finalized draft",
            inputSchema={
                "type": "object",
                "properties": {
                    "start":{
                        "type": "boolean",
                        "description": "return True if the tool has been called"
                    },
                    "user_feedback":{
                        "type": "string",
                        "description": "List all feedback from the user."
                    },
                },
                "required": ["start", "user_feedback"]
            }
        ),
        Tool(
            name="apply_template",
            description="Apply template formatting to all finalized components and save the card",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Finalized card title (without timestamp)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Finalized card content"
                    },
                    "heading": {
                        "type": "string",
                        "description": "Optional content heading"
                    }
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="save_card",
            description="Save the formatted card to the filesystem",
            inputSchema={
                "type": "object",
                "properties": {
                    "formatted_card": {
                        "type": "string",
                        "description": "The complete formatted card content"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename for the card (will be auto-prefixed with timestamp)"
                    }
                },
                "required": ["formatted_card", "filename"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from the MCP client."""
    global config

    if config is None:
        config_path = os.getenv("CONFIG_PATH", "config.yaml")
        config = Config(config_path)

    return dispatch_tool_call(name, arguments, config)



async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
