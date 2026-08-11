"""`tests` collection — one file per check (was a single flat `tasks/tests.py`), still registered
as one flat `tests.*` namespace (`tests.actionlint`, `tests.theme_check`, etc.) so nothing that
calls these tasks needs to change.
"""

from invoke import Collection

from .actionlint import actionlint
from .pylint import pylint
from .rufflint import rufflint
from .theme_check import theme_check
from .yamllint import yamllint

namespace = Collection(auto_dash_names=False)
namespace.add_task(actionlint, name="actionlint")
namespace.add_task(pylint, name="pylint")
namespace.add_task(rufflint, name="rufflint")
namespace.add_task(theme_check, name="theme_check")
namespace.add_task(yamllint, name="yamllint")
