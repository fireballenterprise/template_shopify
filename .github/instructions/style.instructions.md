---
applyTo: "**"
---
# Markdown Style Standards

Rules for all markdown files created across this repository.

---

## Headers

**Do not add a blank line after any header (`#`, `##`, `###`, etc.).** Content begins on the very next line.

```markdown
# ✅ CORRECT
## Section
- bullet one
- bullet two

## Another Section
Content starts here immediately.

| col1 | col2 |
|------|------|
| a    | b    |
```

```markdown
# ❌ WRONG
## Section

- bullet one

## Another Section

Content with extra blank line above.
```

Blank lines **before** a header (to separate sections) are fine and expected.

## Alphabetical Ordering

**Always order functions, tasks, methods, and list items alphabetically** unless execution order requires otherwise (e.g., a pipeline that must run step 1 before step 2).

This applies to:
- Invoke task functions within a task file
- Module-level functions within a Python file
- Dictionary keys, YAML keys, and list items where order is arbitrary
- GitHub Actions `jobs:` keys within a workflow file (e.g. `pylint` before `ruff_lint` before
  `theme_lint`) — split an oversized job rather than leaving it out of alphabetical order
- Import groups are sorted by ruff — do not override

```python
# ✅ CORRECT — alphabetical
@task
def clean(...): ...

@task
def install(...): ...

@task
def restart(...): ...
```

```python
# ❌ WRONG — order of addition
@task
def install(...): ...

@task
def update(...): ...

@task
def clean(...): ...
```
