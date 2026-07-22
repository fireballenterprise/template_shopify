---
description: "Use when creating, editing, or reviewing Invoke tasks in this project. Covers Collection wiring, task structure, and alias conventions."
applyTo: "tasks/**"
---
# Tasks Instructions

## File Location
- All invoke task modules live under `tasks/`
- `tasks/__init__.py` builds the root `Collection` — every new task module must be imported and wired there explicitly (no auto-glob loading)
- Group related tasks by concern: `tasks/claude.py`, `tasks/dawn.py`, `tasks/repo.py`, `tasks/ruff.py`, `tasks/shopify.py`, `tasks/template.py`, `tasks/tests.py`, `tasks/uv.py`, `tasks/version.py`, `tasks/versioning.py`

## Collection Conventions
- Sub-collections usually mirror file names (`tasks/repo.py` → `invoke repo.<task>`), but the
  exposed name can be overridden via `add_collection(module, name="...")` — e.g.
  `tasks/versioning.py` is exposed as `ver` (`namespace.add_collection(versioning, name="ver")`)
  for a shorter CLI namespace
- Top-level alias tasks (no namespace) live in `tasks/combos.py` — short names (`test`, `fix`)
- Set `namespace.configure({"auto_dash_names": False})` so task names keep underscores
- When the desired CLI task name is a Python reserved word/builtin (e.g. `list`), use
  `@task(name="list")` on a differently-named function rather than shadowing the builtin — see
  `tasks/dawn.py`'s `list_()` function, exposed as `dawn.list`

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

from . import combos, my_new_module, repo, ruff, shopify, tests

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
      tests.theme_check(context)
      tests.yamllint(context)
  ```

## Calling Into `modules/`
- Tasks that wrap git or Shopify workflow logic (`repo.pull`, `shopify.pull`, etc.) should be thin wrappers that
  import the module and call its `main()` — keep git/business logic in `modules/repo/*.py` or `modules/shopify/*.py`, not in `tasks/*.py`
- Unused `context` parameters (required by Invoke's `@task` signature) should be prefixed `_context`

