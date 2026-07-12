# Version Module

Bumps the repo's root `VERSION` file (`Major.Minor.Patch[-Build]`) for development deploys, and
finalizes it for release. Does not commit or push — that's handled by the calling GitHub Actions
workflow (`deploy.yml`/`release.yml`), same as the promote (`release.yml`) and `upgrade.yml` inline `git` steps.

## Usage

```sh
uv run --no-sync invoke version.bump_build        # dev deploy: new minor's first build, or next build number
uv run --no-sync invoke version.bump_release     # release: drop the build suffix
```

## `bump.py` — `version.bump_build` / `version.bump_release`

1. Reads and parses the root `VERSION` file against `Major.Minor.Patch[-Build]`.
2. `bump_build()` — no build suffix yet (e.g. `1.0.0`) means the last release shipped and no dev
   builds have started against the next one, so it bumps the minor and starts build `001`:
   `1.0.0` -> `1.1.0-001`. A build suffix already present means builds are in progress, so it
   only increments the build number: `1.1.0-001` -> `1.1.0-002`.
3. `bump_release()` — drops the build suffix: `1.1.0-003` -> `1.1.0`.
4. Both write the new value back to `VERSION`, restamp the version comment in
   `snippets/fireball-version.liquid` (the theme's home-page version stamp), and return it.

```
uv run --no-sync invoke version.bump_build
  ↓
modules/version/bump.py
  ↓
VERSION (Major.Minor.Patch[-Build])   →   VERSION (next build, or next minor's build 001)

uv run --no-sync invoke version.bump_release
  ↓
modules/version/bump.py
  ↓
VERSION (Major.Minor.Patch-Build)     →   VERSION (Major.Minor.Patch, no build)
```

## Conventions

- Exposes `bump_build()`/`bump_release()` (public, no leading `_`) rather than a single `main()` —
  both are equally valid entry points, one per `version.*` invoke task, same pattern as
  `modules/repo/pr.py`'s `main()`/`save_notes()`/`create_pr()`
- Resolves the repo path via `modules.common.properties.get_repo_root()`, not `get_repo_local()`
  — these tasks run in CI (GitHub Actions), where `get_repo_local()`'s hardcoded
  `properties.yml` path doesn't exist; `get_repo_root()` finds the repo from the actual working
  directory instead, same as `modules/versioning/` and `modules/dawn/`
- Use `modules.common.utils` (`success`/`error`) for all console output
