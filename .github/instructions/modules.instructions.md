---
description: "Use when creating or editing shared Python modules used by invoke tasks or prompts. Covers modules/ structure, module patterns, and helper conventions."
applyTo: "modules/**/*.py"
---
# Modules Instructions

## Purpose
Modules provide reusable Python logic consumed by invoke tasks, prompts, and scripts. They contain no task definitions — only functions.

## Locations
| Path | Purpose |
|------|---------|
| `modules/common/` | Helpers tightly coupled to invoke tasks (`cli`, `properties`, `utils`); non-generic, project-specific helpers get their own file here (e.g. `shopify.py`) rather than living in `properties.py`, which mirrors the shared `template_python` repo verbatim for easy sync |
| `modules/repo/` | Git/PR workflow logic (pull, push, log, squash, rebase, pr) |
| `modules/setup/` | Repo bootstrap logic called by `setup.sh`/`setup.ps1` (`properties.py`) |
| `modules/template/` | Syncs shared, generic tooling with the parent template repo for `/template` |
| `modules/tests/` | Repo consistency checks called by `tasks/tests.py` (`check_agents.py`) |
| `modules/versioning/` | Checks `pyproject.toml` deps and workflow action refs against latest releases, updates locks; bumps the repo's `VERSION` file for deploys/releases (`project.py`) |

## Module Conventions
- One concern per file; filename matches the concern in snake_case
- Use module-level functions, not classes, unless state genuinely requires it
- `modules/repo/*.py` files each expose a `main()` entry point; a file may expose additional public
  functions (not prefixed `_`) if it backs more than one invoke task — e.g. `pr.py` exposes `main()`
  (diff context), `save_notes()`, and `create_pr()` for its three `repo.pr_*` tasks
- Private helpers are prefixed with `_` (e.g. `_stash_if_needed`)

## Method Patterns
```python
"""One-line module docstring."""

import subprocess
from pathlib import Path

from ..common import cli as click
from ..common.utils import error, success


def _helper(repo_path: Path) -> bool:
    """Docstring explaining behavior."""
    result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True)
    return bool(result.stdout.strip())


def main() -> None:
    """Entry point."""
    # implementation
```

## Common Helper Modules (`modules/common/`)
| Module | Use When |
|--------|----------|
| `cli.py` | Click-like `echo`, `prompt`, `confirm`, `is_tty`, `command`/`option` decorators |
| `properties.py` | Read `properties.yml` — `get_repo_local()`, `get_repo_remote()`, `get_template_local()`, `get_template_remote()`. Mirrors `template_python`'s copy exactly — don't add project-specific functions here |
| `shopify.py` | Shopify store/theme config, not part of `template_python` — `get_shopify_store()`, `get_shopify_theme_id()`, `is_ci()` |
| `utils.py` | `success()`, `error()`, `warning()`, `info()`, `create_slug()` |

## Guidelines
- Keep functions focused and single-purpose; extract private helpers instead of writing long functions
- Subprocess, logging/`print()`, and type-hint rules are covered once in
  `.github/instructions/python.instructions.md` (always loaded alongside this file for any
  `modules/**/*.py` edit) — not restated here
