# Zettelkasten Card MCP Server

An MCP (Model Context Protocol) server that helps you capture insights from long AI conversations as permanent Zettelkasten notes.

## Why This Exists

**Problem**: During long AI conversations, you gain valuable insights but they get lost in the chat history. You want to capture specific concepts as permanent, atomic notes.

**Solution**: This MCP server is your **copilot for distilling insights**. When YOU decide something is worth saving, say "create a card about X" and it helps you synthesize that specific topic into a standalone note.

**Core Motivation**: Give you control over what to capture. The AI doesn't decide for you—it helps when you're ready to distill.

**Important**: This is a user-initiated tool. The AI won't automatically suggest or create cards. You decide what's worth capturing and when.

## See It In Action

**During an AI conversation:**

```
You: Can you explain how MCP servers maintain state across tool calls?

AI: [Detailed explanation about stateless design, context flow, patterns...]

You: This is really helpful. Create a Zettelkasten card about "MCP stateless design patterns"

AI: [Stage 1: Draft Generation]
    - Thinking about title...
    - Generated: "MCP Stateless Design Patterns"
    - Thinking about content structure...
    - Generating content by synthesizing our discussion...

    Draft complete. Here's what I created:

    Title: MCP Stateless Design Patterns
    Content: [Shows synthesized narrative article]

    Review the draft and provide tags when ready.

You: Looks good! Tags: #MCP #Architecture #Patterns

AI: [Stage 2: Card Formatting]
    - Deciding if heading needed...
    - Generating detailed heading...
    - Applying template with timestamp...

    Card saved: 20251024150530 - MCP Stateless Design Patterns.md
```

**Result**: A permanent, atomic note in your Zettelkasten—captured from our conversation, ready to link with other notes.

---

**Another quick example:**

```
You: [After discussing database indexing for 10 minutes]
     Create a card about "B-tree index tradeoffs"

AI: [Generates draft → you review → add tags → saves]
    Card saved: 20251024151230 - B-tree Index Tradeoffs.md
```

**That's it.** You decide what to capture, AI helps you distill it. Your knowledge, your control.

## Key Features

- **User-Initiated**: You decide what and when to capture—AI doesn't auto-suggest
- **Two-Stage Workflow**: Draft generation (content) → Card formatting (save)
- **Review Checkpoint**: You approve content and add tags before saving
- **Narrative Synthesis**: Converts dialogue into flowing first-person articles
- **Atomic Notes**: One concept per card, focused and self-contained
- **Think Tools**: AI reasoning visible at each step
- **Token Optimized**: No unnecessary previews (~180-230 tokens saved per card)
- **Template Support**: Use default or specify your own template
- **Stateless Design**: Works with any MCP client

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
template_file: "./template.md"             # Optional: use custom template
```

### Add to MCP Client

**For Claude Desktop:**

Add this server to your configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "/full/path/to/python3",
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

Replace `/full/path/to/python3` with your Python path (run `which python3` to find it).

Replace `/absolute/path/to/config.yaml` with the actual path to your config file.

### Restart Your MCP Client

Quit and restart your MCP client (e.g., Claude Desktop) to load the server.

## Usage

### Basic Workflow

1. **Have a conversation** with your AI assistant about any topic
2. **When YOU decide to capture something**, request a card: "Create a Zettelkasten card about [concept]"
3. **Review the draft** - AI shows you the generated title and content
4. **Add your tags** - Provide your personal tags (e.g., `#Learning #Databases`)
5. **Done** - Card is saved with timestamp to your Zettelkasten directory

**Remember**: The AI is your copilot. It waits for your command. You decide what's worth capturing.

### Tips

**Be specific**: "Create a card about recursion base cases" is better than "make a card about recursion"

**Engage first**: Have a meaningful discussion, then capture the insight

**Review carefully**: Stage 1 gives you a checkpoint to refine before saving

**Use your tags**: Tags are personal—use your own system

**Link cards**: Reference other card IDs in the content to build your knowledge graph

## Configuration

### Template System

The server uses a single template file with placeholders:

**Default template** (`template.md`):
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

**Placeholders**:
- `{timestamp}` - Compact timestamp (YYYYMMDDHHMMSS)
- `{created_at}` - ISO format timestamp with timezone
- `{heading}` - Optional detailed heading (line removed if not generated)
- `{content}` - Main content body
- `tags:` - Left empty for you to fill manually

**Custom Template**:

You can specify your own template in `config.yaml`:

```yaml
template_file: "/path/to/your/custom_template.md"
```

Use the same `{placeholder}` format (single braces) in your custom template.

### Filename Format

Cards are saved as: `YYYYMMDDHHMMSS - Card Title.md`

Example: `20251024150530 - MCP Stateless Design Patterns.md`

### Directory Structure

```
zettelkasten-card-mcp/
├── config.yaml                  # Configuration
├── template.md                  # Default template
├── zettelkasten_mcp/           # Server code
│   ├── server.py               # MCP server and tool definitions
│   ├── handlers.py             # Tool handler functions
│   ├── responses.py            # Prompts and response templates
│   └── config.py               # Configuration management
└── docs/                       # Documentation
```

## Workflow Details

### Stage 1: Draft Generation (5 tools)

```
start_draft_generation → title_thinker → generate_title
→ content_thinker → generate_content
```

**What happens**:
- AI thinks about the title, then generates it
- AI thinks about content structure, then generates narrative article
- You see the complete draft for review

### Stage 2: Card Formatting (3 tools)

```
start_card_generation → [optional: generate_heading]
→ apply_template (formats + saves)
```

**What happens**:
- AI decides if a detailed heading is needed
- Applies your template with timestamps
- Saves directly to your Zettelkasten directory
- No preview (you can open the file locally)

### Token Optimization

**No preview in Stage 2**: Saves ~150 tokens per card. You review the draft in Stage 1, then check the final file locally after saving.

**Merged operations**: `apply_template` now formats and saves in one step (no separate `save_card` tool).

**Total savings**: ~180-230 tokens per card (15-20% reduction).

## Design Philosophy

### User Agency First

- **Manual Tagging**: Your personal tag system, you control it
- **Review Checkpoint**: Stage 1 lets you refine before formatting
- **No AI Tags**: Tags are too personal to automate

### Transparency

- **Think Tools**: See AI reasoning before generation
- **Visible Workflow**: Each step clearly communicated
- **Predictable Flow**: Tool chaining makes the process inspectable

### Content Quality

- **Narrative Synthesis**: Converts dialogue into flowing articles
- **Atomic Notes**: One concept per card, focused and self-contained
- **Human Perspective**: Content written from your viewpoint (first-person)
- **Clean Markdown**: Minimal formatting, emphasis on content

### Efficiency

- **Two Stages**: Finalize content once, then format
- **Embedded Prompts**: Load instructions only when needed
- **Token Optimized**: Skip unnecessary previews and operations
- **Stateless Server**: Works with any MCP client

## Troubleshooting

### Server Not Connecting

- Check Python path is correct: `which python3`
- Verify CONFIG_PATH is absolute (not relative)
- Restart your MCP client completely
- Check logs for errors

### Cards Not Saving

- Verify `output_directory` exists and is writable
- Check `template_file` path is correct
- Ensure placeholders use single braces `{placeholder}`

### Template Not Loading

- If you specify `template_file`: ensure the file exists at that path
- If not specified: default `template.md` in project root is used
- Check for syntax errors in your custom template

### Workflow Stuck

- AI should follow tool workflow automatically
- If stuck, restart the conversation
- Check MCP client logs for tool call errors

### Logs Location

**macOS**: `~/Library/Logs/Claude/`

**Windows**: `%APPDATA%\Claude\logs\`

Look for `mcp*.log` files related to the zettelkasten server.

## Development

### Project Structure

- `zettelkasten_mcp/server.py` - MCP server and tool definitions
- `zettelkasten_mcp/handlers.py` - Tool handler functions (one per tool)
- `zettelkasten_mcp/responses.py` - All prompts and response templates
- `zettelkasten_mcp/config.py` - Configuration loading and validation
- `template.md` - Default card template

### Handler Pattern

Each tool has a handler function:

```python
def handle_tool_name(arguments: dict, config: Config) -> list[TextContent]:
    """Handle tool_name tool call."""
    # Extract arguments
    param = arguments["param"]

    # Process
    result = process(param)

    # Return with embedded prompt or next instruction
    return [TextContent(
        type="text",
        text=RESPONSE_TEMPLATE.format(result=result, next_tool="next_tool_name")
    )]
```

All handlers are registered in `TOOL_HANDLERS` dictionary.

### Adding New Tools

1. Define tool in `server.py` `list_tools()`
2. Create handler function in `handlers.py`
3. Add prompt/response template in `responses.py`
4. Register in `TOOL_HANDLERS` dictionary
5. Follow pattern: return text with next action

## Credits

Built on the Zettelkasten method of knowledge management. Uses MCP for tool-driven workflows with embedded prompts for transparent, automated card creation.

## License

MIT License - See LICENSE file for details
