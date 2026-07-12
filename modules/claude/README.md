# Claude Module

Keeps `.claude/commands/` in sync with `.github/prompts/*.prompt.md`, the source of truth for all
slash commands in this repo (see [prompts.instructions.md](../../.github/instructions/prompts.instructions.md)).

## Usage

```sh
uv run --no-sync invoke claude.sync          # additive only — writes commands that don't exist yet
uv run --no-sync invoke claude.sync --force  # overwrite all, including hand-crafted commands
```

Running `uv run python -m modules.claude.sync` directly is always additive-only — `--force` is only
wired up through the `claude.sync` invoke task.

## What It Does

For each `.github/prompts/*.prompt.md` file, writes a matching `.claude/commands/<slug>.md` with
a minimal `description` header. Existing files are left untouched unless `--force` is passed, since
hand-crafted commands often carry extra frontmatter (`allowed-tools`, `argument-hint`, etc.) that a
plain sync would otherwise clobber.

The command bodies are also expected to diverge intentionally: `.github/prompts/*.prompt.md` uses
`` !`command` `` to inject shell output for Copilot, but in Claude Code that syntax runs as a
harness-level preprocessing step — a non-zero exit hard-aborts the whole command before the model
ever sees the output. `.claude/commands/*.md` bodies instead tell Claude to run the command via the
Bash tool as plain prose, so a failure surfaces as normal tool output the model can explain or react
to instead of a silent abort. Keep this divergence when hand-editing or re-syncing commands.

## Architecture

```
uv run --no-sync invoke claude.sync [--force]
  ↓
modules/claude/sync.py
  ↓
.github/prompts/*.prompt.md  →  .claude/commands/*.md
```
