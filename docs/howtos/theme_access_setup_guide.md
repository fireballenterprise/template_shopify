# Theme Access Setup Guide
Checklist for generating and securing a Shopify Theme Access token.

## When You Need This
- [ ] Only needed for non-interactive sessions (CI, scripts without a TTY)
- [ ] Skip entirely for local interactive use — `shopify theme pull/push` opens a browser login by default (CLI 4.0+)

## Generate the Token
- [ ] Install [Theme Access](https://apps.shopify.com/theme-access) (official Shopify app) on the store
- [ ] Open the app → Create password → copy the token (`shptka_...`, shown once)

## Store It Locally
- [ ] Save to `tmp/.shopify/.token` (already covered by `**/tmp/**` in `.gitignore`)
- [ ] Paste via an editor, not `echo "..." > file` (avoids leaking the token into shell history)
- [ ] `chmod 600 tmp/.shopify/.token` — owner read/write only

## Load It
- [ ] `eval "$(uv run --no-sync invoke shopify.env)"` — exports `SHOPIFY_FLAG_STORE` and `SHOPIFY_CLI_THEME_TOKEN`
- [ ] Or let `uv run --no-sync invoke shopify.pull` prompt for it interactively when unset

## Verify
- [ ] `git check-ignore -v tmp/.shopify/.token` confirms it's ignored
- [ ] `git ls-files | grep tmp/.shopify` returns nothing (never tracked)

## Rotate / Revoke
- [ ] Shopify Admin → Apps → Theme Access → regenerate password to invalidate the old token immediately
