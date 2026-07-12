# Translate & Adapt
Shopify's first-party translation/localization app — manages translated content for
additional languages and market-specific adaptations.

## App Details
| Field | Value |
|-------|-------|
| Handle | — (admin-only, no theme footprint) |
| Status | Active |

## Theme Footprint
- None (theme `locales/*.json` files are Dawn's own translations, independent of this app)

## Related Fireball Customizations
- The chat country filter in `layout/theme.liquid` reads `localization.country.iso_code`,
  which reflects the markets/localization setup this app plugs into

## Configuration
<!-- TODO: capture which languages/markets are enabled and any manually adapted content -->
