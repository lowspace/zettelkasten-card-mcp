# Changelog

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
