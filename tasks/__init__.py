import sys
from pathlib import Path

from invoke import Collection

# Ensure the repo root (parent of tasks/) is importable so `modules.*` resolves
# regardless of how invoke was invoked.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from . import (  # noqa: E402  # pylint: disable=wrong-import-position
    debug,
    shopify,
    tests,
    versioning,
)

namespace = Collection()
namespace.configure({"auto_dash_names": False})

namespace.add_collection(debug, name="debug")
namespace.add_collection(shopify, name="shopify")
namespace.add_collection(tests, name="tests")
namespace.add_collection(versioning, name="ver")
