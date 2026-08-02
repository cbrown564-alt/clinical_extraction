from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel

from clinical_extraction.core.schemas import EvidenceSpan
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)


class PredictedMention(BaseModel):
    model_config = {"frozen": True}

    entity: str
    text: str
    attributes: Mapping[str, str]
    evidence: str
    evidence_span: EvidenceSpan | None = None
    rationale: str = ""
    confidence: Literal["low", "medium", "high"] | None = None
    uncertainty_flags: tuple[str, ...] = ()
    component_owner: str = ""

    def model_post_init(self, _context: Any) -> None:
        object.__setattr__(self, "attributes", _freeze_mapping(self.attributes))


class PredictedLetter(BaseModel):
    model_config = {"frozen": True}

    letter_id: str
    mentions: tuple[PredictedMention, ...]
    diagnostics: Mapping[str, Any] = {}

    def model_post_init(self, _context: Any) -> None:
        object.__setattr__(self, "diagnostics", _freeze_mapping(self.diagnostics))


class _ImmutableDict(dict[str, Any]):
    def _immutable(self, *_args: Any, **_kwargs: Any) -> None:
        raise TypeError("producer values are immutable")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _immutable  # type: ignore[assignment]


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    frozen = _ImmutableDict()
    dict.update(
        frozen,
        {
            key: _freeze_mapping(item) if isinstance(item, Mapping) else item
            for key, item in value.items()
        },
    )
    return frozen


def to_exect_annotation(mention: PredictedMention) -> ExectAnnotation:
    """Drop transparency fields; produce a scorer-compatible annotation."""
    return ExectAnnotation(
        entity=mention.entity,
        text=mention.text,
        attributes=dict(mention.attributes),
    )


def to_exect_letter(letter: PredictedLetter, note_text: str = "") -> ExectLetter:
    """Adapt a PredictedLetter into the shape score_entity consumes."""
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text=note_text,
        annotations=tuple(to_exect_annotation(m) for m in letter.mentions),
    )
