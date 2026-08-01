---
name: repos
description: Use for showing this repo's related-repos map (org/repo list + template lineage) from properties.yml, or applying a change to all related repos. Also a TRIGGER — read .github/instructions/repos.instructions.md whenever the user says "related repos"/"the repos"/"other repos"/"all of the repos" about this repo's family, even without running /repos. Equivalent to /repos.
---

# Repos Workflow

Use this file as source of truth: `.github/prompts/repos.prompt.md`

When the user asks about this repo's related repos, wants a change applied across them, or runs
`/repos`, read `.github/instructions/repos.instructions.md` in full and follow it — it covers both
the `repos`/`lineage` map and the two-phase (apply, then checkpoint, then ship) Cross-Repo Change
Workflow.
