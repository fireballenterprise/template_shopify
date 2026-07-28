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

**Always order functions, tasks, methods, constants, and list items alphabetically** unless
execution order requires otherwise (e.g., a pipeline that must run step 1 before step 2).
Alphabetical is the rule specifically because it's objectively checkable — "most important first"
or "most recently added" aren't quantifiable and depend on the author's head at the time.

This applies to:
- Invoke task functions within a task file
- Module-level functions and module-level constants within a Python file (see
  `python.instructions.md`'s Constants section)
- Dictionary keys, YAML keys, and list items where order is arbitrary
- Import groups are sorted by ruff — do not override

**When to apply it:** alphabetize when *adding* a new function/constant (insert it in alphabetical
position), or when a file is already being edited for another reason and its ordering needs
correcting. This is not a mandate to do a repo-wide resort pass — a file you aren't otherwise
touching stays as-is, even if its existing order predates this rule (e.g.
`modules/template/scope.py`'s constants are grouped by concern, not alphabetical, and aren't
retroactively fixed by this rule alone).

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
