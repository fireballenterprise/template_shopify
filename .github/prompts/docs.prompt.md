---
name: docs
description: Audit that .github/instructions/, .claude/commands/, and READMEs are in sync with current code and conversation, including rules the user has stated but not yet saved anywhere. Read-only — reports gaps, does not edit files until approved.
argument-hint: no arguments required
agent: agent
---
Gather the scope of what has changed recently:

!`git status --short`

!`git diff --stat development...HEAD`

Check the following areas, in order, and build a single checklist of gaps. Do not edit any file
until the user has reviewed the checklist and approved specific items.

## 1. `.github/instructions/` accuracy
Compare each file under `.github/instructions/` against what it documents (see the file table in
`project.instructions.md`). Flag:
- Tasks in `tasks/*.py` or modules in `modules/` that are new, renamed, or removed since the last
  update to `tasks.instructions.md` / `modules.instructions.md`
- Conventions introduced by the current diff (branch conventions, workflow jobs, dependency
  changes) that aren't reflected in the relevant instructions file
- Any Fireball customization added, disabled, or removed in this diff whose row in
  `fireball.instructions.md`'s tracking table is missing or stale

## 2. `.claude/commands/` sync with `.github/prompts/`
`.github/prompts/*.prompt.md` is the source of truth (`prompts.instructions.md`). For every
`.prompt.md` file, confirm a matching `.claude/commands/<slug>.md` exists and that its
`description` still matches the prompt's frontmatter `description`. Flag:
- A prompt file with no matching command file — suggest `uv run --no-sync invoke claude.sync`
- A command file whose description has drifted from its prompt — suggest re-running
  `uv run --no-sync invoke claude.sync --force`, and warn this overwrites hand-crafted extras
  (`allowed-tools`, `argument-hint`, etc.), so confirm with the user before running it

## 3. READMEs
Check root `README.md` and every `modules/*/README.md` against the current invoke tasks, modules,
and setup steps. Flag sections that reference removed or renamed things, or that omit something
added in the current diff.

## 4. Rules stated but not saved
Scan the current conversation for any rule, correction, or preference the user gave (e.g. "always
do X", "never do Y", "stop doing Z") that should govern future work in this repo, but that hasn't
been written into a `.github/instructions/*.md` file, `CLAUDE.md`, or saved as a `feedback` /
`project` memory (if running under Claude Code's auto-memory system). List each one with a
suggested destination.

## Reporting
Present one checklist grouped by the four sections above. For each gap, ask which ones to fix, and
only touch the files the user approves.
