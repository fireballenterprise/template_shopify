---
description: "Use when writing or updating project documentation including README, setup guides, or inline code comments."
applyTo: "*.md"
---
# Docs Instructions

## Files
| File | Purpose |
|------|---------|
| `README.md` | Project overview, setup, and usage |
| `setup.sh` | Shell setup script (self-documenting via comments) |
| `.github/instructions/` | Copilot instruction files for each concern |

## README Conventions
- Lead with a short one-sentence project description
- Include: Prerequisites, Setup, Invoke Tasks, AI Prompts, and Modules sections
- Show invoke commands in fenced `sh` code blocks (`uv run --no-sync invoke ...`)
- Keep it concise — link out rather than duplicating content

## Inline Code Comments
- Comment the *why*, not the *what*
- Reference external docs or issue numbers when a workaround is non-obvious
- Use `# noqa: RULE` or `# pylint: disable=rule-name` with an explanation comment on the same or preceding line

## Instruction Files (`.github/instructions/`)
- One file per concern (python, style, tasks, modules, tests, shopify, docs, prompts, project)
- Always include a `description` in YAML frontmatter using the "Use when..." pattern
- Use `applyTo` glob only when the instruction is relevant to a specific file type or directory
- Keep instructions actionable and example-driven — prefer short code blocks over prose
