# Final Simplified Workflow

## Stage 1: Draft Generation (5 tools)

```
1. start_draft_generation(has_title, user_provided_title?)
   → User either has a title or needs help framing one

2. title_thinker(reasoning, current_title)
   → Role 1: If no title → reason about main topic, propose title
   → Role 2: If has title → check if it's good, suggest refinements
   → Output: reasoning (not final answer)

3. generate_title(title)
   → Based on title_thinker reasoning, generate final title
   → Output: the actual title to use

4. gather_information(title, gathered_info)
   → Collect relevant details from conversation for this title
   → Extract: insights, examples, arguments, details

5. generate_card_body(title)
   → Uses embedded prompt to synthesize dialogue into narrative article
   → Prompt focuses on: narrative synthesis, atomicity, human perspective
   → Output: draft body content

6. commit_draft(content)
   → Confirms draft, shows preview, waits for user review + tags
```

## Stage 2: Card Formatting (3 tools - optimized)

User reviews draft, adds tags, then:

```
start_card_generation
  → heading_reflection → generate_heading (optional)
  → apply_template (format with timestamp and save directly)
```

**Optimization**: Merged apply_template and save_card into one operation.
No preview shown - users check files locally (saves ~150 tokens per card).

## Key Clarifications

### title_thinker vs generate_title

- **title_thinker**: REASONING tool
  - Helps frame or refine
  - Not the final answer
  - Shows thinking process

- **generate_title**: GENERATION tool
  - Based on reasoning, produces actual title
  - This is what gets used

### Prompt Management

- **tool_embedded_prompts.py**: Contains generation prompts
  - Returned by tools to guide generation
  - Separate file makes them easier to modify
  - Not called "prompts.py" (avoids MCP confusion)

- **responses.py**: Contains response text templates
  - Status messages, next action instructions
  - Error messages

### User's Card Body Prompt

The `content_generation` prompt in `tool_embedded_prompts.py` uses the user's specifications:

1. Narrative synthesis (not turn-by-turn)
2. Human perspective (I/we, AI as external)
3. Strict atomicity (one concept per card)
4. Clean markdown (avoid headings unless essential)
5. Logical inquiry path

This generates the **draft body**, not the final formatted card.

## Tool Count

- **Stage 1**: 5 tools
- **Stage 2**: 3 tools (optimized from 4+)
- **Total**: 8 tools (down from 17 in original design)

## Files Structure

```
zettelkasten_mcp/
├── server.py                     # Tool definitions + dispatcher
├── handlers.py                   # Handler functions + registry
├── responses.py                  # Response text templates
├── tool_embedded_prompts.py     # Generation prompts (renamed from prompts.py)
└── config.py                     # Configuration management
```

---

**Status**: Ready for implementation
**Date**: 2025-10-22
