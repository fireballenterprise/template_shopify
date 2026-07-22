---
applyTo: ".opencode/command/**,.claude/commands/**,.clinerules/workflows/**,.github/prompts/**"
---
# AI Prompts Instructions

Standards for the AI custom prompts / slash commands, potentially synced across all four tool
directories (`.github/prompts/`, `.claude/commands/`, `.opencode/command/`, `.clinerules/workflows/`)
— this repo currently only populates `.github/prompts/` (source of truth, see
`prompts.instructions.md`) and `.claude/commands/` (mirrored via `uv run --no-sync invoke
claude.sync`). The `.opencode/command/`/`.clinerules/workflows/` formats below are documented for
forward-compatibility (`modules/template/scope.py` already treats them as eligible push/pull
directories) even though nothing lives there yet.

## Required Frontmatter

### OpenCode (.opencode/command/*.md)
```yaml
---
description: Brief description
agent: general
subtask: false  # CRITICAL — prevents Task tool recursion
slash_command: /command_name
---
```

### Claude Code (.claude/commands/*.md)
```yaml
---
description: Brief description
---
```
Claude Code uses the filename as the command name. Extra frontmatter fields are ignored.

### GitHub Copilot (.github/prompts/*.prompt.md)
```yaml
---
name: command_name
description: Brief description
argument-hint: arg1 | arg2 [optional]
agent: agent
---
```

### Cline (.clinerules/workflows/*.md)
No frontmatter — Cline workflows are plain markdown body only. The filename (minus extension) is
the command name.

## Command Body

OpenCode, Claude Code, and Copilot use the same inline-execution syntax:

```
!`uv run --no-sync invoke <collection>.<task>`
```

The `!` prefix runs bash. Most commands here call a single `invoke` task directly (e.g. `/push` →
`invoke repo.push`) — see `prompts.instructions.md` for that convention. A command that needs
subcommand dispatch (e.g. `/template pull` vs. `/template push diff`) instead runs a Python router
module, receiving everything after the command name via `$ARGUMENTS`:

```
!`uv run --no-sync python -m modules.template.route "$ARGUMENTS"`
```

Cline doesn't support inline `!`...`` execution — its workflow body instead tells the agent to run
the command explicitly:

```markdown
Run this terminal command:

\`\`\`
uv run --no-sync invoke <collection>.<task>
\`\`\`
```

## Cache Restart Requirement

AI tools cache command files at startup. After editing a command file, restart the AI tool before testing.

## uv --no-sync Flag

All `uv run` calls in commands MUST use `--no-sync`:
```
✅ uv run --no-sync invoke repo.push
❌ uv run invoke repo.push
```

## Creating a New Command

Most commands need no router — the prompt body calls `invoke <collection>.<task>` directly (see
`dawn.prompt.md`/`shopify.prompt.md` for prompts that branch on `$ARGUMENTS` in markdown and call
different invoke tasks per branch). Reach for a Python router only when a command needs
multi-phase logic with confirmation gates between steps that a single invoke call can't express —
`/template` (`modules/template/route.py` → `pull.py`/`push.py`) is the one example in this repo:

1. Create Python module(s) under `modules/your_module/` (ALL logic here, no business logic in the
   prompt markdown)
2. Create `modules/your_module/route.py` (argument dispatch, mirroring `modules/template/route.py`)
3. Create command files in the tool dirs actually in use here (`.github/prompts/`,
   `.claude/commands/`) with the router execution body from "Command Body" above
4. Run `uv run --no-sync invoke fix && uv run --no-sync invoke test` (must be 10/10 for `.py` changes)

**DO NOT:**
- ❌ Put business logic in slash command markdown files
- ❌ Write bash scripts directly in slash commands
- ❌ Use `subtask: true` in OpenCode frontmatter (causes Task tool recursion)

## Command → Task/Module Mapping

### Repo (git workflow)
```
/push              → invoke repo.push
/pull               → invoke repo.pull
/pr                 → invoke repo.pr_create
/pr-notes           → invoke repo.pr_notes_save
/punch-it-chewy     → repo.push, then repo.pr_notes_save + repo.pr_create
/rebase             → invoke repo.rebase
/squash             → invoke repo.squash
```

### Shopify / Dawn theme
```
/shopify [pull dev|pull prd|upgrade]  → invoke shopify.pull | shopify.upgrade
/dawn [list|upgrade]                  → invoke dawn.list | dawn.upgrade
```
`shopify.deploy` and `shopify.env` are used directly (`uv run --no-sync invoke shopify.deploy`,
`eval "$(uv run --no-sync invoke shopify.env)"`) — no dedicated slash command wraps them.

### Tests & Fixes
```
/test  → invoke test  (tests.rufflint, tests.pylint, tests.yamllint, tests.actionlint, tests.theme_check)
/fix   → invoke fix   (ruff.fix, ruff.format, shopify.fix)
```

### Version Checks, Upgrades & VERSION Bumps
```
/versioning [libs|workflows|all]  → invoke ver.libs | ver.workflows | ver.all
/update [libs|python|workflows]   → invoke ver.update  → modules.versioning.{libs,python,workflows}
/upgrade [python|libs|sync]       → invoke upgrade      → modules.versioning.upgrade
```
`/update` reviews and rewrites config file references only (dependency locks, pinned Python
version, workflow action refs) — it installs nothing. `/upgrade` performs the actual installs
(new Python version, `.venv` rebuild, `uv sync --upgrade`) after `/update`'s changes are reviewed.

`version.bump_build`/`version.bump_release` are invoked directly by the reusable
`fireballenterprise/workflows` deploy/release workflows (not via a slash command) — see
`version.instructions.md`.

### Template Sync
```
/template [pull]  → modules.template.route → modules.template.pull
/template push     → modules.template.route → modules.template.push
```

### Setup & Docs
```
/setup  → ./setup.sh  (creates the uv venv, installs deps, configures the Shopify CLI env)
/docs   → (AI-guided, read-only) audits .github/instructions/, .claude/commands/, READMEs for drift
```
