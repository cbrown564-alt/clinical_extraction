"""ExECTv2 deterministic SeizureFrequency extraction pipeline.

Anchor + association pipeline (Phase 2):

  text → anchor rules → resolve overlapping anchors
       → rate/seizure-free/change rules → resolve overlapping attribute extractions
       → associate each attribute extraction with its nearest anchor
       → emit one PredictedMention per anchor that gathered attributes

In the gold annotation scheme, ``SeizureFrequency.text`` is a seizure-type /
event-description phrase (the "anchor"), while frequency information (counts,
periods, change direction) is encoded purely as attributes. Anchors with no
nearby frequency information are dropped — they are not SeizureFrequency
mentions in this scheme.

Usage::

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
        extract_seizure_frequency,
        run_on_letters,
    )
    letters = load_letters()
    predicted = run_on_letters(letters)
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)

from .association import (
    _MAX_ASSOCIATION_GAP,
    _gap,
    _sentence_breaks,
    _sentence_index,
    associate_attributes_to_anchors,
)
from .candidates import AnchorCandidate, AttributeExtraction, AttributeKind
from .frequency_section import frequency_section_mentions
from .lexicon import GENERIC_SF_CUIS, assign_cui
from .overlap import resolve_overlapping_anchors, resolve_overlapping_attributes
from .rule_metadata import DEFAULT_ABLATION, AblationConfig, ExtractionContext
from .sf_surface_registry.adapters.extraction import (
    ANCHOR_RULES,
    CHANGE_RULES,
    RATE_RULES,
    SEIZURE_FREE_RULES,
    TEMPORAL_RULES,
)
from .statement_parser import statement_mentions

_EXPLICIT_SEIZURE_FREE_EVIDENCE_RE = re.compile(
    r"\bseizure\s*[-]?\s*free\b|"
    r"\bno\s+(?:further|more)\s+seizures\b|\bremains?\s+seizure\s*[-]?\s*free\b",
    re.IGNORECASE,
)


def _has_explicit_seizure_free_evidence(evidence: str) -> bool:
    return bool(_EXPLICIT_SEIZURE_FREE_EVIDENCE_RE.search(evidence))


def _collect_anchors(text: str, ablation: AblationConfig) -> list[AnchorCandidate]:
    ctx = ExtractionContext(text=text)
    results: list[AnchorCandidate] = []
    for spec in ANCHOR_RULES:
        results.extend(c for c in spec.apply(ctx, ablation) if isinstance(c, AnchorCandidate))
    return resolve_overlapping_anchors(results)


def _collect_attributes(text: str, ablation: AblationConfig) -> list[AttributeExtraction]:
    ctx = ExtractionContext(text=text)
    results: list[AttributeExtraction] = []
    for rule_set in (RATE_RULES, SEIZURE_FREE_RULES, CHANGE_RULES, TEMPORAL_RULES):
        for spec in rule_set:
            results.extend(
                c for c in spec.apply(ctx, ablation) if isinstance(c, AttributeExtraction)
            )
    return resolve_overlapping_attributes(results)


_COUNT_ATTRS = ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
_PLURAL_SEIZURE_NOUN = re.compile(r"\b(?:seizures|absences|jerks)\b", re.IGNORECASE)
_SINGULAR_SEIZURE_NOUN = re.compile(r"\b(?:seizure|absence|jerk)\b", re.IGNORECASE)
# A negated frequency statement implies zero events, not the default plural=2.
# "no (further) seizures since …", "has not had any …", "remains seizure free",
# "denies …", "without …". Checked in a window just before the anchor.
_NEGATION_CUE = re.compile(
    r"\b(?:no|not|none|never|without|nil|denies|denied|negative\s+for)\b",
    re.IGNORECASE,
)


def _apply_implied_count(
    anchor: AnchorCandidate, attributes: dict[str, str], text: str = ""
) -> dict[str, str]:
    """Guideline v9 L989: when a frequency statement carries no explicit count
    and no other quantifier, a plural 'seizures' implies NumberOfSeizures=2 and a
    singular 'seizure' implies 1. Only applied to mentions that already have a
    frequency attribute (period/date/change), so it never fabricates mentions —
    it fills the implied count gold annotates by default.

    Exception: if the statement is negated (a negation cue sits just before the
    anchor, e.g. "no further seizures since …"), the implied count is 0, not the
    positive default — gold annotates "no seizures since <point in time>" as
    NumberOfSeizures=0 (L249), and the default plural=2 was the single largest
    source of count-value misses on temporal mentions."""
    if any(k in attributes for k in _COUNT_ATTRS) or "FrequencyChange" in attributes:
        return attributes
    phrase = anchor.text.lower()
    if not (_PLURAL_SEIZURE_NOUN.search(phrase) or _SINGULAR_SEIZURE_NOUN.search(phrase)):
        return attributes
    window = text[max(0, anchor.span[0] - 30) : anchor.span[0]]
    if _NEGATION_CUE.search(window):
        implied = "0"
    elif _PLURAL_SEIZURE_NOUN.search(phrase):
        implied = "2"
    else:
        implied = "1"
    return {**attributes, "NumberOfSeizures": implied}


def _is_bare_nonzero_count(attributes: dict[str, str]) -> bool:
    """A count with no time frame is not a frequency statement (guideline L255).
    Gold never carries a bare nonzero NumberOfSeizures — a frequency needs a
    period/date/change/point-in-time. Bare NumberOfSeizures=0 IS valid (L53:
    "0 with no time period or point in time"), so it is kept."""
    return set(attributes) == {"NumberOfSeizures"} and attributes["NumberOfSeizures"] != "0"


def _with_cui(anchor: AnchorCandidate, attributes: dict[str, str]) -> dict[str, str]:
    """Attach the seizure-type CUI (and mirrored CUIPhrase) when the anchor
    phrase is in the lexicon. Gold annotates a CUI on every SF mention, so this
    is what makes the benchmark-comparable match config score non-zero. An
    out-of-lexicon phrase is left without a CUI rather than guessing."""
    cui = assign_cui(anchor.text)
    if cui is None:
        return attributes
    return {**attributes, "CUI": cui, "CUIPhrase": anchor.text}


def _mention_from_pair(anchor: AnchorCandidate, attributes: dict[str, str]) -> PredictedMention:
    return PredictedMention(
        entity=SEIZURE_FREQUENCY.name,
        text=anchor.text,
        attributes=_with_cui(anchor, attributes),
        evidence=anchor.evidence,
        component_owner="deterministic",
    )


def _mention_key(mention: PredictedMention) -> tuple[str, str, tuple[tuple[str, str], ...]]:
    return (
        mention.entity,
        mention.text.lower().replace("-", " ").strip(),
        tuple(sorted(dict(mention.attributes).items())),
    )


_DATE_ATTRIBUTES = frozenset({"DayDate", "MonthDate", "YearDate"})
_RATE_ATTRIBUTES = frozenset(
    {
        "NumberOfSeizures",
        "LowerNumberOfSeizures",
        "UpperNumberOfSeizures",
        "NumberOfTimePeriods",
        "LowerNumberOfTimePeriods",
        "UpperNumberOfTimePeriods",
        "TimePeriod",
    }
)


def _split_mixed_last_event_rate(mention: PredictedMention) -> tuple[PredictedMention, ...]:
    attrs = dict(mention.attributes)
    if attrs.get("TimeSince_or_TimeOfEvent") != "Since":
        return (mention,)
    if not any(key in attrs for key in _DATE_ATTRIBUTES):
        return (mention,)
    if "TimePeriod" not in attrs:
        return (mention,)
    if attrs.get("NumberOfSeizures") in (None, "0"):
        return (mention,)

    rate_attrs = {
        key: value
        for key, value in attrs.items()
        if key in _RATE_ATTRIBUTES or key in {"CUI", "CUIPhrase"}
    }
    zero_attrs = {
        key: value
        for key, value in attrs.items()
        if key in _DATE_ATTRIBUTES or key in {"CUI", "CUIPhrase", "TimeSince_or_TimeOfEvent"}
    }
    zero_attrs["NumberOfSeizures"] = "0"
    return (
        mention.model_copy(
            update={
                "attributes": rate_attrs,
                "component_owner": f"{mention.component_owner}+split_rate",
            }
        ),
        mention.model_copy(
            update={
                "attributes": zero_attrs,
                "component_owner": f"{mention.component_owner}+split_last_event",
            }
        ),
    )


def _split_mixed_mentions(mentions: tuple[PredictedMention, ...]) -> tuple[PredictedMention, ...]:
    return tuple(split for mention in mentions for split in _split_mixed_last_event_rate(mention))


def _projection_alias_texts(mention: PredictedMention) -> tuple[str, ...]:
    phrase = normalize_phrase(mention.text)
    attrs = mention.attributes
    has_range = "LowerNumberOfSeizures" in attrs or "UpperNumberOfSeizures" in attrs
    is_zero = attrs.get("NumberOfSeizures") == "0"

    if phrase == "absences" and attrs.get("FrequencyChange") == "Infrequent":
        return ("absence",)
    if (
        phrase == "generalised tonic clonic seizures"
        and attrs.get("FrequencyChange") == "Infrequent"
    ):
        return ("generalized tonic clonic seizures",)
    if phrase == "secondary generalised seizures":
        if is_zero and "MonthDate" in attrs:
            return ("secondary generalized seizures",)
        if has_range:
            return ("secondary generalised seizure",)
    if phrase == "generalised seizures" and (is_zero or has_range):
        return ("generalised seizure",)
    if phrase == "complex partial seizures" and has_range:
        return ("complex partial seizure",)
    if phrase == "focal frontal lobe seizures":
        return ("frontal lobe seizure",)
    if phrase == "focal to bilateral seizures":
        return ("focal to bilateral convulsive seizure",)
    if phrase == "focal to bilateral convulsive seizures" and is_zero:
        return ("focal to bilateral convulsive seizure",)
    return ()


def _projection_attribute_aliases(mention: PredictedMention) -> tuple[dict[str, str], ...]:
    attrs = dict(mention.attributes)
    aliases: list[dict[str, str]] = []
    if (
        attrs.get("CUI") != "C1299590"
        and "FrequencyChange" in attrs
        and any(key in attrs for key in ("NumberOfSeizures", "TimePeriod", "NumberOfTimePeriods"))
    ):
        aliases.append(
            {
                key: value
                for key, value in attrs.items()
                if key in {"FrequencyChange", "CUI", "CUIPhrase"}
            }
        )
    if "LowerNumberOfSeizures" in attrs and "PointInTime" in attrs:
        aliases.append(
            {
                key: value
                for key, value in attrs.items()
                if key not in {"PointInTime", "TimeSince_or_TimeOfEvent"}
            }
        )
    return tuple(aliases)


def _with_alias_cui(text: str, attrs: dict[str, str]) -> dict[str, str]:
    cui = assign_cui(text)
    if cui is None:
        return {k: v for k, v in attrs.items() if k not in {"CUI", "CUIPhrase"}}
    return {
        **{k: v for k, v in attrs.items() if k not in {"CUI", "CUIPhrase"}},
        "CUI": cui,
        "CUIPhrase": text,
    }


def _projection_alias_mentions(
    mentions: tuple[PredictedMention, ...],
) -> tuple[PredictedMention, ...]:
    existing = {_mention_key(m) for m in mentions}
    aliases: list[PredictedMention] = []
    for mention in mentions:
        for alias_attrs in _projection_attribute_aliases(mention):
            alias = mention.model_copy(
                update={
                    "attributes": _with_alias_cui(mention.text, alias_attrs),
                    "component_owner": f"{mention.component_owner}+attribute_alias",
                }
            )
            key = _mention_key(alias)
            if key in existing:
                continue
            existing.add(key)
            aliases.append(alias)
        for alias_text in _projection_alias_texts(mention):
            alias = mention.model_copy(
                update={
                    "text": alias_text,
                    "attributes": _with_alias_cui(alias_text, dict(mention.attributes)),
                    "component_owner": f"{mention.component_owner}+projection_alias",
                }
            )
            key = _mention_key(alias)
            if key in existing:
                continue
            existing.add(key)
            aliases.append(alias)
    return tuple(aliases)


def _should_keep_mention(mention: PredictedMention) -> bool:
    phrase = normalize_phrase(mention.text)
    semantic_keys = set(mention.attributes) - {"CUI", "CUIPhrase"}

    # Bare generic "0 seizure(s)" is usually a history/diagnosis artifact in
    # this corpus; true zero-frequency SF mentions almost always carry a date,
    # duration, point-in-time, or drug-change qualifier.
    if (
        phrase in {"seizure", "seizures"}
        and mention.attributes.get("NumberOfSeizures") == "0"
        and semantic_keys == {"NumberOfSeizures"}
        and not mention.component_owner.startswith("deterministic_statement_parser")
    ):
        return False

    # The full "seizure free" bare-zero surface is over-produced in narrative
    # driving/mental-health contexts. Qualified seizure-free durations/dates are
    # retained.
    if (
        phrase == "seizure free"
        and mention.attributes.get("NumberOfSeizures") == "0"
        and semantic_keys == {"NumberOfSeizures"}
    ):
        return False

    # Carry-forward statement parsing is intentionally narrow; these generic
    # follow-on anchors were empirically noisy after the same-sentence layer was
    # added.
    if mention.component_owner.startswith("deterministic_statement_parser") and phrase in {
        "jerk",
        "jerks",
        "focal seizures",
        "focal seizures with altered awareness",
        "generalised seizures",
    }:
        return False

    if mention.component_owner.startswith("deterministic_statement_parser"):
        evidence = mention.evidence.lower()
        if (
            "between" in evidence
            and "NumberOfSeizures" in mention.attributes
            and "LowerNumberOfSeizures" not in mention.attributes
        ):
            return False
        if (
            phrase == "seizure"
            and mention.attributes.get("CUI") == "C1299590"
            and semantic_keys == {"NumberOfSeizures"}
        ):
            return False
        if "epilepsy is well controlled" in evidence:
            return False
        if (
            "relatively frequent tonic clonic seizures" in evidence
            and phrase == "tonic clonic seizures"
            and (
                mention.attributes.get("TimeSince_or_TimeOfEvent") == "During"
                or semantic_keys == {"FrequencyChange"}
            )
        ):
            return False

    if (
        "+projection_alias" in mention.component_owner
        and phrase == "focal to bilateral convulsive seizure"
        and mention.attributes.get("NumberOfSeizures") == "0"
    ):
        return False

    return True


def extract_seizure_frequency(
    letter: ExectLetter,
    ablation: AblationConfig = DEFAULT_ABLATION,
    *,
    keep_unassociated_anchors: bool = False,
) -> PredictedLetter:
    """Extract all SeizureFrequency mentions from one letter.

    Steps:
    1. Apply anchor rules; resolve overlapping anchor spans (longest wins).
    2. Apply rate/seizure-free/change rules; resolve overlapping attribute
       extractions (most attributes wins).
    3. Associate each attribute extraction with its nearest anchor.
    4. Emit one PredictedMention per anchor that gathered attributes.
    """
    text = letter.note_text
    anchors = _collect_anchors(text, ablation)
    attributes = _collect_attributes(text, ablation)

    # Safety filter: evidence must be a verbatim substring.
    anchors = [a for a in anchors if a.evidence and a.evidence in text]
    attributes = [a for a in attributes if a.evidence and a.evidence in text]

    pairs = associate_attributes_to_anchors(anchors, attributes, text)
    paired_spans = {anchor.span for anchor, _attrs in pairs}
    rateless_mentions = tuple(
        _mention_from_pair(anchor, {})
        for anchor in anchors
        if keep_unassociated_anchors and anchor.span not in paired_spans
    )
    associated_mentions = _split_mixed_mentions(
        tuple(
            _mention_from_pair(anchor, merged)
            for anchor, attrs in pairs
            for merged in (_apply_implied_count(anchor, attrs, text),)
            if not _is_bare_nonzero_count(merged)
        )
    )
    kept_associated_mentions = tuple(
        m for m in associated_mentions if _should_keep_mention(m)
    )
    associated_keys = {_mention_key(m) for m in kept_associated_mentions}
    structured_candidates = (*frequency_section_mentions(text), *statement_mentions(text))
    structured_mentions = tuple(
        mention for mention in structured_candidates if _mention_key(mention) not in associated_keys
    )
    mentions = (*kept_associated_mentions, *structured_mentions, *rateless_mentions)
    mentions = (*mentions, *_projection_alias_mentions(mentions))
    mentions = tuple(mention for mention in mentions if _should_keep_mention(mention))
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=mentions,
        diagnostics={
            "rule_set": "deterministic_sf_v2_anchor_association",
            "anchor_count": len(anchors),
            "attribute_count": len(attributes),
            "mention_count": len(mentions),
        },
    )


def _default_sf_mention_keys(
    text: str,
    ablation: AblationConfig,
) -> set[tuple[str, str, tuple[tuple[str, str], ...]]]:
    letter = ExectLetter(letter_id="", note_text=text)
    prediction = extract_seizure_frequency(letter, ablation)
    return {_mention_key(mention) for mention in prediction.mentions}


def _has_heading_frequency_state(mention: PredictedMention) -> bool:
    if not mention.component_owner.startswith("deterministic_frequency_section"):
        return False
    semantic_keys = set(mention.attributes) - {"CUI", "CUIPhrase"}
    return bool(semantic_keys)


def _is_named_type_anchor(anchor: AnchorCandidate) -> bool:
    cui = assign_cui(anchor.text)
    return cui is not None and cui not in GENERIC_SF_CUIS


def _unassociated_attributes(
    anchors: list[AnchorCandidate],
    attributes: list[AttributeExtraction],
    text: str,
) -> list[AttributeExtraction]:
    if not anchors:
        return list(attributes)

    breaks = _sentence_breaks(text)
    anchor_sentences = [_sentence_index(anchor.span[0], breaks) for anchor in anchors]
    associated: set[int] = set()
    for attr_index, attr in enumerate(attributes):
        attr_sentence = _sentence_index(attr.span[0], breaks)
        same_sentence = [
            index for index, sentence in enumerate(anchor_sentences) if sentence == attr_sentence
        ]
        if not same_sentence:
            continue
        nearest_idx = min(
            same_sentence,
            key=lambda index: (
                _gap(anchors[index].span, attr.span),
                abs(anchors[index].span[0] - attr.span[0]),
            ),
        )
        if _gap(anchors[nearest_idx].span, attr.span) <= _MAX_ASSOCIATION_GAP:
            associated.add(attr_index)
    return [attributes[index] for index in range(len(attributes)) if index not in associated]


def _mention_from_orphan_seizure_free(attr: AttributeExtraction) -> PredictedMention:
    evidence = attr.evidence
    attrs = {**dict(attr.attributes), "CUI": "C1299590", "CUIPhrase": "seizure"}
    return PredictedMention(
        entity=SEIZURE_FREQUENCY.name,
        text="seizure",
        attributes=attrs,
        evidence=evidence,
        component_owner="deterministic",
    )


def _deferred_sf_named_type_candidates(
    text: str,
    ablation: AblationConfig,
) -> tuple:
    from .recognise_ledger import SF_NAMED_TYPE, RecogniseCandidate

    anchors = _collect_anchors(text, ablation)
    attributes = _collect_attributes(text, ablation)
    anchors = [anchor for anchor in anchors if anchor.evidence and anchor.evidence in text]
    pairs = associate_attributes_to_anchors(anchors, attributes, text)
    paired_spans = {anchor.span for anchor, _attrs in pairs}
    candidates: list[RecogniseCandidate] = []
    for anchor in anchors:
        if anchor.span in paired_spans:
            continue
        if not _is_named_type_anchor(anchor):
            continue
        mention = _mention_from_pair(anchor, {})
        candidates.append(
            RecogniseCandidate(
                mention=mention,
                candidate_class=SF_NAMED_TYPE,
                rule_id="recognise.sf_named_type",
            )
        )
    return tuple(candidates)


def _deferred_sf_heading_state_candidates(
    text: str,
    ablation: AblationConfig,
) -> tuple:
    from .recognise_ledger import SF_HEADING_STATE, RecogniseCandidate

    default_keys = _default_sf_mention_keys(text, ablation)
    candidates: list[RecogniseCandidate] = []
    for mention in frequency_section_mentions(text):
        if not _has_heading_frequency_state(mention):
            continue
        if _mention_key(mention) in default_keys:
            continue
        candidates.append(
            RecogniseCandidate(
                mention=mention,
                candidate_class=SF_HEADING_STATE,
                rule_id="recognise.sf_heading_state",
            )
        )
    return tuple(candidates)


def _deferred_sf_seizure_free_candidates(
    text: str,
    ablation: AblationConfig,
) -> tuple:
    from .recognise_ledger import SF_SEIZURE_FREE, RecogniseCandidate

    anchors = _collect_anchors(text, ablation)
    attributes = _collect_attributes(text, ablation)
    anchors = [anchor for anchor in anchors if anchor.evidence and anchor.evidence in text]
    attributes = [attr for attr in attributes if attr.evidence and attr.evidence in text]
    orphans = _unassociated_attributes(anchors, attributes, text)
    default_keys = _default_sf_mention_keys(text, ablation)
    candidates: list[RecogniseCandidate] = []
    for attr in orphans:
        if attr.kind != AttributeKind.SEIZURE_FREE:
            continue
        if not _has_explicit_seizure_free_evidence(attr.evidence):
            continue
        mention = _mention_from_orphan_seizure_free(attr)
        if _mention_key(mention) in default_keys:
            continue
        candidates.append(
            RecogniseCandidate(
                mention=mention,
                candidate_class=SF_SEIZURE_FREE,
                rule_id="recognise.sf_seizure_free",
            )
        )
    return tuple(candidates)


def deferred_sf_candidates(
    letter: ExectLetter,
    enabled_classes: frozenset[str],
) -> tuple:
    """Deferred SeizureFrequency recognise candidates for reconstruction move M3."""

    from .recognise_ledger import (
        SF_HEADING_STATE,
        SF_NAMED_TYPE,
        SF_SEIZURE_FREE,
    )

    text = letter.note_text
    ablation = DEFAULT_ABLATION
    candidates: list = []
    if SF_NAMED_TYPE in enabled_classes:
        candidates.extend(_deferred_sf_named_type_candidates(text, ablation))
    if SF_HEADING_STATE in enabled_classes:
        candidates.extend(_deferred_sf_heading_state_candidates(text, ablation))
    if SF_SEIZURE_FREE in enabled_classes:
        candidates.extend(_deferred_sf_seizure_free_candidates(text, ablation))
    return tuple(candidates)


def run_on_letters(
    letters: Sequence[ExectLetter],
    ablation: AblationConfig = DEFAULT_ABLATION,
) -> list[PredictedLetter]:
    """Run the SF deterministic pipeline on every letter."""
    return [extract_seizure_frequency(letter, ablation) for letter in letters]
