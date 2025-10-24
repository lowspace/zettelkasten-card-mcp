# Zettelkasten Card MCP Server

An MCP (Model Context Protocol) server that enables AI assistants to help you create well-structured Zettelkasten cards through a guided, inspectable workflow.

## Overview

This server implements a **tool-driven workflow** with **embedded prompts** to create Zettelkasten cards automatically while maintaining full transparency and user control. Unlike traditional MCP designs that rely on Resources or Prompts, this system uses tool chaining to guide Claude through a complete card creation process.

### Key Features

- **Two-Stage Workflow**: Separate content creation from formatting for efficient iteration
- **Inspectable**: AI reasoning visible through "think tools" at each stage
- **Stateless Server**: Compatible with multiple MCP clients
- **User Control**: Manual tagging and content review checkpoints
- **Single Template System**: Unified template with optional heading support
- **Embedded Prompts**: Detailed generation instructions loaded only when needed
- **Narrative Synthesis**: Converts conversations into flowing first-person articles

## Installation

### Prerequisites

- Python 3.12 or higher
- pip or uv package manager

### Install Dependencies

Using pip:
```bash
pip install -e .
```

Using uv:
```bash
uv pip install -e .
```

### Configure Output Directory

Edit `config.yaml` to set your Zettelkasten directory:

```yaml
output_directory: "~/zettelkasten/cards"  # Change this to your directory
template_file: "./template.md"
```

### Add to Claude Desktop

Add this server to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "python",
      "args": [
        "-m",
        "zettelkasten_mcp.server"
      ],
      "env": {
        "CONFIG_PATH": "/absolute/path/to/config.yaml"
      }
    }
  }
}
```

Replace `/absolute/path/to/config.yaml` with the actual path to your config file.

## Usage

### Basic Workflow

1. **Start a conversation with Claude Desktop**

2. **Request a card**: "Generate a Zettelkasten card about [topic]"

3. **Stage 1 - Draft Generation**:
   - Claude will automatically call the workflow tools
   - Title thinking → Title generation
   - Content thinking → Content generation
   - Draft preview

4. **User Review**:
   - Review the generated draft
   - Request changes if needed
   - Add your personal tags (e.g., `#SoftwareEngineering #MCP`)

5. **Stage 2 - Card Formatting**:
   - Say "generate card" with your tags
   - Claude decides if heading is needed
   - Optional: Generates detailed heading
   - Applies template with timestamps and saves directly
   - Card saved (no preview - check locally for efficiency)

### Example Interaction

```
You: Generate a Zettelkasten card about MCP tool-driven workflows

Claude: [Automatically goes through Stage 1 workflow]
- Thinks about title framing
- Generates: "MCP Tool Driven Sequential Workflow"
- Thinks about content structure
- Generates draft content synthesizing our conversation
- Shows preview

Claude: The draft generation workflow is completed. Please review and provide feedback or tags.

You: Looks great! Tags: #MCP #WorkflowDesign #SoftwareEngineering
     Generate the card.

Claude: [Stage 2 workflow]
- Decides heading is needed
- Generates detailed heading
- Applies template with timestamp: 20251023120530
- Formats and saves card

Claude: Card saved: ~/zettelkasten/cards/20251023120530 - MCP Tool Driven Sequential Workflow.md

1247 characters written.
```

## Architecture

### Two-Stage Design

**Stage 1: Draft Generation**
```
Input:  User query or topic
Process: Think → Generate title → Think → Generate content
Output: Draft content for review
User Action: Review, request changes, add tags
```

**Stage 2: Card Formatting**
```
Input:  Draft + Title + User Tags + User Feedback
Process: Router (heading decision) → [Optional: Generate heading] → Apply template (formats + saves)
Output: Saved Zettelkasten card with timestamp
Note: No preview shown - users check cards locally for better token efficiency
```

### Tool Chain

The workflow follows this simplified chain:

```
Stage 1 (5 tools):
start_draft_generation → title_thinker → generate_title
→ content_thinker → generate_content

[User Review & Tag Addition]

Stage 2 (3 tools - optimized):
start_card_generation → [optional: generate_heading]
→ apply_template (formats and saves directly)
```

### Key Innovations

1. **Think Tools**: No-op tools that force Claude to articulate reasoning before generation
2. **Embedded Prompts**: Detailed prompts returned in tool responses (not in system prompt)
3. **Router Pattern**: Decides optional steps (like heading generation) based on content
4. **Stateless Server**: All context flows through tool calls and responses
5. **Narrative Synthesis**: Converts dialogue into cohesive first-person article format

## Configuration

### Directory Structure

```
zettelkasten-card-mcp/
├── config.yaml                      # Main configuration
├── template.md                      # Single unified template
├── config/
│   └── naming-conventions.md       # Card naming guidelines
└── zettelkasten_mcp/               # Server code
    ├── server.py                   # MCP server and tool definitions
    ├── handlers.py                 # Tool handler functions
    ├── responses.py                # All text templates and prompts
    └── config.py                   # Configuration management
```

### Template System

The template (`template.md`) uses these placeholders:

- `{{title}}` - Card title
- `{{heading}}` - Optional detailed heading (line removed if not provided)
- `{{content}}` - Main content body
- `{{tags}}` - User-provided tags
- `{{timestamp}}` - Compact timestamp (YYYYMMDDHHMMSS)
- `{{created_at}}` - ISO format timestamp with timezone

**Template Structure**:
```markdown
---
uid: {timestamp}
aliases:
  - "[]"
created: {created_at}
tags:
citekey:
source:
---

# {heading}

{content}
```

If no heading is generated, the `# {{heading}}` line is automatically removed.

### Filename Format

Cards are saved with the format: `YYYYMMDDHHMMSS - Card Title.md`

Example: `20251023120530 - MCP Tool Driven Sequential Workflow.md`

## Design Philosophy

### User Agency First

- **Manual Tagging**: Respects personal tag systems (too personal to automate)
- **Review Checkpoints**: User reviews draft before formatting
- **Flexible Workflow**: Optional heading generation based on content needs

### Transparency

- **Think Tools**: Show Claude's reasoning before generation
- **Workflow Visibility**: Each step clearly communicated
- **Tool Chaining**: Predictable, inspectable flow

### Efficiency

- **Two Stages**: Finalize content once, then format
- **Embedded Prompts**: Load instructions only when needed
- **Smart Routing**: Skip unnecessary steps (e.g., heading when not needed)

### Content Quality

- **Narrative Synthesis**: Converts dialogue into flowing articles
- **Atomic Notes**: Each card focuses on single concept
- **Human Perspective**: Content written from user's viewpoint (first-person)

## Development

### Project Structure

- `zettelkasten_mcp/server.py` - Main MCP server and tool definitions
- `zettelkasten_mcp/handlers.py` - Individual handler functions for each tool
- `zettelkasten_mcp/responses.py` - All prompts and response templates
- `zettelkasten_mcp/config.py` - Configuration management
- `template.md` - Single unified card template
- `config/` - Configuration files and conventions

### Handler Pattern

Each tool follows this pattern in `handlers.py`:

```python
def handle_tool_name(arguments: dict, config: Config) -> list[TextContent]:
    """Handle tool_name tool call."""
    # Extract arguments
    param = arguments["param"]

    # Process logic
    result = process(param)

    # Return response with embedded prompt or next action
    return [TextContent(
        type="text",
        text=RESPONSE_TEMPLATE.format(result=result, next_tool="next_tool_name")
    )]
```

All tools are registered in `TOOL_HANDLERS` dictionary for dispatch.

### Adding New Tools

1. Define tool in `server.py` `list_tools()`
2. Create handler function in `handlers.py`
3. Add prompt/response template in `responses.py`
4. Register handler in `TOOL_HANDLERS` dictionary
5. Follow pattern: return response with next action instruction

## Troubleshooting

### Card Not Saved

- Check `output_directory` in `config.yaml`
- Ensure directory exists and is writable
- Check Claude Desktop logs for errors

### Template Not Found

- Verify `template_file` path in `config.yaml`
- Ensure `template.md` exists
- Check file permissions

### Workflow Stuck

- Claude should follow `next_tool` instructions automatically
- If stuck, you can manually guide: "Call [tool_name]"
- Restart conversation if needed

### Missing Tools in Claude

- Restart Claude Desktop completely
- Check config path is absolute (not relative)
- Review Claude Desktop logs for server startup errors

### Logs Location

**macOS**: `~/Library/Logs/Claude/`

**Windows**: `%APPDATA%\Claude\logs\`

## Credits

Based on the Zettelkasten method of knowledge management, this server implements a novel MCP design pattern using tool-driven workflows and embedded prompts for automated yet transparent card creation.

## License

MIT License - See LICENSE file for details
