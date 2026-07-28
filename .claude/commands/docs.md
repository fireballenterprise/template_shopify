---
description: Audit the repo for doc/AI-config drift against recent changes and fix anything stale (READMEs, .github/instructions/, AGENTS.md, CLAUDE.md, and the synced command dirs).
subtask: false
agent: general
slash_command: /docs
allowed-tools: Bash(uv run --no-sync *)
---

Gather what changed on this branch by running `uv run --no-sync invoke repo.pr_diff` using the Bash
tool.

If that fails (e.g. no base branch found), fall back to `git status` and `git diff` against HEAD to
see uncommitted changes instead.

Using that diff, audit every doc and AI-config file that could be stale because of it. At minimum
check:

1. **Root `README.md`** — Setup, Project Structure, Invoke Tasks, AI Prompts, Modules sections.
2. **Module READMEs** (`modules/*/README.md`) — for every module touched by the diff.
3. **`.github/instructions/*.md`** — the source of truth for all AI rules; look for now-stale
   references to removed/renamed modules, commands, tasks, or config keys.
4. **`AGENTS.md` / `CLAUDE.md`** — thin pointer files; only need edits if the pointer chain itself
   changed (rare).
5. **The three synced command dirs** — `.github/prompts/*.prompt.md` (source of truth),
   `.claude/commands/*.md`, `.clinerules/workflows/*.md` — these must describe the same behavior;
   if one changed, the other two need the matching edit (see
   `.github/instructions/prompts.instructions.md`).
6. **`properties.yml.example`** and any other example/config file describing setup — if `setup.sh`,
   `setup.ps1`, or `modules/setup/properties.py` changed what gets generated.
7. Any other `*.md` file that references a file, command, module, or behavior touched by the diff.

For each stale doc you find, fix it directly — this is a repo-local consistency sweep, not a
cross-repo sync, so no confirmation is needed before editing; git history is the safety net.

When done, report a short summary: which files you updated and why, or "no doc drift found" if
everything was already current.
