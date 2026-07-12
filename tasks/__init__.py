import sys
from pathlib import Path

from invoke import Collection

# Ensure the repo root (parent of tasks/) is importable so `modules.*` resolves
# regardless of how invoke was invoked.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from . import (  # noqa: E402  # pylint: disable=wrong-import-position
    claude,
    combos,
    dawn,
    debug,
    repo,
    ruff,
    shopify,
    skeleton,
    tests,
    uv,
    version,
    versioning,
)

namespace = Collection()
namespace.configure({"auto_dash_names": False})

namespace.add_collection(claude, name="claude")
namespace.add_collection(dawn, name="dawn")
namespace.add_collection(debug, name="debug")
namespace.add_collection(repo, name="repo")
namespace.add_collection(ruff, name="ruff")
namespace.add_collection(shopify, name="shopify")
namespace.add_collection(skeleton, name="skeleton")
namespace.add_collection(tests, name="tests")
namespace.add_collection(uv, name="uv")
namespace.add_collection(version, name="version")
namespace.add_collection(versioning, name="ver")

namespace.add_task(combos.fix, name="fix")
namespace.add_task(combos.test, name="test")
