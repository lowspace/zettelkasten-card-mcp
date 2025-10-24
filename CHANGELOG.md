# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-10-24

### Major Changes

#### Token Optimization
- **Merged `apply_template` and `save_card`**: Single operation formats and saves directly
- **Removed preview in Stage 2**: Users check files locally instead (saves ~150 tokens)
- **Simplified success messages**: Concise output with essential info only
- **Total savings**: ~180-230 tokens per card (15-20% reduction in Stage 2)

#### Template System
- **Single-brace placeholders**: Changed from `{{placeholder}}` to `{placeholder}` format
- **Updated default template**: Matches user template format with uid, aliases, created fields
- **Smart template loading**: User-specified template in config.yaml takes precedence, falls back to default template.md
- **Template validation**: Ensures user templates exist before loading

#### Bug Fixes
- **Fixed `content_thinker` parameter mismatch**: Added missing `title` parameter to tool definition
- **Fixed template placeholder replacement**: All placeholders now use single braces consistently
- **Fixed syntax errors**: Corrected mismatched parentheses in `handle_generate_content`
- **Fixed package detection**: Added explicit `packages = ["zettelkasten_mcp"]` to pyproject.toml

#### Documentation
- **README restructure**: Purpose-first approach with "Why This Exists" leading
- **Demo-driven workflow**: "See It In Action" shows two-stage flow naturally
- **Copilot scope clarification**: Emphasized user-initiated approach throughout
- **Generic AI references**: Changed from "Claude" to generic "AI" for broader applicability

### Workflow Changes

**Stage 1: Draft Generation** (5 tools)
```
start_draft_generation → title_thinker → generate_title
→ content_thinker → generate_content
```

**Stage 2: Card Formatting** (3 tools - optimized)
```
start_card_generation → [optional: generate_heading]
→ apply_template (formats + saves directly)
```

### Tool Count
- **v0.2.0**: 17 tools
- **v0.3.0**: 8 tools (5 in Stage 1, 3 in Stage 2)
- **Removed**: `save_card` (merged into `apply_template`)

### Template Placeholders

Now using single-brace format:
- `{timestamp}` - Compact timestamp (YYYYMMDDHHMMSS)
- `{created_at}` - ISO format timestamp with timezone
- `{heading}` - Optional detailed heading
- `{content}` - Main content body

### Breaking Changes

- **Template format**: If you have custom templates, update placeholders from `{{name}}` to `{name}`
- **No preview**: Stage 2 no longer shows preview before saving
- **Merged tool**: `save_card` tool removed, functionality now in `apply_template`

---

## [0.2.0] - 2025-10-22

### Changed

#### Workflow Improvements
- **Added `context_gatherer` tool**: New first step in Stage 1 workflow to deeply analyze topic and extract insights from conversation before title/content generation
- **Refined think tool descriptions**: Enhanced to explicitly incentivize extended thinking and reasoning capacity
- **Updated `title_thinker` scope**: Now focuses on topic-specific information rather than full conversation summary

#### Template System
- **Simplified to single template**: Removed template directory and selection logic
- **Single `template.md` file**: One unified template for all cards
- **Removed `template_selector` tool**: No longer needed with single template

#### Naming Convention
- **New timestamp format**: `YYYYMMDDHHMMSS - Card Title` (e.g., `20251022143015 - MCP Tool Driven Workflow.md`)
- **Hyphen separator**: Space-hyphen-space (` - `) connects timestamp and title
- **Natural language titles**: Titles now use regular spaces, no hyphens within the title itself
- **Automatic timestamp**: Timestamp added by server during `apply_template`, not by user

### New Workflow

**Stage 1: Draft Generation**
```
start_draft_generation
  ↓
context_gatherer (NEW - analyze topic, extract insights)
  ↓
title_thinker (REFINED - focus on topic specifics)
  ↓
generate_title
  ↓
commit_title
  ↓
content_thinker (REFINED - deep reasoning on structure)
  ↓
generate_content
  ↓
commit_draft
```

**Stage 2: Card Generation**
```
start_card_generation
  ↓
title_reflection
  ↓
content_reflection
  ↓
heading_reflection
  ↓
apply_template (adds timestamp, uses single template)
  ↓
save_card
```

### Tool Count
- **v0.1.0**: 18 tools
- **v0.2.0**: 17 tools (added context_gatherer, removed template_selector and get_available_templates)

---

## [0.1.0] - 2025-10-22

### Added
- Initial implementation of Zettelkasten MCP server
- Two-stage workflow (draft generation + card generation)
- Think tools for segmented cognition
- Embedded prompts for token efficiency
- Template system with 4 templates (general, meeting, literature, project)
- File system operations with safety measures
- Configuration management via YAML
- Comprehensive documentation
