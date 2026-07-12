# Skeleton Module

Locates the shared skeleton repo (`repo_setup_python`) for `/sync-setup`, the command that pulls
tooling updates from this repo into other projects that were bootstrapped from it.

## Usage

```sh
uv run --no-sync invoke skeleton.locate_source
```

## What It Does

Resolves `skeleton.local` from `properties.yml`. If that path exists on disk, it's used directly —
no `git pull` is run, since the assumption is you already pushed your changes here before running
`/sync-setup` elsewhere. If the local path isn't found (e.g. a different machine or CI), it shallow-
clones `skeleton.remote` into `tmp/skeleton_sync/` instead.

Either way, the resolved path is printed on its own line as `SKELETON_PATH=<path>` so the
`/sync-setup` prompt can parse it out of any other output.

The actual file-by-file comparison, classification (shared tooling vs. project-specific), and
conflict resolution happens in the `/sync-setup` prompt itself, not here — see
`.github/prompts/sync-setup.prompt.md`.

## Architecture

```
uv run --no-sync invoke skeleton.locate_source
  ↓
modules/skeleton/sync.py
  ↓
properties.yml (skeleton.local / skeleton.remote)  →  SKELETON_PATH=<resolved path>
```
