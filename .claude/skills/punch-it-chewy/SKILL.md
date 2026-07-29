---
name: punch-it-chewy
description: Use for the full ship workflow — test, audit docs for drift, push the current branch, then draft PR notes and open a Pull Request. Equivalent to /punch-it-chewy.
---

# Punch It Chewy Workflow

Use this file as source of truth: `.github/prompts/punch-it-chewy.prompt.md`

When the user asks to ship/finish a branch end-to-end, read that prompt file and follow it.

It composes, in order: `test` → `docs` → `push` → `pr` (see those skills for each step's
underlying command). Stop and ask the user how to proceed if any stage fails — do not continue to
the next stage.
