# Versioning Module

Checks project dependencies and workflow action refs against the latest published releases, and
updates the version locks. Does not install anything or run any workflow.

## Usage

```sh
uv run --no-sync invoke ver.libs                 # check pyproject.toml deps, prompt to update
uv run --no-sync invoke ver.workflows             # check .github/workflows/ action refs, prompt to update
uv run --no-sync invoke ver.all                   # run every version check (libs, workflows)
uv run --no-sync invoke ver.libs --dry-run        # preview only, never writes
uv run --no-sync invoke ver.libs --yes            # skip the confirmation prompt
```

`--dry-run` and `--yes` work the same way on `ver.workflows` and `ver.all`.

## `lib.py` — `ver.libs`

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
modules/versioning/lib.py
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

## Conventions

- Every module exposes a module-level `main()` entry point
- Both use `@click.command()` with `--dry-run`/`--yes` options
- Shell out via `subprocess.run(..., cwd=repo_path)` — never `shell=True`
- Use `modules.common.utils` (`success`/`error`/`warning`/`info`) for all console output

Dawn upstream version listing/upgrade-staging used to live here (`dawn.py`) but is its own module
now — see [`modules/dawn/`](../dawn/README.md).
