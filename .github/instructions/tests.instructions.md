---
description: "Use when adding, editing, or running tests and linters in this project. Covers Ruff, Pylint, yamllint, actionlint, and Shopify theme-check invoke task conventions."
applyTo: "tasks/tests.py"
---
# Tests Instructions

## Test Tooling
| Tool | Covers | Run With |
|------|--------|----------|
| Ruff | Python style & lint | `uv run --no-sync invoke tests.rufflint` |
| Pylint | Python deep static analysis | `uv run --no-sync invoke tests.pylint` |
| theme-check | Shopify theme lint | `uv run --no-sync invoke tests.theme_check` |
| yamllint | YAML files | `uv run --no-sync invoke tests.yamllint` |
| actionlint | GitHub Actions workflows | `uv run --no-sync invoke tests.actionlint` |

## Running Tests
```sh
uv run --no-sync invoke test               # All: ruff + pylint + theme-check + yamllint + actionlint
uv run --no-sync invoke fix                # Auto-correct: ruff --fix + ruff format + theme-check --auto-correct
```

## File Structure
```
tasks/
  tests.py      # tests.rufflint, tests.pylint, tests.theme_check, tests.yamllint, tests.actionlint
  ruff.py       # ruff.fix, ruff.format
  shopify.py    # shopify.fix (theme-check --auto-correct), shopify.pull, shopify.upgrade, shopify.env
  combos.py     # top-level test/fix aliases
```

## Adding a New Test Task
1. Add a function to `tasks/tests.py` (or a new dedicated module for a distinct tool)
2. Wire the new module into `tasks/__init__.py` if it's a new file
3. Add the task call to the `test` (or `fix`) function in `tasks/combos.py`

## Ruff & Pylint
- Config lives in `pyproject.toml` under `[tool.ruff]` and `[tool.pylint]`
- Pylint must score 10.00/10 to pass `invoke test`
- Autocorrect: `uv run --no-sync invoke ruff.fix` then `uv run --no-sync invoke ruff.format`

## theme-check
- Lints Shopify theme files (`assets/`, `sections/`, `snippets/`, `templates/`, etc.)
- Runs via the Shopify CLI (no Ruby/gem dependency): `shopify theme check`
- Auto-correct: `shopify theme check --auto-correct`
- Config: `.theme-check.yml` at project root (if present)

## yamllint
- Config lives in `.yamllint` at project root
- Runs: `yamllint -c .yamllint .`

## actionlint
- Lints GitHub Actions workflow files under `.github/workflows/`
- Installed via the `actionlint-py` pip dependency (no Homebrew required)
- Runs: `actionlint`

