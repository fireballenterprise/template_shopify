---
name: shopify
description: Use for running a Shopify theme action — pulling the live theme from the store (dev/prd) or upgrading Dawn from upstream. Equivalent to /shopify.
---

# Shopify Theme Workflow

Use this file as source of truth: `.github/prompts/shopify.prompt.md`

When the user asks to pull the live theme from a Shopify store, or upgrade Dawn from upstream,
read that prompt file and follow it.

- `upgrade`: `uv run --no-sync invoke shopify.upgrade`
- `pull dev`: `uv run --no-sync invoke shopify.pull --env=dev`
- `pull prd`: `uv run --no-sync invoke shopify.pull --env=prd`
- A specific theme by raw name or ID instead of dev/prd: `uv run --no-sync invoke shopify.pull --theme="<theme>"`
