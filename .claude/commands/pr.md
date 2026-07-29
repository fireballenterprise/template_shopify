---
description: Draft PR notes for the current feature branch and open a Pull Request via gh (does not push).
subtask: false
agent: general
slash_command: /pr
allowed-tools: Bash(uv run --no-sync *)
---

Gather the branch and diff context by running `uv run --no-sync invoke repo.pr_diff` using the Bash
tool. If it fails, show the full output to the user and ask how they'd like to proceed.

Using the branch, commit log, and diff above, write a Pull Request description (same as `/pr-notes`,
but do NOT save it to a file this time — just hold it in context). Use the canonical PR format
from `.github/instructions/git.instructions.md` (`## Summary` + `## Changes`).

Then create the pull request:
1. Note the `Base branch:` value printed above.
2. Draft a concise PR title (under 70 characters) summarizing the change.
3. Run:
   `uv run --no-sync invoke repo.pr_create --title="<title>" --content="<notes>"`
   (this also assigns the PR to the calling user via `--assignee @me`)
4. Report the PR URL to the user.

If a PR already exists for this branch, `repo.pr_create` reports its URL instead of erroring —
just relay that to the user.
