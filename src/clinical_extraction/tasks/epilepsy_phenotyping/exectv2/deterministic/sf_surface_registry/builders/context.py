"""Convention-phase context passed to registry builders."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    normalize_phrase,
)

RewriteResult = tuple[str, dict[str, Any], str]
ResidualCandidate = tuple[str, str, dict[str, str]]


@dataclass
class ConventionContext:
    text: str
    evidence: str
    attributes: Mapping[str, Any]
    attrs: dict[str, Any] = field(init=False)
    phrase: str = field(init=False)
    surface: str = field(init=False)

    def __post_init__(self) -> None:
        self.attrs = dict(self.attributes)
        self.phrase = normalize_phrase(self.text)
        self.surface = " ".join(part for part in (self.text, self.evidence) if part)
