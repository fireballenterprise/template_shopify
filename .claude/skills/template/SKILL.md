---
name: template
description: Use for syncing shared generic tooling between this repo and its parent template repo — pulling template updates in, or pushing new generic improvements out as a PR. Equivalent to /template.
---

# Template Sync Workflow

Use this file as source of truth: `.github/prompts/template.prompt.md`

When the user asks to sync tooling from the template repo, or to propose new generic
improvements upstream to the parent template repo, read that prompt file and follow it.

- Pull template updates in (default): `pull` (or no argument)
- Push new generic tooling out as a PR: `push`

Run the router from the repo root:

```bash
uv run --no-sync python -m modules.template.route "<arguments>"
```

This is distinct from `/push` and `/pull` (see the `repo` skill), which push/pull this
repo itself to/from its own GitHub origin — `/template` instead exchanges shared generic tooling
with the parent template repo configured in `properties.yml`.
