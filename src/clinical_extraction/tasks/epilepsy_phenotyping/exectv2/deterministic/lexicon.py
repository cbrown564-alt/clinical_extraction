"""Phrase → CUI lexicon for ExECTv2 SeizureFrequency (gap 1, plan satellite 02).

All 261 gold SF mentions carry a ``CUI`` (16 distinct), so the
benchmark-comparable ``sf_benchmark`` match config (which keeps ``CUI`` in the
match key) is structurally 0 until the deterministic family emits one. This
module is the finite, source-grounded lexicon that closes that gap: it maps the
seizure-type *concept phrase* an anchor extracts to its UMLS CUI.

The map is keyed on the gold ``CUIPhrase`` values (the canonical seizure-type
name annotated alongside each mention), normalized with
``scoring.normalize_phrase`` so lookup is robust to hyphen/quote/case surface
variation — the same normalization scoring uses for phrase matching. Keying on
``CUIPhrase`` (44 distinct variants) rather than the raw mention ``text`` (which
often embeds temporal context, e.g. "2 generalised tonic clonic seizures in
2014") is what makes the map finite and almost collision-free.

**Collisions (2, both resolved to the dominant gold CUI):**

- ``"seizure"`` — C0036572 (generic seizure, 36 mentions) vs C1299590
  (seizure-free, 4). The 4 C1299590 cases are offset-drift truncations of
  "seizure free"; the seizure-free anchor rule emits the full "seizure free"
  phrase, which maps unambiguously to C1299590, so bare "seizure" → C0036572.
- ``"focal"`` — C0877017 (focal-to-bilateral, 3) vs C0751495 (focal, 1) vs
  C0016399 (focal-motor, 1). All three are truncations; the anchor normally
  emits the full phrase. Bare "focal" → C0877017 by dominance.

Both bare-token keys are low-confidence (truncation artifacts); the anchor rules
emit the full phrase in the common case, which keys unambiguously.

Portability tag: ``benchmark_format`` — this is a finite ontology lookup shaped
to the benchmark's annotation conventions, not a general clinical rule.

Regenerate the gold inventory behind this map with::

    uv run python -c "from collections import Counter, defaultdict; \
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters; \
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import \
SEIZURE_FREQUENCY; \
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import \
normalize_phrase; ..."
"""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")

_CLUSTER_OF_SEIZURES_RE = re.compile(r"\bclusters?\s+of\s+seizures?\b", re.I)
_GENERLISED_RE = re.compile(r"generlised", re.I)

# CUI → normalized concept-phrase variants observed in gold (canonical phrase
# first). Counts in comments are gold-mention frequencies, 2026-06-10 corpus.
SF_CUI_LEXICON: dict[str, tuple[str, ...]] = {
    # Generic seizure (111). Bare "seizure"/"seizures" resolve here.
    "C0036572": ("seizures", "seizure", "no further seizures"),
    # Generalised tonic-clonic seizure (32).
    "C0494475": (
        "generalised tonic clonic seizures",
        "generalised tonic clonic seizure",
        "generalized tonic clonic seizures",
        "generalised tonic chronic seizures",
        "generalized tonic chronic seizures",
        "tonic clonic seizures",
        "tonic clonic seizure",
        "generalised",
        "grand mal",
    ),
    # Focal to bilateral convulsive seizure (24).
    "C0877017": (
        "focal to bilateral convulsive seizures",
        "focal to bilateral convulsive seizure",
        "focal to bilateral seizures",
        "focal to bilateral seizure",
        "bilateral convulsive seizures",
        "focal",
    ),
    # Seizure-free / seizure freedom (17).
    "C1299590": ("seizure free", "seizure freedom"),
    # Focal seizure with impaired awareness / dyscognitive (16).
    "C0270834": (
        "focal seizures with altered awareness",
        "focal seizures with loss of awareness",
        "focal seizures with impaired awareness",
        "focal impaired awareness seizures",
        "focal dyscognitive seizures",
        "dyscognitive seizures",
        "dyscognitive",
    ),
    # Secondary generalised seizure (11).
    "C0270838": (
        "secondary generalised seizures",
        "secondary generalised seizure",
        "secondary generalized seizures",
        "secondarily generalised seizures",
    ),
    # Absence seizure (10).
    "C0563606": ("absences", "absence", "absence like seizures", "absence events"),
    # Myoclonic jerk (8).
    "C0027066": ("myoclonic jerks", "myoclonic jerk"),
    # Focal seizure (6).
    "C0751495": ("focal seizures", "focal seizure"),
    # Focal motor seizure (6).
    "C0016399": (
        "focal motor seizures",
        "focal motor seizure",
        "partial motor seizures",
    ),
    # Complex partial seizure (6).
    "C0149958": ("complex partial seizures", "complex partial seizure", "complex"),
    # Generalised seizure (5).
    "C0234533": ("generalised seizures", "generalised seizure", "generalised convulsions"),
    # Cluster of seizures (4).
    "C3203523": ("cluster of seizures", "seizure cluster"),
    # Convulsive seizure (3).
    "C0751494": ("convulsive seizure",),
    # Frontal lobe seizure (1).
    "C0085541": ("frontal lobe seizure", "frontal lobe seizures", "focal frontal lobe seizures"),
    # Typical absences (1).
    "C4316903": ("typical absences",),
}

GENERIC_SEIZURE_CUI = "C0036572"
GENERIC_SEIZURE_FREE_CUI = "C1299590"
GENERIC_SF_CUIS = frozenset({GENERIC_SEIZURE_CUI, GENERIC_SEIZURE_FREE_CUI})
GENERIC_SF_PHRASES = frozenset({"seizure", "seizures", "seizure free", "seizure-free"})

# Bare tokens that appear under more than one CUI in gold (truncation
# artifacts). Listed here so the inversion below resolves them deterministically
# to the dominant CUI rather than depending on dict ordering.
_COLLISION_RESOLUTION: dict[str, str] = {
    "seizure": "C0036572",  # vs C1299590 (seizure-free)
    "focal": "C0877017",  # vs C0751495 (focal), C0016399 (focal-motor)
}

# Model extract rows sometimes use a generic event word or omit the noun after
# a well-known type adjective. These are standard-name repairs only after the
# row has already been typed as SeizureFrequency; they are not extraction
# aliases and are intentionally narrow.
_SF_STANDARD_NAME_ALIASES: dict[str, str] = {
    "episode": "C0036572",
    "episodes": "C0036572",
    "tonic clonic": "C0494475",
}


def _build_phrase_to_cui() -> dict[str, str]:
    inverted: dict[str, str] = {}
    for cui, phrases in SF_CUI_LEXICON.items():
        for phrase in phrases:
            key = normalize_phrase(phrase)
            if key in _COLLISION_RESOLUTION:
                inverted[key] = _COLLISION_RESOLUTION[key]
            elif key in inverted and inverted[key] != cui:
                raise ValueError(
                    f"Unresolved phrase→CUI collision: {key!r} maps to both "
                    f"{inverted[key]!r} and {cui!r}; add it to _COLLISION_RESOLUTION."
                )
            else:
                inverted[key] = cui
    return inverted


# Normalized phrase → CUI. The single source consulted by ``assign_cui``.
PHRASE_TO_CUI: dict[str, str] = _build_phrase_to_cui()


def _longest_known_phrase_cui(phrase: str) -> str | None:
    haystack = normalize_phrase(phrase)
    if not haystack:
        return None
    for key in sorted(PHRASE_TO_CUI, key=len, reverse=True):
        if key and key in haystack:
            return PHRASE_TO_CUI[key]
    return None


def fold_seizure_type_phrase(phrase: str, cui: str | None = None) -> str:
    """Return the canonical seizure-type head for a phrase or attached CUI.

    Exact phrase lookup wins, then the longest known type string inside the
    wording, then attached CUI. A wrong attached id does not override a
    known type name.
    """

    resolved = assign_cui(phrase) or _longest_known_phrase_cui(phrase)
    if resolved is None and cui:
        resolved = cui
    if resolved in SF_CUI_LEXICON:
        return normalize_phrase(SF_CUI_LEXICON[resolved][0])
    return normalize_phrase(phrase)


def canonical_seizure_type_name(phrase: str) -> str:
    """Return the closed 16-head standard name for a known SF type phrase."""

    normalized = normalize_phrase(phrase)
    resolved = assign_cui(phrase) or _longest_known_phrase_cui(phrase)
    if resolved is None:
        resolved = _SF_STANDARD_NAME_ALIASES.get(normalized)
    if resolved in SF_CUI_LEXICON:
        return SF_CUI_LEXICON[resolved][0]
    return phrase


def evidence_refined_seizure_type_name(phrase: str, evidence: str) -> str:
    """Use one unambiguous named type in local evidence to refine ``phrase``.

    This only changes generic seizure names, or the parent ``absence`` name
    when the evidence explicitly says ``typical absence``. If the evidence
    names more than one distinct seizure type, ownership remains unresolved and
    the original phrase is preserved.
    """

    current_cui = assign_cui(phrase)
    normalized = normalize_phrase(phrase)
    if current_cui == "C0563606" and re.search(
        r"\btypical\s+absences?\b", evidence, re.IGNORECASE
    ):
        return SF_CUI_LEXICON["C4316903"][0]
    evidence_hits = _maximal_evidence_type_hits(evidence)
    hit_cuis = {cui for _start, _end, cui in evidence_hits}
    if normalized not in {"seizure", "episode"}:
        return phrase
    if len(hit_cuis) != 1:
        return phrase
    resolved = next(iter(hit_cuis))
    return SF_CUI_LEXICON[resolved][0]


def _maximal_evidence_type_hits(evidence: str) -> list[tuple[int, int, str]]:
    """Return non-nested named seizure-type spans from local evidence."""

    normalized_evidence = evidence.translate(_QUOTES).replace("-", " ").lower()
    hits: list[tuple[int, int, str]] = []
    for phrase, cui in PHRASE_TO_CUI.items():
        if cui in GENERIC_SF_CUIS or len(phrase.split()) < 2:
            continue
        pattern_text = re.escape(phrase)
        for singular in ("seizure", "absence", "jerk", "convulsion", "episode"):
            if phrase.endswith(singular):
                pattern_text = re.escape(phrase[: -len(singular)]) + singular + "s?"
                break
        pattern = re.compile(rf"(?<!\w){pattern_text}(?!\w)", re.IGNORECASE)
        hits.extend(
            (match.start(), match.end(), cui)
            for match in pattern.finditer(normalized_evidence)
        )
    return [
        hit
        for hit in hits
        if not any(
            other[0] <= hit[0]
            and other[1] >= hit[1]
            and (other[1] - other[0]) > (hit[1] - hit[0])
            for other in hits
        )
    ]


def assign_cui(phrase: str) -> str | None:
    """Return the SeizureFrequency CUI for an anchor phrase, or None if unknown.

    ``phrase`` is normalized with the same ``normalize_phrase`` scoring uses, so
    surface variation (hyphens, quotes, case, whitespace) does not matter. An
    unknown phrase returns None — the mention is then emitted without a CUI
    rather than guessing, keeping the lexicon's precision intact.

    Scoring ``normalize_phrase`` strips ``cluster of ``, which would collapse
    ``cluster of seizures`` onto generic ``C0036572``. Cluster phrasing is
    therefore resolved before that strip. The typo ``generlised`` is folded
    onto the existing ``generalised`` map. Neither step guesses a sibling type.
    """
    if _CLUSTER_OF_SEIZURES_RE.search(phrase):
        return "C3203523"
    folded = _GENERLISED_RE.sub("generalised", phrase)
    return PHRASE_TO_CUI.get(normalize_phrase(folded))


def attach_cui(text: str, attrs: dict[str, str]) -> dict[str, str]:
    """Add CUI/CUIPhrase to ``attrs`` when ``text`` resolves to a known CUI."""
    cui = assign_cui(text)
    if cui is None:
        return attrs
    return {**attrs, "CUI": cui, "CUIPhrase": text}
