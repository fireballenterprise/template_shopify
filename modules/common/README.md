# Common Modules

Shared helpers used by `modules/repo/*`, `modules/shopify/*`, and `tasks/*`.

| Module | Purpose |
|--------|---------|
| `cli.py` | Click-like CLI compatibility helpers (`echo`, `prompt`, `confirm`, `command`, `option`) backed by `argparse` — avoids adding a `click` dependency |
| `properties.py` | Reads `properties.yml` (cached): `get_repo_root()`, `get_properties()`, `get_repo_local()`, `get_repo_remote()`, `get_shopify_store()`, `get_shopify_theme_id_dev()`, `get_shopify_theme_id_prd()`, `get_shopify_local_theme_token()`, `get_template_local()`, `get_template_remote()` |
| `route_utils.py` | `find_repo_root()`, `build_env()` — used by `modules/template/route.py` to locate the repo root and pass `active_topic.yml` context through to subprocess calls |
| `utils.py` | Output helpers (`success`, `error`, `warning`, `info`) and `create_slug()` |

## Conventions

- All functions are module-level (no classes except small validator helpers in `cli.py`)
- `error()` prints to stderr and calls `sys.exit()` — use for unrecoverable failures
- `get_repo_root()`/`get_properties()` are `lru_cache`d singletons — safe to call repeatedly
