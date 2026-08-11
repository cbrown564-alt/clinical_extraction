"""Shared regex fragments for selected-evidence span matching."""

from __future__ import annotations

#: Up to 4 filler words (with optional internal hyphen) before a seizure-term list.
GAP_WORDS_TOKEN = r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"

#: Wider variant allowing up to 5 filler words.
GAP_WORDS_TOKEN_5 = r"(?:[a-z]+(?:-[a-z]+)?\s+){0,5}"
