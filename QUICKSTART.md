# Quick Start Guide

Get up and running with the Zettelkasten MCP Server in 5 minutes.

## Step 1: Install Dependencies

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Step 2: Configure Your Output Directory

Edit `config.yaml` and set your Zettelkasten directory:

```yaml
output_directory: "~/zettelkasten/cards"  # Change this!
template_file: "./template.md"
```

The output directory will be created automatically if it doesn't exist.

## Step 3: Add to Claude Desktop

### macOS

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows

Edit: `%APPDATA%\Claude\claude_desktop_config.json`

### Add this configuration:

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
        "CONFIG_PATH": "/full/path/to/your/config.yaml"
      }
    }
  }
}
```

**Important**: Replace `/full/path/to/your/config.yaml` with the actual absolute path!

To get the path:
```bash
# In this directory, run:
pwd
# Copy the output and append /config.yaml
```

## Step 4: Restart Claude Desktop

Quit Claude Desktop completely and restart it.

## Step 5: Test It!

Open Claude Desktop and try:

```
Generate a Zettelkasten card about the benefits of spaced repetition for learning
```

### Stage 1: Draft Generation

Claude will automatically:
1. **Think about the title** (title_thinker)
2. **Generate title**: `Spaced Repetition Learning Benefits`
3. **Think about content** (content_thinker)
4. **Generate draft content** as a narrative article
5. **Show preview**: "The draft generation workflow is completed."

### User Review

Now you:
1. Review the draft content
2. Request changes if needed ("make it more technical", "add examples", etc.)
3. When ready, add tags and proceed:

```
Tags: #Learning #CognitiveScience #Memory
Generate the card.
```

### Stage 2: Card Formatting

Claude will:
1. **Route**: Decide if heading is needed
2. **Generate heading** (if needed): "Spaced Repetition: Leveraging the Forgetting Curve for Long-Term Memory Retention"
3. **Apply template**: Format with frontmatter and timestamps
4. **Save card**: `20251023120530 - Spaced Repetition Learning Benefits.md`

```
Card saved successfully.

Location: ~/zettelkasten/cards/20251023120530 - Spaced Repetition Learning Benefits.md
File Size: 1247 characters

Your Zettelkasten card is ready. You can view or edit it anytime.
```

Done! Your card is saved with:
- Frontmatter (title, tags, timestamps)
- Optional detailed heading
- Content synthesized from your conversation
- Related Concepts and References sections

## Troubleshooting

### "Template not found"

- Check that `template.md` exists in the project root
- Verify `template_file` path in `config.yaml`
- Ensure the path is correct (relative or absolute)

### "Error saving card"

- Verify `output_directory` path in `config.yaml`
- Ensure directory is writable
- Check for typos in the path
- Try using absolute path instead of `~/`

### Claude doesn't see the tools

- Restart Claude Desktop **completely** (quit and reopen)
- Check the CONFIG_PATH in `claude_desktop_config.json`
- Make sure you used an **absolute path** (not `./config.yaml`)
- Verify Python is in your PATH

### Check if server is running

Look for the Zettelkasten tools in Claude Desktop:
- start_draft_generation
- title_thinker
- generate_title
- content_thinker
- generate_content
- start_card_generation
- generate_heading
- apply_template
- save_card

### Where are the logs?

**macOS**: `~/Library/Logs/Claude/`

**Windows**: `%APPDATA%\Claude\logs\`

Look for error messages related to the zettelkasten server.

## Understanding the Workflow

### Stage 1: Draft Generation (Content First)

This stage focuses purely on **content creation**:

- **Purpose**: Generate quality content without worrying about formatting
- **Think Tools**: Claude explicitly reasons about title and content before generating
- **Output**: Draft content ready for your review
- **User Control**: You can iterate on content, request changes, refine before proceeding

**Why separate stages?** Content and formatting are different concerns. By separating them, you can:
1. Focus on getting the content right first
2. Iterate on content without re-formatting
3. Add your personal tags after reviewing
4. Proceed to formatting only when satisfied

### Stage 2: Card Formatting (Format Second)

This stage focuses on **presentation**:

- **Purpose**: Format the finalized content into a proper Zettelkasten card
- **Router Pattern**: Decides what's needed (heading or not)
- **Template Application**: Adds timestamps, frontmatter, structure
- **Output**: Saved card file with proper naming

**Why routing?** Not all cards need a detailed heading. The router pattern lets Claude decide based on content complexity.

## Tips for Better Cards

### 1. Be Specific with Topics

**Good**: "MCP tool chaining patterns for sequential workflows"
**Poor**: "MCP stuff" or "Some programming thing"

Specific topics lead to better titles and more focused content.

### 2. Engage in Dialogue First

The best cards come from **actual conversations**:
- Discuss the topic with Claude first
- Ask questions, explore nuances
- Then say "create a card about this conversation"

The narrative synthesis will capture your inquiry path naturally.

### 3. Review Before Proceeding

Stage 1 is your checkpoint:
- Read the draft carefully
- Request changes: "make it more technical", "add an example about X"
- Iterate until satisfied
- **Then** proceed to Stage 2

### 4. Use Your Tag System

Tags are personal:
- Use your existing tag structure
- Be consistent with tag names
- Consider hierarchies: `#Tech/MCP` or `#Learning/Memory`

### 5. Link Cards Together

After saving, use the "Related Concepts" section to link cards:
- Reference other card IDs
- Build your knowledge graph
- Create meaningful connections

## Next Steps

### Customize Your Setup

- **Edit template.md**: Adjust frontmatter, add custom sections
- **Modify prompts**: Edit `responses.py` to change generation style
- **Configure naming**: Review `config/naming-conventions.md`

### Build Your Zettelkasten

- Create cards regularly during learning
- Link related concepts together
- Review and refine existing cards
- Let your knowledge graph grow organically

### Advanced Usage

- Experiment with different conversation styles
- Try creating cards from meeting notes
- Generate literature note cards from papers
- Build project-specific card collections

## Example Card Types

### Concept Cards
```
You: Explain the testing pyramid concept
[Discuss, refine understanding]
You: Create a card. Tags: #Testing #SoftwareEngineering
```

### Meeting Notes
```
You: I just had a meeting about API design decisions...
[Capture key points]
You: Create a card from this. Tags: #Meetings #APIDesign
```

### Learning Notes
```
You: I'm learning about neural networks. Let's discuss backpropagation...
[Deep dive conversation]
You: Create a card summarizing our discussion. Tags: #MachineLearning #AI
```

### Literature Notes
```
You: I read this paper about attention mechanisms in transformers...
[Discuss paper insights]
You: Create a literature note card. Tags: #Papers #DeepLearning
```

## Getting Help

- **Issues**: Report at [GitHub Issues](https://github.com/yourusername/zettelkasten-card-mcp/issues)
- **Logs**: Always check logs first for error messages
- **Documentation**: See README.md for architecture details

Enjoy building your Zettelkasten!
