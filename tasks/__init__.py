import sys
from pathlib import Path

from invoke import Collection

# Ensure the repo root (parent of tasks/) is importable so `modules.*` resolves
# regardless of how invoke was invoked.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from . import shopify, versioning  # noqa: E402  # pylint: disable=wrong-import-position
from .common import debug  # noqa: E402  # pylint: disable=wrong-import-position
from .tests import namespace as tests_namespace  # noqa: E402  # pylint: disable=wrong-import-position

namespace = Collection(auto_dash_names=False)

# `common/` groups boilerplate inherited from template_python (debug only here — ruff/setup don't
# apply to this repo: theme-check/ruff run directly via tests.*, and properties.yml is committed
# directly with no per-machine stamping) — kept at its original top-level name (`debug.*`), not
# nested under `common.*`, matching template_python's own convention. `shopify.*`/`ver.*` are this
# repo's own reason for existing (Shopify theme CI + release versioning) and stay flat.
namespace.add_collection(debug, name="debug")
namespace.add_collection(shopify, name="shopify")
namespace.add_collection(tests_namespace, name="tests")
namespace.add_collection(versioning, name="ver")
