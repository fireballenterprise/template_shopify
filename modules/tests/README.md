# Tests Module
Repo-local consistency checks, called by `tasks/tests.py`.

## Commands
```sh
uv run --no-sync invoke tests.check_agents
```

## What It Does
`check_agents.py` verifies that every `.github/prompts/*.prompt.md` file (the source of truth for
slash commands — see `.github/instructions/prompts.instructions.md`) has a matching mirror in each
of the other three tool-specific command dirs:

- `.claude/commands/<name>.md`
- `.claude/skills/<name>/SKILL.md`
- `.clinerules/workflows/<name>.md`

It reports any prompt missing a mirror, and any mirror file left over with no matching prompt
(e.g. after a command is renamed or removed), then exits non-zero if anything is out of sync.

## Files
- `check_agents.py` — verifies `.github/prompts/` mirrors (used by `inv tests.check_agents`)
- `README.md` — this file
