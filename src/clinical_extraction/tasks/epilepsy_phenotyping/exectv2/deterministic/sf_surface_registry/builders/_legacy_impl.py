"""SeizureFrequency benchmark rewrite dictionary (Stack B — legacy implementation).

.. deprecated::
    Prefer ``sf_surface_registry.adapters.convention`` for new imports.
    Shared regex patterns live in ``sf_surface_registry.patterns`` (Phase 1).
    This module remains the authoritative rewrite implementation until Phase 2
    migrates branches into ``catalog/convention_rewrite.yaml``; it will become
    a thin re-export shim for one release cycle after adapter parity lands.

See ``sf_surface_registry/README.md`` for migration status.
"""

from __future__ import annotations

from ._legacy_constants import *  # noqa: F401,F403
from ._legacy_constants import __all__ as _constants_all
from ._legacy_noise import *  # noqa: F401,F403
from ._legacy_noise import __all__ as _noise_all
from ._legacy_residual import *  # noqa: F401,F403
from ._legacy_residual import __all__ as _residual_all
from ._legacy_rewrite import *  # noqa: F401,F403
from ._legacy_rewrite import __all__ as _rewrite_all

__all__ = [
    *_constants_all,
    *_rewrite_all,
    *_noise_all,
    *_residual_all,
]
