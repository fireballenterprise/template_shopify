---
description: "Use when reviewing a pull request or code change in this repo — including automated PR review. Covers what to prioritize and what to skip."
---
# Review Instructions

## Priorities (in order)
1. **Logic correctness** — trace the actual code paths changed, don't just skim the PR
   description. Flag off-by-one errors, unhandled edge cases, incorrect conditionals, silent
   failures, and mismatched types. If a function's behavior changed, confirm every caller still
   gets what it expects.
2. **DRY / duplication** — flag near-duplicate logic that belongs in a shared helper (see
   `modules/common/` in `.github/instructions/modules.instructions.md`), and duplicated
   constants/strings that should be defined once.
3. **Docs kept in sync** — see `.github/instructions/docs.instructions.md`. If the diff touches a
   module, command, task, or config key, the matching `README.md` and `.github/instructions/*.md`
   file must reflect it. This repo runs a `/docs` drift sweep before every `/punch-it-chewy` (see
   `.github/prompts/docs.prompt.md`) — a PR that skipped it should still read as internally
   consistent.
4. **Style compliance** — see `.github/instructions/style.instructions.md` (Markdown) and
   `.github/instructions/python.instructions.md` (Python). Flag violations even where
   `invoke test` would still pass — some of these are conventions, not lint-enforced rules.
5. **Tests/linters** — see `.github/instructions/tests.instructions.md`. Any `.py`, `.yml`, or
   `.yaml` change must be clean under `uv run --no-sync invoke test` (pylint 10.00/10 required).

## Repo-Specific Consistency Checks
- `.github/instructions/` is this repo's source of truth for all AI/agent rules — a PR that
  changes behavior without updating the relevant instruction file is incomplete, not just
  under-documented.
- The four synced command dirs (`.github/prompts/`, `.claude/commands/`, `.claude/skills/`,
  `.clinerules/workflows/`) must stay behaviorally consistent — see
  `.github/instructions/prompts.instructions.md`. Flag a PR that edits some but not all of the four.
- Branch name and PR title/body should follow `.github/instructions/git.instructions.md` — flag a
  branch name that isn't lowercase `snake_case` ending in `_<github_username>`, or a PR body
  missing the `## Summary`/`## Changes` structure.

## What NOT to Flag
- Formatting nitpicks `ruff format` already enforces — don't re-litigate what the tool owns.
- Missing tests/docs inside `addons/` — that content is excluded from this repo's own lint/test
  surface by design (see "Addons" in the root `README.md`).
