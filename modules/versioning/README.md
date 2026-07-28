# Versioning Module

Checks project version configs against the latest published releases and updates the locks —
it does not install anything or run any workflow. Installing is a separate, explicit step
(`/upgrade` / `invoke upgrade` / `invoke ver.upgrade`). Also bumps the repo's root `VERSION` file
for development deploys and releases (`project.py`) — a separate, unrelated concern that happens
to live in the same module for now.

## Usage

```sh
uv run --no-sync invoke ver.libs                  # check pyproject.toml deps, prompt to update
uv run --no-sync invoke ver.python                # check the pinned Python version, prompt to update
uv run --no-sync invoke ver.workflows             # check .github/workflows/ action refs, prompt to update
uv run --no-sync invoke ver.update                # run every version check (libs, python, workflows)
uv run --no-sync invoke update                    # same as above — top-level alias
uv run --no-sync invoke ver.libs --dry-run        # preview only, never writes
uv run --no-sync invoke ver.libs --yes            # skip the confirmation prompt

uv run --no-sync invoke ver.project_bump_build        # dev deploy: new minor's first build, or next build number
uv run --no-sync invoke ver.project_bump_release      # release: drop the build suffix
```

`/update` is the slash command (`.github/prompts/update.prompt.md`) backing the `ver.*` checks
above.

## Files

- `libs.py` — checks `[project.dependencies]` and `[project.optional-dependencies]` against
  latest releases via `uv pip list --outdated`, rewrites version locks in `pyproject.toml`
  preserving constraint operators (exits `3` when everything is already up to date)
- `python.py` — checks the pinned Python version against the latest release and updates config
  file references
- `workflows.py` — scans `.github/workflows/*.yml` for `uses: owner/repo@vN` refs, compares against
  the highest published major tag (`git ls-remote`, no API token), and rewrites the pins in place;
  SHAs, branch refs, and full semver pins are left alone
- `upgrade.py` — install/sync helpers used by `/upgrade`
- `project.py` — bumps the root `VERSION` file (`Major.Minor.Patch[-Build]`) for development
  builds, and finalizes it for release. Does not commit, push, or trigger any workflow — this repo
  has no `deploy.yml`/`release.yml` of its own. See
  `.github/instructions/versioning.instructions.md` for the full scheme.

`libs.py`, `python.py`, `workflows.py`, and `project.py` only edit config files — review the diff
before committing.
