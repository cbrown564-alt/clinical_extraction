"""Swappable semantic concept-normalization seam (convention projection).

The dedup scoring path keys a predicted concept's **surface text** against gold's
canonical convention (via a closed hand alias table), so the model is penalized for
clinically-correct facts expressed in a non-gold surface form — the convention tax
quantified in ``experiments/exectv2_convention_tax_analysis.py`` (SeizureFrequency
recall ~75% convention-recoverable; Diagnosis precision tax +0.13). The fix per the
ExECTv2 GEPA workstream reframe (2026-06-28): the *model* should determine the
clinically-relevant fact; a deterministic, **semantics-preserving** projection should
normalize it to the gold convention. This module is that projection, behind a
swappable interface so the in-sample stub can be replaced by a real UMLS map.

``ConceptNormalizer.canonicalize(entity, text, attributes)`` maps a predicted concept
to a ``CanonicalConcept(cui, phrase)`` in gold convention, or ``None`` to leave it
untouched. ``normalize_letter`` rewrites a predicted letter's mention text to the
canonical phrase (preserving the CUI) so the existing scorer reconciles it.

Backends:

* ``InSampleConceptNormalizer`` — STUB built from the gold corpus (phrase→CUI and
  CUI→canonical-phrase). Because it is derived from gold it is **in-sample / leaky**:
  its dev number is an OPTIMISTIC ceiling, NOT a deployable or test-safe result. It
  exists to read the headroom of perfect convention reconciliation before investing
  in a real ontology.
* ``UmlsConceptNormalizer`` — the test-safe drop-in (NOT yet implemented): maps free
  clinical text → CUI via a real UMLS resource (MRCONSO), independent of gold, so it
  generalizes to ``test`` and other corpora. Acquire UMLS (NLM UTS license) to fill it.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Protocol, runtime_checkable

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

#: Families whose headline key is concept-identity (text-keyed), where convention
#: normalization applies. Prescription/Investigations are component-keyed on
#: attributes (drug/modality), where the tax is small, so they are left untouched.
DEFAULT_ENTITIES: tuple[str, ...] = ("Diagnosis", "SeizureFrequency")


@dataclass(frozen=True)
class CanonicalConcept:
    """A predicted concept resolved to gold convention."""

    cui: str | None
    phrase: str


@runtime_checkable
class ConceptNormalizer(Protocol):
    """Map a predicted concept to its gold-convention canonical form."""

    def canonicalize(
        self, entity: str, text: str, attributes: Mapping[str, str]
    ) -> CanonicalConcept | None: ...


class InSampleConceptNormalizer:
    """Gold-derived concept normalizer — an OPTIMISTIC, leaky, dev-only stub.

    Built from a gold corpus: ``phrase→CUI`` (assigns a CUI to a predicted phrase
    when that phrasing was attested in gold) and ``CUI→canonical-phrase`` (the
    gold-preferred surface form for a concept). Both directions see gold, so its dev
    number is a ceiling, not a result. Swap for ``UmlsConceptNormalizer`` to deploy.
    """

    def __init__(
        self,
        phrase_to_cui: Mapping[str, Mapping[str, str]],
        cui_to_phrase: Mapping[str, Mapping[str, str]],
        entities: Sequence[str] = DEFAULT_ENTITIES,
    ) -> None:
        self._phrase_to_cui = {e: dict(m) for e, m in phrase_to_cui.items()}
        self._cui_to_phrase = {e: dict(m) for e, m in cui_to_phrase.items()}
        self._entities = tuple(entities)

    @classmethod
    def from_gold(
        cls,
        letters: Sequence[ExectLetter],
        entities: Sequence[str] = DEFAULT_ENTITIES,
    ) -> InSampleConceptNormalizer:
        phrase_to_cui: dict[str, dict[str, str]] = {}
        cui_to_phrase: dict[str, dict[str, str]] = {}
        for entity in entities:
            phrase_votes: dict[str, Counter] = defaultdict(Counter)
            cui_phrase_votes: dict[str, Counter] = defaultdict(Counter)
            for letter in letters:
                for ann in letter.entities(entity):
                    cui = ann.attributes.get("CUI")
                    if not cui:
                        continue
                    surfaces = {normalize_phrase(ann.text)}
                    cui_phrase = ann.attributes.get("CUIPhrase")
                    if cui_phrase:
                        surfaces.add(normalize_phrase(cui_phrase))
                    for surface in surfaces:
                        if surface:
                            phrase_votes[surface][cui] += 1
                    # Canonical surface = the gold CUIPhrase if present, else the text.
                    canonical = normalize_phrase(cui_phrase or ann.text)
                    if canonical:
                        cui_phrase_votes[cui][canonical] += 1
            phrase_to_cui[entity] = {
                surface: votes.most_common(1)[0][0] for surface, votes in phrase_votes.items()
            }
            cui_to_phrase[entity] = {
                cui: votes.most_common(1)[0][0] for cui, votes in cui_phrase_votes.items()
            }
        return cls(phrase_to_cui, cui_to_phrase, entities)

    def canonicalize(
        self, entity: str, text: str, attributes: Mapping[str, str]
    ) -> CanonicalConcept | None:
        if entity not in self._entities:
            return None
        cui = attributes.get("CUI") or self._phrase_to_cui.get(entity, {}).get(normalize_phrase(text))
        if not cui:
            return None
        canonical = self._cui_to_phrase.get(entity, {}).get(cui)
        if not canonical:
            return None
        return CanonicalConcept(cui=cui, phrase=canonical)


class UmlsConceptNormalizer:
    """Test-safe concept normalizer backed by a real UMLS resource — NOT YET BUILT.

    Intended to map free clinical text → CUI via UMLS MRCONSO (or the UTS API),
    independent of the gold corpus, so it generalizes to ``test`` and other datasets.
    Acquire UMLS (NLM UTS account + license, download MRCONSO.RRF) and implement
    ``canonicalize`` against it, then swap it in for ``InSampleConceptNormalizer``.
    """

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError(
            "UmlsConceptNormalizer requires a UMLS resource (MRCONSO.RRF / UTS API), "
            "not yet available. Use InSampleConceptNormalizer (dev-only stub) meanwhile."
        )

    def canonicalize(
        self, entity: str, text: str, attributes: Mapping[str, str]
    ) -> CanonicalConcept | None:  # pragma: no cover - placeholder
        raise NotImplementedError


def normalize_letter(letter: ExectLetter, normalizer: ConceptNormalizer) -> ExectLetter:
    """Rewrite a letter's mention text to gold-convention canonical form.

    Preserves semantics: only the surface phrase (and CUI) is normalized; attributes,
    evidence, and offsets are untouched. Mentions the normalizer cannot resolve pass
    through unchanged.
    """

    new_annotations = []
    for ann in letter.annotations:
        canonical = normalizer.canonicalize(ann.entity, ann.text, ann.attributes)
        if canonical is None:
            new_annotations.append(ann)
            continue
        attributes = dict(ann.attributes)
        if canonical.cui:
            attributes["CUI"] = canonical.cui
        new_annotations.append(replace(ann, text=canonical.phrase, attributes=attributes))
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text=letter.note_text,
        annotations=tuple(new_annotations),
    )
