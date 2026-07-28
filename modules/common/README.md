# Common Utilities Module

Shared utilities and helper functions used across all modules in the template_python repository.

## Overview

This module provides common functionality that is used by other modules throughout the repository, including configuration parsing and utility functions.

## Modules

### `utils.py`

Common utility functions for console output, error handling, and shared operations.

**Functions:**
- `success(message)` - Print success messages with ✅ emoji
- `error(message)` - Print error messages with ❌ emoji  
- `warning(message)` - Print warning messages with ⚠️ emoji
- `info(message)` - Print info messages with ℹ️ emoji

## Dependencies

This module depends on:
- `common.properties` - For reading configuration from `properties.yml`
- Standard library: `pathlib`, `shutil`
- Internal CLI helper: `modules/common/cli.py` (TUI-safe prompt/confirm/option handling)

## Architecture

The common module follows these principles:
- **Shared utilities only** - Functions used by multiple modules
- **No business logic** - Pure utility functions
- **Minimal dependencies** - Only depends on standard library and config
- **Clear error messages** - User-friendly output with emojis
- **Type hints** - Full type annotations for all functions

## Integration

Other modules import from common:

```python
from modules.common.utils import success, error, warning, info
```
