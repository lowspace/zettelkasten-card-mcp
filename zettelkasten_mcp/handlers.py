"""Tool handlers for Zettelkasten MCP server."""

from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.types import TextContent

from .config import Config
from .responses import *


# ============================================================================
# Stage 1: Draft Generation Handlers
# ============================================================================

def handle_start_draft_generation(arguments: dict, config: Config) -> list[TextContent]:
    """Handle start_draft_generation tool call."""
    query = arguments["query"]
    next_tool = 'title_thinker'
    return [TextContent(
        type="text",
        text=TITLE_THINKER_PROMPT.format(query = query, next_tool=next_tool)
    )]


def handle_title_thinker(arguments: dict, config: Config) -> list[TextContent]:
    """Handle title_thinker tool call."""
    next_tool = "generate_title"
    return [TextContent(
        type="text",
        text=TITLE_GENERATION_PROMPT.format(
            next_tool=next_tool
        )
    )]


def handle_generate_title(arguments: dict, config: Config) -> list[TextContent]:
    """Handle generate_title tool call."""
    title = arguments["title"]
    next_tool = "content_thinker"
    return [TextContent(
        type="text",
        text=CONTENT_THINKER_PROMPT.format(
            title=title,
            next_tool=next_tool
        )
    )]


def handle_content_thinker(arguments: dict, config: Config) -> list[TextContent]:
    """Handle content_thinker tool call."""
    title = arguments["title"]
    next_tool = "generate_content"

    return [TextContent(
        type="text",
        text=CONTENT_GENERATION_PROMPT.format(
            title=title,
            next_tool=next_tool
        )
    )]


def handle_generate_content(arguments: dict, config: Config) -> list[TextContent]:
    """Handle generate_content tool call."""
    # Get title from arguments or context
    return [TextContent(
        type="text",
        text="The draft generation workflow is completed."
    )]

# ============================================================================
# Stage 2: Card Generation Handlers
# ============================================================================

def handle_start_card_generation(arguments: dict, config: Config) -> list[TextContent]:
    """Handle start_card_generation tool call."""
    user_feedback = arguments["user_feedback"]

    return [TextContent(
        type="text",
        text=ROUTER_PROMPT
    )]


def handle_generate_heading(arguments: dict, config: Config) -> list[TextContent]:
    """Handle generate_heading tool call."""
    next_tool = 'apply_template'
    return [TextContent(
        type="text",
        text=HEADING_GENERATION_PROMPT.format(next_tool=next_tool)
    )]


def handle_apply_template(arguments: dict, config: Config) -> list[TextContent]:
    """Handle apply_template tool call."""
    title = arguments["title"]
    content = arguments["content"]
    heading = arguments.get("heading", "")
    next_tool="save_card"

    # Load template
    template_content = config.load_template()
    if not template_content:
        return [TextContent(
            type="text",
            text=ERROR_TEMPLATE_NOT_FOUND.format(template_file=config.template_file)
        )]

    # Get current timestamp in the format: YYYYMMDDHHMMSS
    local_now = datetime.now().astimezone()
    format_compact = local_now.strftime("%Y%m%d%H%M%S")
    format_iso_offset = local_now.isoformat(timespec='seconds')

    # Apply template replacements
    formatted_card = template_content.replace("{{title}}", title)
    formatted_card = formatted_card.replace("{{content}}", content)
    formatted_card = formatted_card.replace("{{timestamp}}", format_compact)
    formatted_card = formatted_card.replace("{{created_at}}", format_iso_offset)

    # Handle heading - remove placeholder line if no heading provided
    if heading:
        formatted_card = formatted_card.replace("{{heading}}", heading)
    else:
        # Remove lines containing {{heading}} placeholder
        lines = formatted_card.split('\n')
        formatted_card = '\n'.join(line for line in lines if '{{heading}}' not in line)

    # Create full filename with timestamp prefix
    full_filename = f"{format_compact} - {title}.md"

    preview = formatted_card[:800] + ('...' if len(formatted_card) > 800 else '')

    return [TextContent(
        type="text",
        text=RESPONSE_CARD_PREVIEW.format(
            preview=preview,
            next_tool=next_tool
        )
    )]


def handle_save_card(arguments: dict, config: Config) -> list[TextContent]:
    """Handle save_card tool call."""
    from .server import sanitize_filename, validate_output_path

    formatted_card = arguments["formatted_card"]
    filename = arguments["filename"]

    # Sanitize filename
    if config.filename_sanitization:
        filename = sanitize_filename(filename)

    # Construct full path
    filepath = config.output_directory / filename

    # Validate path
    if not validate_output_path(filepath, config.output_directory):
        return [TextContent(type="text", text=ERROR_PATH_TRAVERSAL)]

    # Check if file exists and create backup if needed
    backup_created = False
    if filepath.exists() and config.create_backup:
        backup_path = filepath.with_suffix('.md.backup')
        try:
            filepath.rename(backup_path)
            backup_created = True
        except Exception as e:
            return [TextContent(
                type="text",
                text=ERROR_BACKUP_FAILED.format(error=str(e))
            )]

    # Write file
    try:
        with open(filepath, 'w') as f:
            f.write(formatted_card)

        backup_msg = "\n✅ Backup created for existing file." if backup_created else ""

        return [TextContent(
            type="text",
            text=RESPONSE_CARD_SAVED.format(
                filepath=filepath,
                backup_msg=backup_msg,
                file_size=len(formatted_card)
            )
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=ERROR_SAVE_FAILED.format(error=str(e))
        )]


# ============================================================================
# Handler Registry
# ============================================================================

TOOL_HANDLERS = {
    # Stage 1: Draft Generation
    "start_draft_generation": handle_start_draft_generation,
    "title_thinker": handle_title_thinker,
    "generate_title": handle_generate_title,
    "content_thinker": handle_content_thinker,
    "generate_content": handle_generate_content,

    # Stage 2: Card Generation
    "start_card_generation": handle_start_card_generation,
    "generate_heading": handle_generate_heading,
    "apply_template": handle_apply_template,
    "save_card": handle_save_card,
}


def dispatch_tool_call(tool_name: str, arguments: dict, config: Config) -> list[TextContent]:
    """Dispatch tool call to appropriate handler.

    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments
        config: Server configuration

    Returns:
        List of TextContent responses
    """
    handler = TOOL_HANDLERS.get(tool_name)

    if handler:
        return handler(arguments, config)
    else:
        return [TextContent(
            type="text",
            text=ERROR_UNKNOWN_TOOL.format(tool_name=tool_name)
        )]
