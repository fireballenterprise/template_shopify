---
description: "Use when creating, editing, or reviewing Invoke tasks in this project. Covers Collection wiring, task structure, alias conventions, and the built-in task reference."
applyTo: "tasks/**"
---
# Tasks Instructions

## Overview
Invoke is the task runner for CI/CD-style automation (fix, test, upgrade, version checks) —
deterministic CLI only, no business logic, no AI-specific behavior. All tasks are called via
`uv run --no-sync invoke <task>`. See `.github/instructions/logic.instructions.md` for how this
fits into the full modules/tasks/prompts stack — business logic always lives in `modules/`, never
here.

## File Location
- All invoke task modules live under `tasks/`
- `tasks/__init__.py` builds the root `Collection` — every new task module must be imported and wired there explicitly (no auto-glob loading)
- Group related tasks by concern: `tasks/repo.py`, `tasks/tests.py`, `tasks/ruff.py`

## Collection Conventions
- Sub-collections mirror file names: `tasks/repo.py` → `invoke repo.<task>`
- Top-level alias tasks (no namespace) live in `tasks/combos.py` — short names (`test`, `fix`)
- Set `namespace.configure({"auto_dash_names": False})` so task names keep underscores

## Task Structure Pattern
```python
from invoke import task


@task
def task_name(context):
    """Short description shown in `invoke -l`"""
    print("\n------------")
    print("Task Display Name")
    print("------------\n")
    context.run("shell-command --flag")
```

## Wiring a New Task Module
```python
# tasks/__init__.py
from invoke import Collection

from . import combos, my_new_module, repo, ruff, tests

namespace = Collection()
namespace.configure({"auto_dash_names": False})
namespace.add_collection(my_new_module, name="my_new_module")
```

## Alias Tasks
- Define combo/alias tasks in `tasks/combos.py`, calling sub-tasks directly:
  ```python
  @task
  def test(context):
      """Run All Tests"""
      tests.actionlint(context)
      tests.pylint(context)
      tests.rufflint(context)
      tests.yamllint(context)
  ```

## Calling Into `modules/`
- Tasks that wrap git workflow logic (`repo.pull`, `repo.push`, etc.) should be thin wrappers that
  import the module and call its `main()` — keep git/business logic in `modules/repo/*.py`, not in `tasks/repo.py`
- Unused `context` parameters (required by Invoke's `@task` signature) should be prefixed `_context`

## Task Reference

### Combo Tasks (use these most often)
| Task | Command | Description |
|------|---------|-------------|
| Fix | `uv run --no-sync invoke fix` | Run all auto-fixes (ruff fix + format) |
| Test | `uv run --no-sync invoke test` | Run all tests (actionlint + pylint + ruff + yamllint) |

### Test Tasks
| Task | Command | Description |
|------|---------|-------------|
| actionlint | `uv run --no-sync invoke tests.actionlint` | GitHub Actions workflow validation |
| pylint | `uv run --no-sync invoke tests.pylint` | Python code quality |
| rufflint | `uv run --no-sync invoke tests.rufflint` | Python linting and formatting |
| yamllint | `uv run --no-sync invoke tests.yamllint` | YAML file validation |

### Ruff Tasks
| Task | Command | Description |
|------|---------|-------------|
| fix | `uv run --no-sync invoke ruff.fix` | Auto-fix ruff lint issues |
| format | `uv run --no-sync invoke ruff.format` | Auto-format Python code |

### Upgrade Tasks
| Task | Command | Description |
|------|---------|-------------|
| libs | `uv run --no-sync invoke upgrade.libs` | Upgrade libraries only |
| python | `uv run --no-sync invoke upgrade.python` | Upgrade Python only |
| sync | `uv run --no-sync invoke upgrade.sync` | Sync dependencies (no version check) |
| upgrade | `uv run --no-sync invoke upgrade.upgrade` | Upgrade Python + all dependencies (default) |

### Versioning Tasks
Read-only version-lock *checks* — compare `pyproject.toml` deps and `.github/workflows/` action
refs against latest releases and update the version locks in place (does not install anything;
see Upgrade Tasks above for that). See `.github/instructions/versioning.instructions.md` for the
module behavior behind these.

| Task | Command | Description |
|------|---------|-------------|
| update | `uv run --no-sync invoke ver.update` | Run every version check (libs, python, workflows) |
| libs | `uv run --no-sync invoke ver.libs` | Check `pyproject.toml` deps against latest releases |
| python | `uv run --no-sync invoke ver.python` | Check the pinned Python version against the latest release |
| workflows | `uv run --no-sync invoke ver.workflows` | Check `.github/workflows/` action refs against latest versions |

### Invoke vs Direct Python
| Use case | Command |
|----------|---------|
| Fix code style | `uv run --no-sync invoke fix` |
| Run all tests | `uv run --no-sync invoke test` |
| Run one linter | `uv run --no-sync invoke tests.pylint` |
| Upgrade everything | `uv run --no-sync invoke upgrade.upgrade` |
| Run a module | `uv run --no-sync python -m modules.chat.start --title="..."` |
| Test a route | `uv run --no-sync python -m modules.chat.route "start my chat"` |

## Canonical Workflow
```bash
# After modifying Python or YAML files:
uv run --no-sync invoke fix    # auto-fix first
uv run --no-sync invoke test   # verify 10/10
```
All `uv run` calls MUST use `--no-sync`. See `.github/instructions/tests.instructions.md`.

## AI Command Mirrors
`.github/prompts/*.prompt.md` is the source of truth for every slash command. `.claude/commands/`
and `.clinerules/workflows/` are hand-maintained mirrors, not generated by an invoke task — see
`.github/instructions/prompts.instructions.md` for the required frontmatter/body per tool and the
"create in all three dirs" step whenever a prompt is added or changed.

| Task | Command | Description |
|------|---------|-------------|
| hermes | `uv run --no-sync python -m modules.hermes.sync` | Sync `~/.hermes/` config + SKILL.md (not an invoke task) |

## Task Ordering & File Locations
Tasks within a file are ordered alphabetically by function name — see the Alphabetical Ordering
rule in `.github/instructions/style.instructions.md` (not restated here). For the full `tasks/`
directory tree, see `.github/instructions/index.instructions.md`'s Project Structure section — the
canonical, single copy of that listing.
