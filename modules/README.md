# Modules

Reusable Python modules imported by `tasks/*.py` invoke tasks. All functions are module-level —
no classes required except small helper validators in `common/cli.py`.

## Structure

```
modules/
  claude/       # sync .claude/commands/ from .github/prompts/
  common/       # cli, properties, utils helpers
  dawn/         # upstream Shopify/dawn tag listing and upgrade-staging
  repo/         # pull, push, log, squash, rebase (git workflow)
  shopify/      # pull, upgrade, env (Shopify theme workflow)
  template/     # sync shared, generic tooling with the parent template repo for /template
  versioning/   # dependency locks, workflow action refs, and VERSION-file bumps (project.py)
```

## Submodules

| Directory | Purpose |
|-----------|---------|
| [`claude/`](claude/README.md) | Sync `.claude/commands/` from `.github/prompts/` source of truth |
| [`common/`](common/README.md) | CLI helpers, `properties.yml` config reader, output/utility helpers |
| [`dawn/`](dawn/README.md) | List upstream Shopify/dawn tags, stage a Dawn upgrade for manual review |
| [`repo/`](repo/README.md) | Git workflow, session logging, squash, and rebase |
| [`shopify/`](shopify/README.md) | Shopify CLI theme pull, Dawn upstream upgrade, and CLI env var workflow |
| [`template/`](template/README.md) | Sync shared, generic tooling with the parent template repo for `/template` (pull + push) |
| [`versioning/`](versioning/README.md) | Dependency lock and workflow action-ref checks; bump the root `VERSION` file for dev deploys and releases |

## Conventions

- One module per file; filename matches the concern in snake_case
- Each `modules/repo/*.py` and `modules/shopify/*.py` file exposes a `main()` entry point
- Shell out via `subprocess.run(..., cwd=repo_path)` — never `shell=True`
- Use `modules.common.utils` (`success`/`error`/`warning`/`info`) for all console output
- Resolve repo config via `modules.common.properties`
