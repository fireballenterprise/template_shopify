---
description: Compare the current feature branch to its base branch (development/main) and draft a Pull Request description with a Summary and bulleted Changes.
subtask: false
agent: general
slash_command: /pr-notes
allowed-tools: Bash(uv run --no-sync *)
---

Gather the branch and diff context by running `uv run --no-sync invoke repo.pr_diff` using the Bash
tool. If it fails, show the full output to the user and ask how they'd like to proceed.

Using the branch, commit log, and diff above, write a Pull Request description:
- `## Summary` — 1-3 sentences describing the overall change
- `## Changes` — a bulleted list of the key changes (one bullet per logical change, not per file)

Then:
- If you were invoked directly by the user (they typed `/pr-notes`), save the notes by running:
  `uv run --no-sync invoke repo.pr_notes_save --content="<the notes>"`
  Report the saved file path to the user — they may copy/paste it into an existing PR description.
- If you are running as a step inside another command (e.g. `/pr`), do not save — just hold the
  composed notes so that command can use them directly.
