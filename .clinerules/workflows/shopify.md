If $ARGUMENTS doesn't already specify it, ask the user: what action do you want to run — `pull dev`, `pull prd`, or `upgrade`?

Then run:

- If action is `upgrade`: `uv run --no-sync invoke shopify.upgrade`
- If action is `pull dev`: `uv run --no-sync invoke shopify.pull --env=dev`
- If action is `pull prd`: `uv run --no-sync invoke shopify.pull --env=prd`

If the user wants a specific theme by raw name or ID instead of dev/prd, run
`uv run --no-sync invoke shopify.pull --theme="<theme>"` instead.
