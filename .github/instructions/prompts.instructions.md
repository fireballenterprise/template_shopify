---
description: "Use when creating or editing slash-command prompt files for this project. Covers prompt structure, frontmatter, naming, the three-way sync across .github/prompts/, .claude/commands/, and .clinerules/workflows/, and how prompts interact with invoke tasks and modules."
applyTo: ".github/prompts/**,.claude/commands/**,.clinerules/workflows/**"
---
# Prompts Instructions

## Location & Source of Truth
`.github/prompts/*.prompt.md` is the **source of truth** for every slash command. It's mirrored
into `.claude/commands/*.md` (Claude Code) and `.clinerules/workflows/*.md` (Cline) — see Required
Frontmatter and Command Body below for each tool's format.

## Architecture
Commands are the AI-facing entrypoint layer described in `.github/instructions/logic.instructions.md`
(Core Principle + The Stack) — thin wrappers only, no business logic. See that file for why
prompts are the AI's decision-capture layer, and how this differs from `tasks.instructions.md`'s
plain CLI automation.

## Naming
- Use kebab-case filenames matching the invoke task or git action: `push.prompt.md`, `pull.prompt.md`
- Name should describe the action, not the subject
- `name` frontmatter (Copilot) should match the filename (without `.prompt.md`)

## Required Frontmatter

### GitHub Copilot (.github/prompts/*.prompt.md)
```yaml
---
name: command_name
description: Brief description
argument-hint: arg1 | arg2 [optional]
agent: agent
---
```
`description` is required — it's how the agent discovers and invokes the prompt.

### Claude Code (.claude/commands/*.md)
```yaml
---
description: Brief description
---
```
Claude Code uses the filename as the command name. Extra frontmatter fields are ignored.

### Cline (.clinerules/workflows/*.md)
No frontmatter — Cline workflows are plain markdown body only. The filename (minus extension) is
the command name.

## Command Body
Claude Code and Copilot use the same inline-execution syntax:
```
!`uv run --no-sync python -m modules.your_module.route "$ARGUMENTS"`
```
The `!` prefix runs bash. `$ARGUMENTS` receives everything after the command name.

Cline doesn't support inline `!`...`` execution — its workflow body instead tells the agent to run
the command explicitly:
```markdown
Run this terminal command:

\`\`\`
uv run --no-sync python -m modules.your_module.route "$ARGUMENTS"
\`\`\`
```

## Prompt Design Guidelines
- One focused task per prompt — do not combine unrelated workflows
- Reference invoke tasks by their full namespaced name: `uv run --no-sync invoke tests.rufflint`
- Reference modules by full path: `modules.repo.pull`
- Keep prompts concise — they share context window with instructions
- All `uv run` calls in a command body MUST use `--no-sync` — it prevents `uv` from silently
  upgrading a dependency mid-task:
  ```
  ✅ uv run --no-sync python -m modules.chat.route "$ARGUMENTS"
  ❌ uv run python -m modules.chat.route "$ARGUMENTS"
  ```

## Creating a New Command
1. Create the Python module: `modules/your_module/your_task.py` (ALL logic here — see
   `modules.instructions.md`)
2. Create the router: `modules/your_module/route.py` (argument dispatch)
   ```python
   # modules/your_module/route.py
   import shlex
   import subprocess
   import sys

   from modules.common.route_utils import build_env, find_repo_root


   def main() -> int:
       raw_args = sys.argv[1] if len(sys.argv) > 1 else ""
       args = shlex.split(raw_args)
       repo_root = find_repo_root()
       env = build_env(repo_root)
       cmd = [sys.executable, "-m", "modules.your_module.your_task", *args]
       return subprocess.run(cmd, cwd=repo_root, env=env, check=False).returncode


   if __name__ == "__main__":
       raise SystemExit(main())
   ```
3. Create command files in **all three tool dirs** (`.github/prompts/`, `.claude/commands/`,
   `.clinerules/workflows/`) with the thin wrapper body — see Command Body above.
4. Run `uv run --no-sync invoke fix && uv run --no-sync invoke test` (must be 10/10 for `.py` changes)

**DO NOT:**
- ❌ Put business logic in slash command markdown files
- ❌ Write bash scripts directly in slash commands
- ❌ Use `subtask: true` in Claude Code frontmatter (causes Task tool recursion)

## Cache Restart Requirement
AI tools cache command files at startup. After editing a command file you MUST restart the AI tool
before testing:
```
❌ WRONG: Edit file → Test immediately → Doesn't work → Get confused
✅ RIGHT: Edit file → Restart AI tool → Test → Works
```

## How Slash Commands Route
```
User: /chat resume wire_tunnels
  ↓
AI tool reads command file (.claude/commands/chat.md, .clinerules/workflows/chat.md,
  or .github/prompts/chat.prompt.md)
  ↓
Command file executes: uv run --no-sync python -m modules.chat.route "resume wire_tunnels"
  ↓
Router (modules/chat/route.py) dispatches: modules.chat.resume --pattern="wire_tunnels"
  ↓
Python function receives: pattern="wire_tunnels"
```

## Command → Router → Module Mapping

### Repo
```
/repo push             → modules.repo.route → modules.repo.push
/repo pull             → modules.repo.route → modules.repo.pull
/rebase                → invoke repo.rebase → modules.repo.rebase
/squash                → invoke repo.squash → modules.repo.squash
/push (alias)          → /repo push
/pull (alias)          → /repo pull
```

### Version Checks & Upgrades
```
/update [libs|python|workflows]  → invoke ver.update → modules.versioning.{libs,python,workflows}
/upgrade [python|libs|sync]      → invoke upgrade    → modules.versioning.upgrade
```
`/update` and `invoke ver.update`/`invoke update` are equivalent, as are `/upgrade` and
`invoke ver.upgrade`/`invoke upgrade` — mirrors `apt update && apt upgrade`.

### Template Sync
```
/template [pull]  → modules.template.route → modules.template.pull
/template push    → modules.template.route → modules.template.push
```

## Related Instructions
- To add a new invoke task: follow `tasks.instructions.md` conventions
- To add a new module: follow `modules.instructions.md` conventions
- Doc/AI-config drift after a prompt change: run `/docs` (see `docs.prompt.md`)
- Branch naming and PR description format used by `pr.prompt.md`/`pr-notes.prompt.md` are defined
  once, canonically, in `git.instructions.md` — don't restate that structure in a new command
