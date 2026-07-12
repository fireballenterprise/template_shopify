# Theme Access
Shopify's first-party app for issuing scoped theme-access tokens — this is what powers this
repo's CLI sync workflow (`shopify theme pull/push` without full admin credentials).

## App Details
| Field | Value |
|-------|-------|
| Handle | — (admin-only, no theme footprint) |
| Status | Active |

## Theme Footprint
- None

## Related Fireball Customizations
- None (tooling, not storefront) — but the whole repo sync workflow depends on it

## Configuration
- Issues the theme token stored locally at `tmp/.shopify/.theme_token` (gitignored),
  referenced by `tmp/.shopify/config.yml` and loaded via `invoke shopify.env`
- CI uses the same token via GitHub Actions secrets (`deploy.yml`)
- Tokens are per-user and emailed on creation; rotate by deleting and re-issuing in the app
