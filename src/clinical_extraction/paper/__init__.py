"""Paper-facing run surface.

Live cells go through ``python -m clinical_extraction.paper``. Campaign
scripts are not a second runner family.
"""

from .cli import main
from .methods import LIVE_METHODS
from .roster import living_models

__all__ = ["LIVE_METHODS", "living_models", "main"]
