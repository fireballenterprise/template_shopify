---
description: "Use when creating or editing Copilot prompt files for this project. Covers prompt structure, frontmatter, naming, and how prompts interact with invoke tasks and modules."
applyTo: ".github/prompts/**"
---
# Prompts Instructions

## Location
All prompt files live in `.github/prompts/*.prompt.md`

## Frontmatter
```yaml
---
name: prompt-name
description: Short description of what the prompt does.
argument-hint: no arguments required
agent: agent
---
```
- `description` is required — it's how the agent discovers and invokes the prompt
- `name` should match the filename (without `.prompt.md`)

## Prompt Design Guidelines
- One focused task per prompt — do not combine unrelated workflows
- Reference invoke tasks by their full namespaced name: `uv run --no-sync invoke tests.rufflint`
- Reference modules by full path: `modules.repo.pull`, `modules.shopify.pull`
- Keep prompts concise — they share context window with instructions

## Interacting with This Project
- To run linting: `uv run --no-sync invoke test`
- To auto-fix: `uv run --no-sync invoke fix`
- To add a new invoke task: follow `tasks.instructions.md` conventions
- To add a new module: follow `modules.instructions.md` conventions

## Naming
- Use kebab-case filenames matching the invoke task or git action: `push.prompt.md`, `pull.prompt.md`
- Name should describe the action, not the subject

