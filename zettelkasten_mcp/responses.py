"""Response text templates and embedded prompts for tool outputs.

All text that gets returned to the user is managed here in one place.
"""
# ============================================================================
# Stage 1: Draft Generation Responses
# ============================================================================

TITLE_THINKER_PROMPT = """A paused reasoning for better title generation or improvement.

**User Query**: {query}.

**NEXT ACTION**: Call {next_tool}."""

TITLE_GENERATION_PROMPT = """You are generating a Zettelkasten card title.

**Important**: Generate ONLY the title part - do NOT include the timestamp. The timestamp will be automatically added when saving (format: YYYYMMDDHHMMSS - Title).

**Guidelines**:
- **Format**: CoreConcept (clear, descriptive phrase)
- **Length**: 3-8 words typically
- **Atomic**: One card, one concept - keep it focused
- **Self-explanatory**: The title alone should convey the topic clearly
- **Natural language**: Use spaces, capitalize appropriately

**Examples of Good Titles**:
- MCP Tool Driven Sequential Workflow
- Embedded Prompts for Token Efficiency
- Think Tools Force Segmented Cognition
- Two Stage Workflow Content Before Format

**Examples of Poor Titles**:
- Stuff (too vague)
- How To Build A Complete MCP Server With All Features And Tools (too long)
- mcp_workflows (poor formatting)

Based on the specific topic information you identified in title_thinker, generate a concise, descriptive title that captures the core concept.

**NEXT ACTION**: Call {next_tool}."""

CONTENT_THINKER_PROMPT = """A paused reasoning for better content writing given the title: {title}.

**NEXT ACTION**: Call {next_tool}."""

CONTENT_GENERATION_PROMPT = """**Your Task:**
Generate the body content for a single Zettelkasten note by synthesizing the dialogue about the title: **{title}**

**Core Principles & Constraints:**

1.  **Content Only (No Metadata):** Generate the body content *only*. Omit the title itself, tags, links, or any other metadata. The output should be ready to be pasted directly into a note file.

2.  **Narrative Perspective:** The note must be written from the perspective of the human participant(s).
    *   **Infer the Human's Identity:** First, analyze the source dialogue to determine how the human refers to themselves (e.g., "I," "we," "our team," a specific name). Use this identifier consistently.
    *   **Default to 'I':** If no specific self-referential term can be inferred from the dialogue, default to the first-person singular ("I").
    *   **AI's Identity:** The AI must always be referred to as an external entity (e.g., "the AI," "the model").

3.  **Narrative Synthesis (Article Format):** Synthesize the entire interaction into a cohesive, article-style text. The article must narrate the progression of the inquiry and the AI's corresponding explanations from the established perspective.
    *   **Do not use a turn-by-turn dialogue format (e.g., `Human:`, `AI:`).**
    *   Weave the interaction into a flowing narrative that reads like a self-contained thought exploration, attributing the source of ideas (e.g., "The initial question was about...", "The AI clarified that...", "This led to a refined query about...").

4.  **Strict Atomicity:** The note must be *atomic*, focusing exclusively on the single, self-contained idea related to the note's title: **{title}**. Do not include related but distinct ideas that would belong in their own separate notes.

5.  **Logical Inquiry Path:** The narrative must logically represent the human's thought process—capturing the essence and progression of questions, refinements, and follow-ups that led to the final insight.

6.  **Language Consistency:** The output must be in the same primary language as the source dialogue. Bilingual explanations for technical terms are acceptable where necessary for clarity.

7.  **Clean Markdown:** Format the entire output as a clean Markdown article. To maintain the note's atomic focus, **avoid using headings (`#`, `##`, etc.) unless absolutely essential for clarity**. Rely on paragraphs and simple formatting like bolding or lists for internal structure.

The final output should read like a self-contained, atomic note that documents the exploration of a single concept through a focused narrative of inquiry and discovery."""

DRAFT_COMPLETE_PROMPT = """**Stage 1: Draft Generation Complete**

**Next Steps**: Represent title and content to the user, and let them review manually."""

# Stage 2: Card Generation Responses

ROUTER_PROMPT = """Decides whether the content needs a heading.

Note: heading is a detailed title in the content body part, not the title itself.

If needs a heading, the next action is to call `heading_generation`, otherwise, to call `apply_template`
"""

HEADING_GENERATION_PROMPT = """You are generating a detailed content heading for a Zettelkasten card.

**Context**:
- The card already has a filename-friendly title (e.g., "20251021-MCP-Stateless-Workflow")
- You need to create a more descriptive heading that will appear at the top of the content
- This heading has no filename constraints, so it can be more detailed and readable

**Requirements**:
- **More detailed than the card title**: Expand abbreviations, add context
- **Accurately describes the core mechanism or concept**: Be specific about what the card covers
- **Length**: 40-100 characters (longer than title, but still concise)
- **Natural language**: Use full words, proper punctuation, can include colons or parentheses

**Examples**:

Card Title: `20251021-MCP-Tool-Driven-Workflow`
Good Heading: `MCP: Implementing Stateless Sequential Workflows Through Tool-Returned Process Instructions`

Card Title: `20251021-Embedded-Prompts-Token-Efficiency`
Good Heading: `Embedded Prompts: Loading Generation Instructions On-Demand to Reduce System Prompt Pollution`

Card Title: `20251021-Think-Tools-Segmented-Cognition`
Good Heading: `Think Tools: Using No-Op Tools as Cognitive Checkpoints to Force Deliberate Reasoning`

**Guidelines**:
- Expand on what the card title abbreviates
- Include the "how" or "why" if space permits
- Use natural language (not filename-constrained format)
- Make it immediately clear what the reader will learn

Based on the card title and content summary, generate a detailed, descriptive heading.

**NEXT ACTION**: Call {next_tool}."""

RESPONSE_CARD_SAVED = """Card saved: {filepath}{backup_msg}

{file_size} characters written."""

# Error Messages

ERROR_EMPTY_TITLE = "Error: Title cannot be empty. Please generate a valid title."

ERROR_TEMPLATE_NOT_FOUND = "Error: Template file not found at {template_file}"

ERROR_PATH_TRAVERSAL = "Error: Invalid file path. Path traversal detected."

ERROR_BACKUP_FAILED = "Error creating backup: {error}"

ERROR_SAVE_FAILED = "Error saving card: {error}"

ERROR_UNKNOWN_TOOL = "Unknown tool: {tool_name}"
