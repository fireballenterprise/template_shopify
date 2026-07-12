# Variant Option Product Options (BCPO)
Custom product options beyond Shopify's variant limit — used for the custom barcode file
upload on personalized products (uploads land as `/uploads/` line-item properties).

## App Details
| Field | Value |
|-------|-------|
| Handle | `vo-product-options` |
| Status | Active |
| Theme embed | `shopify://apps/vo-product-options/blocks/embed-block` (app embed in `config/settings_data.json`) |

## Theme Footprint
- App embed enabled in `config/settings_data.json` (no template app blocks)

## Related Fireball Customizations
- **BCPO uploaded file preview** — `sections/main-cart-items.liquid` and
  `snippets/cart-drawer.liquid` show a thumbnail (or "Uploaded file" link) for uploaded
  files in the cart, keyed off `/uploads/` in line-item property values

## Configuration
<!-- TODO: capture app settings here (option sets, which products use file upload, allowed file types, pricing add-ons) -->
