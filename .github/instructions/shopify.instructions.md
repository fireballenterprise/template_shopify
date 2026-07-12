---
description: "Use when working with Shopify theme files, Shopify CLI, or theme-check. Covers theme structure, sync workflow, Dawn conventions, and Shopify-specific tooling."
applyTo: "{assets,config,layout,locales,sections,snippets,templates}/**"
---
# Shopify Instructions

## Theme Overview
A fork of [Shopify Dawn](https://github.com/Shopify/dawn) customized for Fireball Enterprise (fireballenterprise.com). Dawn is Shopify's reference theme built on Online Store 2.0.

## Shopify Theme Directories
Only these directories are synced to Shopify via CLI — do not put Ruby tooling here:
| Directory | Purpose |
|-----------|---------|
| `assets/` | JS, CSS, images, fonts |
| `config/` | Theme settings schema (`settings_schema.json`, `settings_data.json`) |
| `layout/` | Base layout files (`theme.liquid`) |
| `locales/` | Translation strings (`.json`) |
| `sections/` | Shopify sections (`.liquid` + optional `schema`) |
| `snippets/` | Reusable Liquid snippets |
| `templates/` | Page templates (JSON or Liquid) |

## Shopify CLI Sync Workflow
```sh
# Load store domain + theme token for this shell session (values come from tmp/.shopify/config.yml, gitignored)
eval "$(uv run --no-sync invoke shopify.env)"

# Pull live theme edits from Shopify → local repo
shopify theme pull

# Push local changes → Shopify store
shopify theme push

# After pulling, commit to keep repo in sync
git add -A && git commit -m "Sync theme edits"
```

## Staging with Unpublished Themes
- Duplicate the live theme in Shopify Admin → edit the duplicate → preview → publish
- No separate dev store needed at this scale

## Theme Linting
```sh
uv run --no-sync invoke tests.theme_check   # Run theme-check via Shopify CLI
uv run --no-sync invoke shopify.fix         # Auto-correct theme-check offenses
```

## Shopify Workflow Tasks
```sh
uv run --no-sync invoke shopify.pull --env=dev       # Pull the dev theme → local branch
uv run --no-sync invoke shopify.pull --env=prd       # Pull the production (live) theme → local branch
uv run --no-sync invoke shopify.pull theme=<name>    # Pull a specific theme by raw name or ID
uv run --no-sync invoke shopify.deploy --env=dev     # Push local theme files → dev theme
uv run --no-sync invoke shopify.deploy --env=prd     # Push local theme files → production (live) theme
uv run --no-sync invoke shopify.upgrade              # Upgrade dawn_vanilla from upstream Shopify/dawn, merge into development
uv run --no-sync invoke shopify.env                  # Print Shopify CLI env var exports (eval "$(uv run --no-sync invoke shopify.env)")
```

`shopify.pull`/`shopify.deploy`'s `env=dev`/`env=prd` resolve the theme ID and store from
`tmp/.shopify/config.yml` locally, or from `SHOPIFY_THEME_ID_DEV`/`SHOPIFY_THEME_ID_PRD`/
`SHOPIFY_FLAG_STORE` env vars when running in CI (`GITHUB_ACTIONS=true`) — same command, same
task, either context. The `deploy.yml` workflow just calls `shopify.deploy` with secrets exported
as env vars and `env` (`dev`/`prd`) passed in as a workflow input; no shell logic lives in the
workflow YAML itself.

## Liquid Conventions
- Follow [Dawn's](https://github.com/Shopify/dawn) existing patterns for new sections/snippets
- Use `{{ 'file.css' | asset_url | stylesheet_tag }}` for asset loading
- Prefer `render` over `include` for snippets
- Section schemas go in the same `.liquid` file as a `{% schema %}` block

## Fireball Customization Markers
Any hand-written customization on top of stock Dawn — inline in an existing Dawn file, or a
new file we authored — must be marked so it's obvious later which parts are ours vs. upstream
Dawn. Use a `Fireball - <what/why>` comment at the start of the customized block (or top of
file for a dedicated custom file):
- Liquid: `{% comment %}Fireball - <description>{% endcomment %}`
- CSS: `/* Fireball - <description> */`
- JS: `// Fireball - <description>`

This does **not** apply to files generated/injected by a third-party app (e.g. loyalty or
chat-widget scripts pulled in from the live theme) — those are left as-is since we don't own
their content, even though they land in these directories after a `shopify.pull`.

Every customization must also have a row in the tracking table in
`fireball.instructions.md` — add/update the row whenever a customization is added,
disabled (commented out), or removed.

## settings_schema.json / settings_data.json
- `config/settings_schema.json` — defines theme editor controls
- `config/settings_data.json` — stores current theme editor values (managed by Shopify GUI — do not manually edit)

## .shopifyignore
No `.shopifyignore` is needed — the CLI only syncs the known theme directories above. Use `.shopifyignore` only if you need to exclude specific files *within* those directories from syncing.
