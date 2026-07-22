# Versioning Module

Checks project dependencies, the pinned Python version, and workflow action refs against the
latest published releases, and updates the locks/config refs — does not install anything or run
any workflow. Installing is a separate, explicit step (`/upgrade` / `invoke upgrade` / `invoke
ver.upgrade`). Also bumps the repo's root `VERSION` file for development deploys and releases
(`project.py`) — a separate, unrelated concern that happens to live in the same module for now.

## Usage

```sh
uv run --no-sync invoke ver.libs                  # check pyproject.toml deps, prompt to update
uv run --no-sync invoke ver.python                # check the pinned Python version, prompt to update
uv run --no-sync invoke ver.workflows             # check .github/workflows/ action refs, prompt to update
uv run --no-sync invoke ver.all                    # run libs + workflows only
uv run --no-sync invoke ver.update                # run every version check (libs, python, workflows)
uv run --no-sync invoke update                    # same as above — top-level alias
uv run --no-sync invoke ver.libs --dry-run        # preview only, never writes
uv run --no-sync invoke ver.libs --yes            # skip the confirmation prompt

uv run --no-sync invoke version.bump_build        # dev deploy: new minor's first build, or next build number
uv run --no-sync invoke version.bump_release      # release: drop the build suffix

uv run --no-sync invoke ver.project_bump_build    # same as version.bump_build, under the ver.* namespace
uv run --no-sync invoke ver.project_bump_release  # same as version.bump_release, under the ver.* namespace

uv run --no-sync invoke ver.upgrade    # install the upgrades reviewed via ver.update — same as top-level `upgrade`
uv run --no-sync invoke upgrade        # same as above — top-level alias, also `upgrade.python`/`upgrade.libs`/`upgrade.sync`
```

`/update` is the slash command (`.github/prompts/update.prompt.md`) backing the `ver.*` checks
above; `/upgrade` (`.github/prompts/upgrade.prompt.md`) backs the installs.

`version.bump_build`/`version.bump_release` keep their own `version.*` task names (not only
`ver.project_bump_*`) — the reusable `fireballenterprise/workflows` deploy.yml/release.yml call
them by these exact names, so renaming or removing them would break deploys. `ver.project_bump_*`
is an additional alias wrapping the same `project.py` functions, kept for consistency with
`template_python`'s `tasks/versioning.py`.

`--dry-run` and `--yes` work the same way on `ver.python`, `ver.workflows`, and `ver.update`.

## `libs.py` — `ver.libs`

1. Reads installed and outdated packages via `uv pip list [--outdated] --format json`.
2. Parses each dependency string in `pyproject.toml`'s `[project.dependencies]` (name, operator,
   pinned version).
3. For any dependency whose latest published version differs from what's pinned, prints a
   Package | Current | Latest table.
4. Prompts to confirm, then rewrites just the version number in each affected dependency string,
   preserving its operator (`~=`, `==`, `>=`, etc.) and the rest of `pyproject.toml`'s formatting
   (via `tomlkit`).

This only edits `pyproject.toml`. To actually install the new versions, run
`uv run --no-sync invoke uv.upgrade` afterward.

```
uv run --no-sync invoke ver.libs [--dry-run] [--yes]
  ↓
modules/versioning/libs.py
  ↓
uv pip list [--outdated] --format json   →   pyproject.toml (version locks only)
```

## `workflows.py` — `ver.workflows`

1. Scans every `.github/workflows/*.yml` for `uses: owner/repo[/path]@ref` lines. Local reusable
   workflow refs (`uses: ./.github/workflows/x.yml`, no `@ref`) are skipped automatically, as are
   refs not pinned to a bare major tag — commit SHAs, branch names, and full semver pins (e.g.
   `@v4.2.0`) are left alone since there's no single unambiguous "latest" to compare against.
2. For each unique `owner/repo`, finds the highest bare-major tag (`v1`, `v2`, ... `vN`) published
   via `git ls-remote --tags --refs https://github.com/<owner>/<repo>.git` (no GitHub API token
   needed).
3. For any ref whose pinned major is lower than the latest available major, prints a
   File:Line | Action | Current | Latest table.
4. Prompts to confirm, then does an exact in-place text replacement of `action@oldref` →
   `action@newref` in each affected file — no YAML re-serialization, so comments, formatting, and
   everything else in the file is untouched.

This only edits `.github/workflows/*.yml`. It does not run, trigger, or validate the workflows —
review the diff (and consider running `uv run --no-sync invoke tests.actionlint`) before
committing.

```
uv run --no-sync invoke ver.workflows [--dry-run] [--yes]
  ↓
modules/versioning/workflows.py
  ↓
git ls-remote --tags <action repo>   →   .github/workflows/*.yml (action ref pins only)
```

## `python.py` — `ver.python`

1. Runs `uv python list` and picks the latest stable (non-freethreaded, non-prerelease) 3.x minor.
2. Compares it against `requires-python` in `pyproject.toml`.
3. If newer, prints a Current | Latest table and, on confirm, rewrites the version reference in
   every file that has one: `pyproject.toml` (`requires-python`, `target-version`),
   `.python-version`, `.pylintrc`, `setup.sh`, `.github/actions/setup_uv/action.yml`. Missing
   files are skipped with a warning, not an error — this repo doesn't have `.pylintrc` or
   `.github/actions/setup_uv/action.yml`, for example.

This only edits config file references — it does NOT install a new Python or rebuild `.venv`. Run
`uv run --no-sync invoke upgrade.python` afterward to actually install it.

## `upgrade.py` — `upgrade` / `ver.upgrade` (installs)

Executes the actual installs that `ver.libs`/`ver.python` only prepared: removes and recreates
`.venv` via `setup.sh` if Python changed, then runs `uv sync --upgrade`. Imports `libs.py`'s
private `_get_installed_packages`/`_get_outdated_packages`/`_load_pyproject`/`_find_updates`
helpers (aliased on import) to decide whether libraries need upgrading at all before doing
anything. `upgrade.sync` (no check step) just runs `uv sync --upgrade` directly.

## `project.py` — `version.bump_build` / `version.bump_release` (aliased as `ver.project_bump_build` / `ver.project_bump_release`)

Bumps the root `VERSION` file (`Major.Minor.Patch[-Build]`) for development deploys, and finalizes
it for release. Does not commit or push — that's handled by the calling GitHub Actions workflow
(`deploy.yml`/`release.yml`). See `.github/instructions/version.instructions.md` for the full
scheme and workflow relationship.

## Conventions

- `libs.py`/`python.py`/`workflows.py` each expose a module-level `main()` entry point;
  `project.py` exposes `bump_build()`/`bump_release()` instead — both equally valid entry points.
  `version.bump_build`/`version.bump_release` stay as their own top-level collection (not only
  `ver.*`), so the external `fireballenterprise/workflows` reusable workflow's
  `invoke version.bump_build` / `version.bump_release` calls keep working unchanged
- `libs.py`/`python.py`/`workflows.py` use `@click.command()` with `--dry-run`/`--yes` options
- Shell out via `subprocess.run(..., cwd=repo_path)` — never `shell=True`
- Use `modules.common.utils` (`success`/`error`/`warning`/`info`) for all console output

Dawn upstream version listing/upgrade-staging used to live here (`dawn.py`) but is its own module
now — see [`modules/dawn/`](../dawn/README.md).
