---
name: repos
description: Use for showing this repo's related-repos map (org/repo list + template lineage) from properties.yml, or applying a change to all related repos. Equivalent to /repos. Also triggered by the phrases "related repos", "the repos", "other repos", or "all of the repos".
---

# Repos Trigger

Use this file as source of truth: `.github/prompts/repos.prompt.md`

When the user says "related repos", "the repos", "other repos", "all of the repos", or otherwise
asks about this repo's family — even without running `/repos` — read
`.github/instructions/repos.instructions.md` in full and follow it. It covers both the
`repos`/`lineage` map and the two-phase (apply, then checkpoint, then ship) Cross-Repo Change
Workflow.
