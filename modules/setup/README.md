# Setup Module
One-time repo bootstrapping helpers, called by `setup.sh`.

## Commands
```sh
uv run --no-sync invoke setup.properties
```

## What It Does
`properties.yml` is gitignored. **A no-op if it already exists** — `modules/setup/properties.py`
only ever creates the file, it never rewrites an existing one. To regenerate it (e.g. after moving
the repo, renaming it, or pointing it at a new fork), delete or rename `properties.yml` first, then
run again.

On first run, assembles it from every tier fragment under `modules/setup/templates/properties/*.yml`
— one file per repo in the lineage, each named after itself:
- `template_python.yml` — `repo`, `template` (the root; generic to every template-stamped repo
  regardless of product line)
- `template_shopify.yml` — `shopify.local_config` (generic to every Shopify-line repo descended
  from here)

A descendant repo (e.g. a brand store) adds its own same-named fragment on top for its own config,
without ever touching this repo's fragments.

`repos` (the GitHub org/repo map + template lineage) is built additively rather than concatenated:
each fragment's own `repos:` block contributes just its own org/repo + the lineage edge to its
parent, deep-merged into whatever was inherited from earlier tiers. A repo only ever ends up
knowing its own ancestor chain, never a sibling branch it isn't descended from.

Detects this repo's actual path on disk and its git `origin` remote (if any), and stamps
`repo.local` and `repo.remote` with those values. Auto-detects `template.*` (the parent template
repo for `/template`) via GitHub's generated-from link, falling back to an interactive prompt.

## Files
- `properties.py` — creates `properties.yml` (used by `inv setup.properties`)
- `templates/properties/*.yml` — per-tier fragments merged into a fresh `properties.yml`
- `README.md` — this file
