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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import \
load_letters, SEIZURE_FREQUENCY; \
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import \
normalize_phrase; ..."
"""
from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import normalize_phrase

# CUI → normalized concept-phrase variants observed in gold (canonical phrase
# first). Counts in comments are gold-mention frequencies, 2026-06-10 corpus.
SF_CUI_LEXICON: dict[str, tuple[str, ...]] = {
    # Generic seizure (111). Bare "seizure"/"seizures" resolve here.
    "C0036572": ("seizures", "seizure"),
    # Generalised tonic-clonic seizure (32).
    "C0494475": (
        "generalised tonic clonic seizures",
        "generalised tonic clonic seizure",
        "generalized tonic clonic seizures",
        "tonic clonic seizures",
        "tonic clonic seizure",
        "generalised",
        "grand mal",
    ),
    # Focal to bilateral convulsive seizure (24).
    "C0877017": (
        "focal to bilateral convulsive seizures",
        "focal to bilateral convulsive seizure",
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
    "C0563606": ("absences", "absence", "absence like seizures"),
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

# Bare tokens that appear under more than one CUI in gold (truncation
# artifacts). Listed here so the inversion below resolves them deterministically
# to the dominant CUI rather than depending on dict ordering.
_COLLISION_RESOLUTION: dict[str, str] = {
    "seizure": "C0036572",  # vs C1299590 (seizure-free)
    "focal": "C0877017",  # vs C0751495 (focal), C0016399 (focal-motor)
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


def assign_cui(phrase: str) -> str | None:
    """Return the SeizureFrequency CUI for an anchor phrase, or None if unknown.

    ``phrase`` is normalized with the same ``normalize_phrase`` scoring uses, so
    surface variation (hyphens, quotes, case, whitespace) does not matter. An
    unknown phrase returns None — the mention is then emitted without a CUI
    rather than guessing, keeping the lexicon's precision intact."""
    return PHRASE_TO_CUI.get(normalize_phrase(phrase))
