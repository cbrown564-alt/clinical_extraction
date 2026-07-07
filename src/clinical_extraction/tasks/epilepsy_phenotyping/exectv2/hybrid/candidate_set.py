"""Live, high-recall candidate set for the hybrid SeizureFrequency extractor.

Built fresh per record (no static precomputed file — satellite 04 §2). The
deterministic candidate stage is the satellite-02 Extract stage run in
*high-recall* mode: it over-generates seizure-type anchor candidates (including
anchors with no nearby frequency information, which the deterministic pipeline
would drop) and attaches a deterministic *suggestion* of the nearby frequency
attributes. The downstream clinical-assessment LLM prunes and judges; it never
sees a 250-row-scoped surface.

An optional LLM candidate extractor can be unioned in for recall the rules miss
(``llm_candidates`` argument); the deterministic candidates always anchor the
set so every dev letter gets a real candidate set.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from ..deterministic.association import associate_attributes_to_anchors
from ..deterministic.candidates import AnchorCandidate, AttributeExtraction
from ..deterministic.pipeline import _collect_anchors, _collect_attributes
from ..deterministic.rule_metadata import DEFAULT_ABLATION, AblationConfig

_SENTENCE_BREAK = re.compile(r"[.!?\n]")


@dataclass(frozen=True)
class SFCandidate:
    """One seizure-type anchor candidate offered to the assessment LLM.

    ``anchor_text`` is the seizure-type / event phrase (the gold ``text``
    basis). ``evidence`` is the enclosing clause/sentence — an exact substring
    of the letter. ``suggested_attributes`` is the deterministic guess at the
    nearby frequency attributes (may be empty for a bare anchor the rules could
    not pair with frequency information). The LLM decides whether the candidate
    is a real SeizureFrequency mention and finalizes the attributes.
    """

    candidate_id: str
    anchor_text: str
    evidence: str
    span: tuple[int, int]
    suggested_attributes: dict[str, str] = field(default_factory=dict)
    source: str = "deterministic"
    rule_id: str = ""


def _enclosing_sentence(text: str, span: tuple[int, int]) -> str:
    """Return the clause/sentence containing ``span`` (verbatim substring)."""
    start = span[0]
    while start > 0 and not _SENTENCE_BREAK.match(text[start - 1]):
        start -= 1
    end = span[1]
    while end < len(text) and not _SENTENCE_BREAK.match(text[end]):
        end += 1
    return text[start:end].strip()


def build_candidate_set(
    letter: ExectLetter,
    *,
    ablation: AblationConfig = DEFAULT_ABLATION,
    llm_candidates: Sequence[SFCandidate] | None = None,
) -> list[SFCandidate]:
    """Build the live candidate set for one letter.

    High-recall: every seizure-type anchor the rules find becomes a candidate,
    *including* anchors with no nearby frequency expression (the deterministic
    pipeline drops those; here the assessment LLM is given the chance to keep or
    reject them). Each candidate carries the deterministic attribute suggestion
    for the anchor when one exists.
    """
    text = letter.note_text
    anchors: list[AnchorCandidate] = _collect_anchors(text, ablation)
    anchors = [a for a in anchors if a.evidence and a.evidence in text]
    attributes: list[AttributeExtraction] = _collect_attributes(text, ablation)
    attributes = [a for a in attributes if a.evidence and a.evidence in text]

    # Deterministic attribute suggestions, keyed by anchor span.
    suggestions: dict[tuple[int, int], dict[str, str]] = {
        anchor.span: dict(attrs)
        for anchor, attrs in associate_attributes_to_anchors(anchors, attributes, text)
    }

    candidates: list[SFCandidate] = []
    seen: set[tuple[str, tuple[int, int]]] = set()
    for anchor in anchors:
        key = (anchor.text, anchor.span)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            SFCandidate(
                candidate_id=f"C{len(candidates)}",
                anchor_text=anchor.text,
                evidence=_enclosing_sentence(text, anchor.span) or anchor.evidence,
                span=anchor.span,
                suggested_attributes=suggestions.get(anchor.span, {}),
                source="deterministic",
                rule_id=anchor.rule_id,
            )
        )

    if llm_candidates:
        for extra in llm_candidates:
            key = (extra.anchor_text, extra.span)
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                SFCandidate(
                    candidate_id=f"C{len(candidates)}",
                    anchor_text=extra.anchor_text,
                    evidence=extra.evidence,
                    span=extra.span,
                    suggested_attributes=dict(extra.suggested_attributes),
                    source="llm",
                    rule_id=extra.rule_id,
                )
            )

    return candidates


def candidate_set_as_payload(candidates: Sequence[SFCandidate]) -> list[dict[str, object]]:
    """Serialize a candidate set for the assessment-LLM prompt payload."""
    return [
        {
            "candidate_id": c.candidate_id,
            "anchor_text": c.anchor_text,
            "evidence": c.evidence,
            "suggested_attributes": c.suggested_attributes,
        }
        for c in candidates
    ]
