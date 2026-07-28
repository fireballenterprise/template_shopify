Auto-fix first:

Run this terminal command:

```
uv run --no-sync invoke fix
```

Then run all tests:

Run this terminal command:

```
uv run --no-sync invoke test
```

If all tests pass, report success and stop.

If any tests fail:
- For Ruff offenses that survived the auto-fix: show the remaining failures and ask the user how they would like to proceed.
- For Pylint offenses (must score 10.00/10): show the offending lines and ask the user how they would like to proceed.
- For YAML lint failures: show the offending lines and ask the user how they would like to proceed.
- For actionlint failures: show the offending workflow file and line, and ask the user how they would like to proceed.
- For any other failures: show the full error output and ask the user how they would like to approach fixing it.
