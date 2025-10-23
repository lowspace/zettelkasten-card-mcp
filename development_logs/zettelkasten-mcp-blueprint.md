# Zettelkasten MCP Server - Project Blueprint

## 1. Project Overview

### 1.1 Purpose
A Model Context Protocol (MCP) server that enables AI assistants to help users create well-structured Zettelkasten cards through a guided, inspectable workflow. The system emphasizes user control over personalized elements (tags) while automating content generation and formatting.

### 1.2 Core Philosophy
- **User-Centric**: Respects personal tag systems and naming conventions
- **Inspectable**: Makes AI reasoning visible through think tools
- **Stateless**: Compatible across different MCP clients
- **Automated**: Minimizes manual intervention while maintaining quality
- **Modular**: Clear separation between content generation and formatting

### 1.3 Key Innovation
Unlike traditional MCP designs that rely on Resources (user-triggered) or Prompts (user-selected), this system uses **tool-driven workflows** with **embedded prompts** to achieve full automation while maintaining inspectability.

---

## 2. Design Principles

### 2.1 Two-Stage Architecture

```
Stage 1: Draft Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  User topic
Process: Generate title + content draft
Output: Plain text draft (no formatting)
Control: User reviews, edits, adds tags manually

Stage 2: Card Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  Draft + Title + User tags
Process: 
  - Title reflection (optional modification)
  - Content reflection (optional modification)  
  - Heading reflection (optional generation)
  - Template selection
  - Apply template with timestamp
Output: Formatted card saved to filesystem
```

**Rationale**: Separating content from format allows users to finalize content before committing to a structure, enabling "one-time edit, final version" efficiency.

### 2.2 Fixed Workflow Chain

Each tool returns explicit `next_action` instructions, creating a deterministic execution path:

```
start_draft_generation 
  → title_thinker 
  → generate_title 
  → commit_title 
  → content_thinker 
  → generate_content 
  → commit_draft
  → [User Review & Tag Addition]
  → start_card_generation
  → title_reflection → [optional: generate_title → commit_title]
  → content_reflection → [optional: generate_content → commit_content]
  → heading_reflection → [optional: generate_heading → commit_heading]
  → template_selector
  → apply_template (receives all components at once)
  → save_card
```

### 2.3 Think Tools (No-op with Purpose)

Think tools serve three purposes:
1. **Force segmented thinking**: Claude focuses on one aspect at a time
2. **Inspectability**: Tool call parameters show Claude's reasoning
3. **Workflow checkpoints**: Mark completion of thinking phases

Design pattern:
```typescript
// Think tool is no-op but records context
title_thinker(context_summary) 
  → Returns: { next_action: "generate_title" }

// Generator tool provides embedded prompt
generate_title()
  → Returns: { embedded_prompt: "...", next_action: "commit_title" }
```

### 2.4 Embedded Prompts

**Problem**: MCP tool descriptions become part of system prompt, polluting context.

**Solution**: Generator tools return detailed prompts in their response:

```json
{
  "embedded_prompt": "Detailed 500-word generation instructions...",
  "next_action": { "tool": "commit_title" }
}
```

**Benefits**:
- ✅ Prompts loaded only when needed
- ✅ No system prompt pollution
- ✅ Dynamic and contextual
- ✅ Can include user-specific conventions

### 2.5 Stateless Server Design

The server does not maintain session state. All context flows through tool calls and responses.

**Implications**:
- Compatible with multiple MCP clients (Claude Desktop, Cursor, Cline, etc.)
- Cannot enforce strict ordering (relies on Claude's adherence)
- Easier to implement and maintain
- Can provide lightweight warnings if steps are skipped

---

## 3. System Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                 MCP Client                          │
│              (Claude Desktop, etc.)                 │
└────────────────────┬────────────────────────────────┘
                     │ MCP Protocol (stdio/SSE)
                     │
┌────────────────────▼────────────────────────────────┐
│            Zettelkasten MCP Server                  │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         Tool Request Handler                │   │
│  │  - start_draft_generation                   │   │
│  │  - title_thinker / generate_title           │   │
│  │  - content_thinker / generate_content       │   │
│  │  - start_card_generation                    │   │
│  │  - template_selector / apply_template       │   │
│  │  - save_card                                │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         Configuration Manager               │   │
│  │  - Load config.yaml                         │   │
│  │  - Template discovery                       │   │
│  │  - Path validation                          │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         File System Manager                 │   │
│  │  - Read templates                           │   │
│  │  - Write cards                              │   │
│  │  - Path safety checks                       │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │
                     │ Standard FS APIs
                     │ (Node.js fs / Python open)
                     │
┌────────────────────▼────────────────────────────────┐
│              Local File System                      │
│                                                     │
│  ./templates/          ~/zettelkasten/cards/       │
│  ├── general.md        ├── 20251021-Title.md       │
│  ├── meeting.md        └── ...                     │
│  └── ...                                           │
│                                                     │
│  config.yaml                                       │
└─────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
User Query
    ↓
Claude (MCP Client)
    ↓ Tool Call Request
MCP Server
    ↓ Process & Generate Response
    ↓ (Read config/templates if needed)
File System
    ↓
MCP Server
    ↓ Tool Call Response (with next_action)
Claude
    ↓ Execute next_action
    ↓ Repeat until workflow complete
Final Card Saved to File System
```

---

## 4. Workflow Specifications

### 4.1 Stage 1: Draft Generation

#### 4.1.1 Start Workflow

**Tool**: `start_draft_generation(topic: string)`

**Logic**:
- Initialize workflow context
- Return instruction to call `title_thinker`

**Response**:
```json
{
  "status": "workflow_started",
  "topic": "MCP",
  "next_action": {
    "tool": "title_thinker",
    "instruction": "Please call title_thinker with your understanding of the conversation context."
  }
}
```

#### 4.1.2 Title Thinking Phase

**Tool**: `title_thinker(context_summary: string)`

**Logic**:
- Record the context summary (no-op, just logging)
- Return instruction to call `generate_title`

**Response**:
```json
{
  "thinking_recorded": true,
  "context_summary": "User provided summary...",
  "next_action": {
    "tool": "generate_title",
    "instruction": "Thinking recorded. Now call generate_title to create the card title."
  }
}
```

#### 4.1.3 Title Generation Phase

**Tool**: `generate_title()`

**Logic**:
- Load naming conventions from config
- Return embedded prompt with detailed instructions
- Provide examples

**Response**:
```json
{
  "embedded_prompt": "You are generating a Zettelkasten card title.\n\nNaming Convention:\n- Format: YYYYMMDD-CoreConcept\n- Length: 20-40 characters\n- Atomic: One card, one concept\n- Self-explanatory: Title alone should convey the topic\n\nExamples:\n- 20251021-MCP-Tool-Driven-Design\n- 20251021-State-Machine-Patterns-in-Workflows\n\nBased on your earlier thinking, generate a concise title.\nThen call commit_title to submit it.",
  "naming_conventions": "[Full conventions from file]",
  "examples": ["20251021-Example1", "20251021-Example2"],
  "next_action": {
    "tool": "commit_title",
    "instruction": "After generating the title, call commit_title with it."
  }
}
```

#### 4.1.4 Title Commit Phase

**Tool**: `commit_title(title: string)`

**Logic**:
- Validate title format
- Store title in workflow context
- Return instruction for next phase

**Response**:
```json
{
  "status": "title_confirmed",
  "title": "20251021-MCP-Tool-Driven-Sequential-Workflow",
  "next_action": {
    "tool": "content_thinker",
    "instruction": "Title confirmed. Now call content_thinker to plan the content."
  }
}
```

#### 4.1.5 Content Thinking Phase

**Tool**: `content_thinker(title: string, key_points: string[])`

**Logic**:
- Record the identified key points (no-op)
- Return instruction to call `generate_content`

**Response**:
```json
{
  "thinking_recorded": true,
  "title": "20251021-MCP-Tool-Driven-Sequential-Workflow",
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "next_action": {
    "tool": "generate_content",
    "instruction": "Key points recorded. Now call generate_content to create the draft."
  }
}
```

#### 4.1.6 Content Generation Phase

**Tool**: `generate_content()`

**Logic**:
- Return embedded prompt with content generation instructions
- Include confirmed title for context
- Provide structure guidance

**Response**:
```json
{
  "embedded_prompt": "You are generating draft content for the card titled '20251021-MCP-Tool-Driven-Sequential-Workflow'.\n\nRequirements:\n- Plain text, no formatting (no markdown headings)\n- Extract key information, arguments, and examples from the conversation\n- Clear logic, well-organized paragraphs\n- Length: 300-800 words\n\nContent should include:\n1. Problem context (why this design is needed)\n2. Solution approach (how it works)\n3. Key design points (core mechanisms)\n4. Practical applications (specific scenarios)\n\nBased on the key points you identified, generate complete draft content.\nThen call commit_draft to submit it.",
  "confirmed_title": "20251021-MCP-Tool-Driven-Sequential-Workflow",
  "key_points_reminder": ["..."],
  "next_action": {
    "tool": "commit_draft",
    "instruction": "After generating content, call commit_draft with it."
  }
}
```

#### 4.1.7 Draft Commit Phase

**Tool**: `commit_draft(content: string)`

**Logic**:
- Store draft content
- Calculate word count
- Return preview and instructions for user review

**Response**:
```json
{
  "status": "draft_completed",
  "draft": {
    "title": "20251021-MCP-Tool-Driven-Sequential-Workflow",
    "content": "[Full draft content]",
    "word_count": 654
  },
  "message": "✅ Draft generation complete!\n\n📋 Content Preview:\n[First 200 words...]\n\n⏸️ Next Steps:\n1. Review the content, tell me if changes are needed\n2. Manually add appropriate tags (e.g., #SoftwareEngineering #MCP)\n3. When ready, say 'generate card' to proceed to Stage 2",
  "next_stage": "card_generation"
}
```

---

### 4.2 Stage 2: Card Generation

#### 4.2.1 Start Card Generation

**Tool**: `start_card_generation(draft_content: string, title: string, tags: string[])`

**Logic**:
- Receive user-modified draft and user-provided tags
- Initialize card generation workflow
- Return instruction to reflect on title

**Response**:
```json
{
  "status": "card_generation_started",
  "received": {
    "title": "20251021-MCP-Tool-Driven-Sequential-Workflow",
    "content_length": 654,
    "tags": ["#MCP", "#WorkflowDesign"]
  },
  "next_action": {
    "tool": "title_reflection",
    "instruction": "Reflect on whether the title needs modification based on user feedback or content analysis."
  }
}
```

#### 4.2.2 Title Reflection Phase

**Tool**: `title_reflection(original_title: string, user_feedback?: string)`

**Logic**:
- Evaluate if title accurately represents the content
- Consider user feedback if provided
- Determine if modification is needed
- Return decision with reasoning

**Response** (if no modification needed):
```json
{
  "needs_modification": false,
  "reasoning": "Title accurately captures the core concept. No modification needed.",
  "next_action": {
    "tool": "content_reflection",
    "instruction": "Title confirmed. Proceed to reflect on content."
  }
}
```

**Response** (if modification needed):
```json
{
  "needs_modification": true,
  "reasoning": "User feedback suggests emphasizing 'stateless' aspect. Title should be adjusted.",
  "next_action": {
    "tool": "generate_title",
    "instruction": "Generate revised title addressing the feedback."
  }
}
```

#### 4.2.3 Title Generation Phase (Optional)

**Tool**: `generate_title()`

**Logic**:
- Provide embedded prompt for title regeneration
- Consider user feedback and content analysis
- Return new title generation instructions

**Response**:
```json
{
  "embedded_prompt": "Regenerate the card title based on user feedback.\n\nOriginal title: 20251021-MCP-Tool-Driven-Sequential-Workflow\nFeedback: Emphasize stateless design aspect\n\nNaming Convention:\n- Format: YYYYMMDD-CoreConcept\n- Length: 20-40 characters\n- Atomic and self-explanatory\n\nGenerate improved title, then call commit_title.",
  "next_action": {
    "tool": "commit_title",
    "instruction": "After generating new title, call commit_title to confirm it."
  }
}
```

**Tool**: `commit_title(title: string)`

**Response**:
```json
{
  "status": "title_confirmed",
  "title": "20251021-MCP-Stateless-Sequential-Workflow",
  "next_action": {
    "tool": "content_reflection",
    "instruction": "Title finalized. Proceed to reflect on content."
  }
}
```

#### 4.2.4 Content Reflection Phase

**Tool**: `content_reflection(original_content: string, user_feedback?: string)`

**Logic**:
- Evaluate if content needs revision
- Consider user feedback if provided
- Determine if modification is needed
- Return decision with reasoning

**Response** (if no modification needed):
```json
{
  "needs_modification": false,
  "reasoning": "Content is well-structured and complete. No changes needed.",
  "next_action": {
    "tool": "heading_reflection",
    "instruction": "Content confirmed. Proceed to reflect on whether heading is needed."
  }
}
```

**Response** (if modification needed):
```json
{
  "needs_modification": true,
  "reasoning": "User requested adding more examples. Content should be expanded.",
  "next_action": {
    "tool": "generate_content",
    "instruction": "Generate revised content addressing the feedback."
  }
}
```

#### 4.2.5 Content Generation Phase (Optional)

**Tool**: `generate_content()`

**Logic**:
- Provide embedded prompt for content regeneration
- Consider user feedback
- Return new content generation instructions

**Response**:
```json
{
  "embedded_prompt": "Regenerate the content based on user feedback.\n\nOriginal content: [draft content]\nFeedback: Add more concrete examples\n\nRequirements:\n- Plain text, no formatting\n- Include 2-3 concrete examples\n- Maintain logical structure\n- Length: 300-800 words\n\nGenerate improved content, then call commit_content.",
  "next_action": {
    "tool": "commit_content",
    "instruction": "After generating new content, call commit_content to confirm it."
  }
}
```

**Tool**: `commit_content(content: string)`

**Response**:
```json
{
  "status": "content_confirmed",
  "content_length": 712,
  "next_action": {
    "tool": "heading_reflection",
    "instruction": "Content finalized. Proceed to reflect on whether heading is needed."
  }
}
```

#### 4.2.6 Heading Reflection Phase

**Tool**: `heading_reflection(title: string, content_summary: string)`

**Logic**:
- Analyze if card title sufficiently describes content
- Consider if a more detailed content heading would be beneficial
- Determine if heading is needed (optional, not mandatory)
- Return decision with reasoning

**Response** (if heading needed):
```json
{
  "needs_heading": true,
  "reasoning": "Card title is abbreviated for filename format (YYYYMMDD-CoreConcept). Content discusses specific mechanism ('tool-returned process instructions') that deserves fuller explanation in heading.",
  "next_action": {
    "tool": "generate_heading",
    "instruction": "Generate detailed content heading."
  }
}
```

**Response** (if heading not needed):
```json
{
  "needs_heading": false,
  "reasoning": "Card title is already sufficiently descriptive. Content heading would be redundant.",
  "next_action": {
    "tool": "template_selector",
    "instruction": "No heading needed. Proceed to template selection."
  }
}
```

#### 4.2.7 Heading Generation Phase (Optional)

**Tool**: `generate_heading()`

**Logic**:
- Provide embedded prompt for heading generation
- Generate more detailed heading than card title
- Return heading generation instructions

**Response**:
```json
{
  "embedded_prompt": "Generate a detailed content heading.\n\nCard title: 20251021-MCP-Stateless-Sequential-Workflow\nContent summary: Discusses how MCP implements stateless sequential workflows through tool-returned process instructions\n\nRequirements:\n- More detailed than card title (no filename constraints)\n- Accurately describes the core mechanism\n- Length: 40-100 characters\n\nGenerate heading, then call commit_heading.",
  "next_action": {
    "tool": "commit_heading",
    "instruction": "After generating heading, call commit_heading to confirm it."
  }
}
```

**Tool**: `commit_heading(heading: string)`

**Response**:
```json
{
  "status": "heading_confirmed",
  "heading": "MCP: Implementing Stateless Sequential Workflows Through Tool-Returned Process Instructions",
  "next_action": {
    "tool": "template_selector",
    "instruction": "Heading finalized. Proceed to template selection."
  }
}
```

#### 4.2.8 Template Selection Phase

**Tool**: `template_selector(title: string, tags: string[])`

**Logic**:
- Analyze title and tags
- Load template mapping rules from config (if exists)
- Recommend template based on heuristics
- Return available templates

**Response**:
```json
{
  "recommended": "general",
  "reasoning": "Title and tags indicate a technical concept discussion. No special type indicators (meeting, literature, project). General template is appropriate.",
  "confidence": 0.85,
  "available_templates": ["general", "meeting", "literature", "project"],
  "next_action": {
    "tool": "apply_template",
    "instruction": "Template selected. Call apply_template with all finalized components."
  }
}
```

#### 4.2.9 Template Application Phase

**Tool**: `apply_template(title: string, content: string, heading?: string, template_type: string, tags: string[])`

**Logic**:
- Receive all finalized components in one call (Claude passes everything it saved in context)
- Obtain current timestamp (server-side)
- Load template file from templates directory
- Parse template structure
- Fill in all placeholders: title, content, heading (if provided), tags, timestamp
- Return formatted card

**Response**:
```json
{
  "formatted_card": "[Complete markdown card with template structure]",
  "template_used": "general",
  "timestamp_added": "2025-10-21T18:30:00Z",
  "sections_populated": ["Core Concept", "Detailed Explanation", "Practical Applications", "Related Links"],
  "next_action": {
    "tool": "save_card",
    "instruction": "Card formatted. Call save_card to persist to filesystem."
  }
}
```

#### 4.2.10 Card Save Phase

**Tool**: `save_card(formatted_card: string, filename: string)`

**Logic**:
- Load output directory from config
- Construct full file path
- Perform safety checks (path traversal prevention)
- Check if file exists (optional: create backup)
- Write file to filesystem
- Return success status with file path

**Response**:
```json
{
  "status": "saved",
  "filepath": "~/zettelkasten/cards/20251021-MCP-Stateless-Sequential-Workflow.md",
  "created": true,
  "backup_created": false,
  "message": "✅ Card saved successfully!\n\nLocation: ~/zettelkasten/cards/20251021-MCP-Stateless-Sequential-Workflow.md\n\nYou can view or edit this card anytime."
}
```

---

## 5. Tool Specifications

### 5.1 Stage 1 Tools

| Tool Name | Type | Parameters | Purpose |
|-----------|------|------------|---------|
| `start_draft_generation` | Initiator | `topic: string` | Start the draft generation workflow |
| `title_thinker` | No-op | `context_summary: string` | Record thinking, return next action |
| `generate_title` | Generator | None | Return embedded prompt for title generation |
| `commit_title` | Commit | `title: string` | Store title, advance workflow |
| `content_thinker` | No-op | `title: string, key_points: string[]` | Record thinking, return next action |
| `generate_content` | Generator | None | Return embedded prompt for content generation |
| `commit_draft` | Commit | `content: string` | Store draft, prompt user review |

### 5.2 Stage 2 Tools

| Tool Name | Type | Parameters | Purpose |
|-----------|------|------------|---------|
| `start_card_generation` | Initiator | `draft_content: string, title: string, tags: string[]` | Start card generation workflow |
| `title_reflection` | Reflector | `original_title: string, user_feedback?: string` | Evaluate if title needs modification |
| `generate_title` | Generator | None | Return embedded prompt for title regeneration (optional) |
| `commit_title` | Commit | `title: string` | Confirm finalized title |
| `content_reflection` | Reflector | `original_content: string, user_feedback?: string` | Evaluate if content needs modification |
| `generate_content` | Generator | None | Return embedded prompt for content regeneration (optional) |
| `commit_content` | Commit | `content: string` | Confirm finalized content |
| `heading_reflection` | Reflector | `title: string, content_summary: string` | Evaluate if content heading is needed |
| `generate_heading` | Generator | None | Return embedded prompt for heading generation (optional) |
| `commit_heading` | Commit | `heading: string` | Confirm finalized heading |
| `template_selector` | Analyzer | `title: string, tags: string[]` | Recommend template based on heuristics |
| `apply_template` | Formatter | `title: string, content: string, heading?: string, template_type: string, tags: string[]` | Format all components into templated card, add timestamp |
| `save_card` | Persister | `formatted_card: string, filename: string` | Write card to filesystem |

### 5.3 Utility Tools

| Tool Name | Parameters | Purpose |
|-----------|------------|---------|
| `get_available_templates` | None | List all available templates with descriptions |
| `reset_workflow` | None | Reset workflow state (optional, for error recovery) |

---

## 6. Configuration Design

### 6.1 config.yaml

```yaml
# Minimal configuration file

# Where template files are stored
templates_directory: "./templates"

# Where generated cards are saved
output_directory: "~/zettelkasten/cards"

# Optional: Naming conventions document
naming_conventions_file: "./config/naming-conventions.md"

# Optional: Template mapping rules
template_mapping_file: "./config/template-mapping.yaml"

# Optional: File operation settings
file_operations:
  create_backup: true          # Create .backup before overwriting
  filename_sanitization: true  # Remove unsafe characters from filenames
```

### 6.2 Template Structure

Templates are markdown files with placeholders:

```markdown
# templates/general.md

---
title: {{title}}
tags: {{tags}}
created: {{created}}
---

# {{content_heading}}

## Core Concept

{{core_concept}}

## Detailed Explanation

{{detailed_explanation}}

## Practical Applications

{{practical_applications}}

## Related Links

{{related_links}}

## References

{{references}}
```

### 6.3 Directory Structure

```
zettelkasten-mcp/
├── config.yaml                      # Main configuration
├── config/
│   ├── naming-conventions.md        # Card title naming rules
│   └── template-mapping.yaml        # Template recommendation rules
├── templates/
│   ├── general.md                   # General purpose template
│   ├── meeting.md                   # Meeting notes template
│   ├── literature.md                # Literature notes template
│   └── project.md                   # Project-related template
├── server.ts (or server.py)         # MCP server implementation
└── package.json (or requirements.txt)

User's zettelkasten directory:
~/zettelkasten/
└── cards/
    ├── 20251021-MCP-Tool-Driven-Sequential-Workflow.md
    ├── 20251020-Another-Card.md
    └── ...
```

---

## 7. File System Operations

### 7.1 Permission Model

**Key Understanding**: MCP Server runs as a local process with the user's file system permissions.

```
┌──────────────────────────────────────┐
│  User's Machine                      │
│                                      │
│  MCP Server Process                  │
│  ↓ (runs with user's permissions)   │
│  ↓                                   │
│  Standard FS APIs                    │
│  - Node.js: fs.readFile/writeFile   │
│  - Python: open()/read()/write()    │
│  ↓                                   │
│  Local File System                   │
│  - Read: ./templates/*.md            │
│  - Write: ~/zettelkasten/cards/*.md │
└──────────────────────────────────────┘
```

**No special MCP permissions required** - the server uses standard file APIs available in Node.js or Python.

### 7.2 Read Operations

**Loading Templates**:
1. Server startup: Scan `templates_directory` for .md files
2. Store mapping: `{ "general": "./templates/general.md", ... }`
3. On `apply_template` call: Read the specified template file
4. Parse template structure and prepare for filling

**Loading Configuration**:
1. Server startup: Read `config.yaml`
2. Parse and validate paths
3. Load optional convention files if specified
4. Cache in memory for quick access

### 7.3 Write Operations

**Applying Templates**:
1. Claude calls `apply_template` with all finalized components:
   - title (finalized through reflection/generation)
   - content (finalized through reflection/generation)
   - heading (optional, if needed)
   - template_type (from selector recommendation)
   - tags (user-provided)
2. Server receives everything in ONE call (no prior state needed)
3. Server obtains current timestamp
4. Server reads specified template file from templates_directory
5. Server fills all placeholders:
   - {{title}} → finalized title
   - {{content_heading}} → heading (if provided) or title
   - {{content}} → finalized content
   - {{tags}} → comma-separated tags
   - {{created}} → current timestamp
6. Return formatted card to Claude

**Saving Cards**:
1. Receive formatted card and filename from Claude
2. Load `output_directory` from config
3. Construct full path: `join(output_directory, filename)`
4. Safety checks:
   - Validate filename (no path traversal: ../, ..\)
   - Ensure path is within allowed directory
   - Check if file exists (create backup if configured)
5. Write file using standard FS API
6. Return success status with file path

### 7.4 Safety Measures

```typescript
// Path safety (conceptual logic)
function sanitizeFilename(filename: string): string {
  // Remove dangerous characters
  // Replace spaces with hyphens
  // Ensure .md extension
}

function validatePath(fullPath: string, allowedDir: string): boolean {
  // Ensure fullPath is within allowedDir
  // Prevent path traversal attacks
  // Return false if unsafe
}
```

---

## 8. Message Flow Examples

### 8.1 Complete Stage 1 Flow

```
User: "Generate a card about MCP workflow design"
  ↓
Claude → Server: start_draft_generation(topic="MCP workflow design")
  ↓
Server → Claude: { next_action: "title_thinker" }
  ↓
Claude → Server: title_thinker(context_summary="Discussion covered...")
  ↓
Server → Claude: { next_action: "generate_title" }
  ↓
Claude → Server: generate_title()
  ↓
Server → Claude: { embedded_prompt: "...", next_action: "commit_title" }
  ↓
[Claude generates title using extended thinking]
  ↓
Claude → Server: commit_title(title="20251021-MCP-Tool-Driven-Workflow")
  ↓
Server → Claude: { next_action: "content_thinker" }
  ↓
Claude → Server: content_thinker(title="...", key_points=["..."])
  ↓
Server → Claude: { next_action: "generate_content" }
  ↓
Claude → Server: generate_content()
  ↓
Server → Claude: { embedded_prompt: "...", next_action: "commit_draft" }
  ↓
[Claude generates content using extended thinking]
  ↓
Claude → Server: commit_draft(content="...")
  ↓
Server → Claude: { status: "draft_completed", message: "Please review and add tags" }
  ↓
Claude → User: [Displays draft, waits for user input]
```

### 8.2 Complete Stage 2 Flow

```
User: "Draft looks good. Tags: #SoftwareEngineering #MCP. Generate card."
  ↓
Claude → Server: start_card_generation(draft="...", title="...", tags=["..."])
  ↓
Server → Claude: { next_action: "title_reflection" }
  ↓
Claude → Server: title_reflection(original_title="...", user_feedback=null)
  ↓
Server → Claude: { needs_modification: false, next_action: "content_reflection" }
  ↓
[Claude saves in context: final_title = original_title]
  ↓
Claude → Server: content_reflection(original_content="...", user_feedback=null)
  ↓
Server → Claude: { needs_modification: false, next_action: "heading_reflection" }
  ↓
[Claude saves in context: final_content = original_content]
  ↓
Claude → Server: heading_reflection(title="...", content_summary="...")
  ↓
Server → Claude: { needs_heading: true, reasoning: "...", next_action: "generate_heading" }
  ↓
Claude → Server: generate_heading()
  ↓
Server → Claude: { embedded_prompt: "...", next_action: "commit_heading" }
  ↓
[Claude generates heading using extended thinking]
  ↓
Claude → Server: commit_heading(heading="MCP: Implementing Stateless Workflows...")
  ↓
Server → Claude: { status: "heading_confirmed", next_action: "template_selector" }
  ↓
[Claude saves in context: final_heading = "..."]
  ↓
Claude → Server: template_selector(title="...", tags=["..."])
  ↓
Server → Claude: { recommended: "general", next_action: "apply_template" }
  ↓
[Claude saves in context: selected_template = "general"]
  ↓
Claude → Server: apply_template(
    title=final_title,
    content=final_content,
    heading=final_heading,
    template_type=selected_template,
    tags=user_tags
  )
  ↓
[Server receives all components in ONE call]
[Server obtains timestamp: 2025-10-21T18:30:00Z]
[Server loads template file]
[Server fills all placeholders]
  ↓
Server → Claude: { formatted_card: "...", next_action: "save_card" }
  ↓
Claude → Server: save_card(formatted_card="...", filename="20251021-MCP-Stateless-Workflow.md")
  ↓
Server → Claude: { status: "saved", filepath: "~/zettelkasten/cards/20251021-MCP-Stateless-Workflow.md" }
  ↓
Claude → User: "✅ Card saved successfully!"
```

---

## 9. Design Trade-offs & Decisions

### 9.1 Tags: User Control vs Automation

**Decision**: Let users manually add tags instead of auto-generating them.

**Rationale**:
- Tag systems are highly personal and often cannot be clearly expressed
- Different users have different taxonomies, hierarchies, and conventions
- AI-generated tags might conflict with user's mental model
- Manual tagging ensures consistency with user's existing system

**Trade-off**: Requires one additional user input, but ensures quality and user satisfaction.

### 9.2 Embedded Prompts vs Tool Descriptions

**Decision**: Use embedded prompts in tool return values, not tool descriptions.

**Rationale**:
- Tool descriptions become part of system prompt (context pollution)
- Embedded prompts are loaded only when needed (token efficiency)
- Allows dynamic, context-aware prompts
- Cleaner tool interface

**Trade-off**: Claude might ignore return values, but testing suggests this is rare with clear instructions.

### 9.3 Stateless vs Stateful Server

**Decision**: Stateless server design with workflow guidance through return values.

**Rationale**:
- Compatible with multiple MCP clients (Claude Desktop, Cursor, Cline, etc.)
- Simpler server implementation
- No session management complexity
- Aligns with MCP's design philosophy

**Trade-off**: Cannot enforce strict ordering (relies on Claude's adherence to instructions), but lightweight warnings can be added.

### 9.4 Two-Stage Workflow

**Decision**: Separate draft generation from card formatting.

**Rationale**:
- Users can finalize content before committing to format
- Allows easy iteration on content without reformatting
- Clear mental model: content first, format second
- Supports "one edit, final version" efficiency

**Trade-off**: Adds one transition point, but the clarity is worth it.

### 9.6 State Management: Claude vs Server

**Decision**: Intermediate state (title, content, heading) is managed by Claude, not Server.

**Rationale**:
- Stage 2 involves multiple optional generation steps (title, content, heading)
- Each component may or may not be regenerated based on reflection
- Claude saves finalized components in its conversation context
- `apply_template` receives all components in ONE call
- Server remains completely stateless

**How it works**:
```
Claude's Internal State (in conversation context):
{
  final_title: "20251021-MCP-Stateless-Workflow",
  final_content: "[complete content]",
  final_heading: "MCP: Implementing Stateless Workflows...",  // optional
  selected_template: "general",
  user_tags: ["#MCP", "#WorkflowDesign"]
}

When calling apply_template:
Claude passes ALL components at once →
Server receives everything →
Server adds timestamp →
Server fills template →
No prior state needed
```

**Trade-off**: 
- Requires Claude to track components across tool calls (relies on Claude's context management)
- Server cannot validate "did you call reflection before generation?" (but can warn)
- Benefit: True stateless server, cross-client compatible

### 9.7 Reflection Tools: Optional vs Mandatory

**Decision**: Title/content/heading generation are all optional, triggered by reflection.

**Rationale**:
- Users may be satisfied with Stage 1 draft (no modification needed)
- Reflection tools evaluate necessity before triggering generation
- Heading is particularly optional (only needed if title is too brief)
- Reduces unnecessary generation steps

**Flow**:
```
title_reflection → needs_modification: false → skip generate_title
content_reflection → needs_modification: false → skip generate_content  
heading_reflection → needs_heading: false → skip generate_heading

Only generate when truly needed.
```

**Trade-off**: More tool calls (reflection + optional generation), but better UX (no unnecessary regeneration).

---

## 10. Feasibility Analysis

### 10.1 Technical Feasibility: ✅ High

| Aspect | Feasibility | Notes |
|--------|-------------|-------|
| File System Access | ✅ Fully Feasible | Standard Node.js/Python FS APIs, no special permissions needed |
| MCP Protocol | ✅ Fully Feasible | Well-documented, mature protocol with SDKs |
| Tool Chaining | ✅ Fully Feasible | Proven pattern, Claude follows next_action instructions reliably |
| Template System | ✅ Fully Feasible | Simple string substitution or parser-based approach |
| Configuration | ✅ Fully Feasible | Standard YAML parsing, widespread library support |
| State Management | ✅ Fully Feasible | Claude manages intermediate state in context, Server receives all in apply_template |

### 10.2 Architectural Feasibility: ✅ High

| Aspect | Feasibility | Notes |
|--------|-------------|-------|
| Stateless Design | ✅ Fully Feasible | No session state needed, all context in tool responses |
| Embedded Prompts | ✅ Fully Feasible | Claude reads and follows tool return values |
| Two-Stage Workflow | ✅ Fully Feasible | Clear separation, natural user interaction points |
| Think Tools | ✅ Fully Feasible | No-op tools are valid MCP pattern |

### 10.3 User Experience Feasibility: ✅ High

| Aspect | Feasibility | Notes |
|--------|-------------|-------|
| Automation Level | ✅ Optimal | Minimal user input (topic → tags), rest is automated |
| Inspectability | ✅ Excellent | Think tool parameters show Claude's reasoning |
| Flexibility | ✅ High | Users can modify draft, add personal tags, choose templates |
| Error Recovery | ⚠️ Moderate | May need manual reset if Claude gets stuck (add reset_workflow tool) |

### 10.4 Cross-Client Compatibility: ✅ High

| Client | Compatibility | Notes |
|--------|---------------|-------|
| Claude Desktop | ✅ Full | Primary target, full feature support |
| Cursor | ✅ Expected | Standard MCP protocol, should work |
| Cline (VSCode) | ✅ Expected | Standard MCP protocol, should work |
| Continue | ✅ Expected | Standard MCP protocol, should work |

### 10.5 Performance Considerations

| Aspect | Expected Performance | Optimization Strategies |
|--------|---------------------|------------------------|
| Tool Call Overhead | ~12 tool calls per card | Acceptable for a one-time card creation |
| File I/O | Minimal | Templates cached in memory after first load |
| Token Usage | Moderate | Embedded prompts add tokens but only when called |
| Latency | Low | All operations are local (no network calls) |

---

## 11. Implementation Considerations

### 11.1 Error Handling

**Scenarios to Handle**:
1. **Invalid file paths**: Config specifies non-existent directories
2. **Permission errors**: Output directory is read-only
3. **File conflicts**: Card with same name already exists
4. **Malformed templates**: Template file has invalid structure
5. **Claude skips steps**: Calls commit_* without calling think_* first

**Strategies**:
- Validate config on server startup
- Check directory permissions before operations
- Offer backup/overwrite options for conflicts
- Graceful degradation for template errors
- Warning messages (not blocking) for skipped steps

### 11.2 Testing Strategy

**Unit Tests**:
- Config parsing and validation
- Filename sanitization
- Path safety checks
- Template loading and parsing

**Integration Tests**:
- Complete Stage 1 workflow
- Complete Stage 2 workflow
- File read/write operations
- Error scenarios

**End-to-End Tests**:
- Test with actual Claude Desktop client
- Verify tool chaining behavior
- Test cross-client compatibility

### 11.3 Deployment

**Prerequisites**:
- Node.js 18+ or Python 3.10+
- MCP SDK for chosen language
- User's Claude Desktop configured

**Installation Steps**:
1. User creates project directory structure
2. User edits config.yaml with their paths
3. User adds templates to templates directory
4. User adds MCP server to Claude Desktop config
5. User restarts Claude Desktop

**Configuration Example** (for Claude Desktop):
```json
{
  "mcpServers": {
    "zettelkasten": {
      "command": "node",
      "args": ["/path/to/zettelkasten-mcp/dist/server.js"],
      "env": {
        "CONFIG_PATH": "/path/to/config.yaml"
      }
    }
  }
}
```

### 11.4 Extensibility

**Future Enhancement Opportunities**:
1. **Additional templates**: User can create custom templates by adding .md files
2. **Template mapping**: Sophisticated rules in template-mapping.yaml
3. **Backup strategies**: Configurable backup behavior
4. **Card linking**: Auto-suggest related cards based on tags
5. **Statistics**: Tool to analyze card collection (word counts, tag distribution)
6. **Search**: Tool to search existing cards
7. **Bulk operations**: Generate multiple cards in one session
8. **Advanced reflections**: Add metadata_reflection, links_reflection for richer cards
9. **Collaborative feedback**: Multi-user review process before finalization

---

## 12. Success Criteria

### 12.1 Functional Requirements

- ✅ Generate card title following user's naming conventions
- ✅ Generate content draft from conversation context
- ✅ Allow user to review and modify draft
- ✅ Support user's personal tag system (manual input)
- ✅ Auto-select appropriate template based on heuristics
- ✅ Generate detailed content heading when needed
- ✅ Apply template formatting correctly
- ✅ Save card to specified directory
- ✅ Provide clear user feedback at each stage

### 12.2 Non-Functional Requirements

- ✅ Inspectable: Show Claude's reasoning at each step
- ✅ Efficient: Complete workflow in under 60 seconds
- ✅ Reliable: Handle errors gracefully without crashing
- ✅ Maintainable: Clear code structure, well-documented
- ✅ Extensible: Easy to add new templates or tools
- ✅ Cross-platform: Works on macOS, Windows, Linux

### 12.3 User Experience Goals

- ✅ Minimal manual input: Just topic and tags
- ✅ Clear workflow progression: User always knows what's happening
- ✅ Natural conversation: No need to memorize commands
- ✅ Error tolerance: Can recover from mistakes
- ✅ Flexible: User can intervene at any point

---

## 13. Conclusion

This blueprint defines a comprehensive system for AI-assisted Zettelkasten card creation. The design emphasizes:

1. **User Agency**: Respects personal systems (tags, naming) while automating repetitive tasks
2. **Transparency**: Makes AI reasoning visible through think tools and workflow checkpoints
3. **Pragmatism**: Stateless design for broad compatibility, embedded prompts for flexibility
4. **Efficiency**: Two-stage workflow minimizes iterations and user friction

The architecture is technically feasible, leveraging standard MCP patterns and file system operations. The fixed workflow chain provides structure while remaining flexible enough for user intervention.

**Next Steps**:
1. Implement core MCP server with tool handlers
2. Create default template set
3. Test workflow with Claude Desktop
4. Gather user feedback and iterate
5. Expand template library and add optional features

This system bridges the gap between AI capabilities and personal knowledge management, enabling users to efficiently capture insights while maintaining their unique organizational systems.