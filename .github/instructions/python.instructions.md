---
description: "Use when writing, editing, or reviewing Python code in this project. Covers Python version, style, module conventions, and ruff/pylint configuration."
applyTo: "**/*.py"
---
# Python Instructions

## Python Version
Target: `>=3.14` (defined in `pyproject.toml`, pinned in `.python-version`)

## Style & Linting
- **Ruff** enforces fast style/lint checks — run `uv run --no-sync invoke tests.rufflint` to check, `uv run --no-sync invoke ruff.fix` to auto-correct
- **Pylint** enforces deeper static analysis — run `uv run --no-sync invoke tests.pylint` (must score 10.00/10 to pass `invoke test`)
- Run `uv run --no-sync invoke fix` to auto-correct everything Ruff can fix, then format
- Config lives in `pyproject.toml` under `[tool.ruff]` and `[tool.pylint]`
- Disable a rule inline only when necessary, with a comment explaining why:
  ```python
  value = compute()  # noqa: PLR0912 -- justified because ...
  ```

## Module & File Conventions
- Use module-level functions (`def foo():`), not classes, unless state genuinely requires it
- Files under `modules/common/` provide shared helpers (`cli`, `properties`, `utils`)
- Files under `modules/repo/` provide git workflow logic; each exposes a `main()` entry point
- Files under `modules/shopify/` provide Shopify theme workflow logic; each exposes a `main()` entry point
- Files under `modules/versioning/` provide dependency/action/Dawn version checks; each exposes a `main()` entry point
- Use type hints on function signatures (`def foo(x: int) -> str:`)
- Prefer `pathlib.Path` over string paths

## Logging & Output
- Use `modules.common.utils` helpers for all console output — `success()`, `error()`, `warning()`, `info()`
- Do not use `print()` directly in `modules/` code (tasks in `tasks/*.py` may `print()` for section headers)
- `error()` prints to stderr and exits the process — use for unrecoverable failures

## Shell Commands
- Use `subprocess.run([...], cwd=repo_path, check=...)` — always pass a list of args, never `shell=True`
- Never interpolate user input into shell strings

## Example Module Pattern
```python
"""One-line module docstring."""

from ..common import cli as click
from ..common.utils import success


def main() -> None:
    """Entry point for this module."""
    click.echo("Doing the thing...")
    success("Done")


if __name__ == "__main__":
    main()
```
