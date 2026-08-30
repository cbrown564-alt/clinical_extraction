"""Phase A three-stage instrumentation for the Gan rules-only program.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md

Score-neutral by construction: the find ledger reuses the same rule
families as the living ``run_record``, the relocated drops reuse the same
pruning functions on the same input, and the competition pool is rebuilt
exactly as ``extract_stage`` builds it. The select stop must therefore be
label- and evidence-identical to the comparator (gate A1); the dev750
measurement script verifies that on every record before reading stops.

Stage stops follow the Phase E policy: the find stop is the pre-codebook
``find_tag`` of the first wide-ledger candidate in document order
(including Select-dropped rows). ``find_extract_label`` and
``find_extract_raw_label`` re-render that same pick in the
``gan_llm_extract`` and ``gan_llm_extract_raw`` dialects. The encode
stop is the normalized codebook label of that pick, and the select
stop is the submitted final label.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    DeferredDrop,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_candidate_pruning import (  # noqa: E501
    _is_contained_monthly_list_fragment,
    prune_contained_frequency_fragments,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_extraction import (  # noqa: E501
    extract_wide_candidates,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_selection import (  # noqa: E501
    FinalSelection,
    select_final_event,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.deterministic_text import (
    normalize_note_text,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.find_dialects import (
    FIND_DIALECT_GAN_LLM_EXTRACT,
    FIND_DIALECT_GAN_LLM_EXTRACT_RAW,
    render_find_fact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.find_encode import (
    FindFact,
    find_tag,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.recall_first import (
    ALL_PROVISIONAL_CLASSES,
    apply_provisional_producers,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    RuleSpec,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    cluster as cluster_rules_module,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    diary as diary_rules_module,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    gan_shorthand as gan_shorthand_rules_module,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    rate as rate_rules_module,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    seizure_free as seizure_free_rules_module,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    _candidate_event,
    _fallback_evidence,
    _normalize_candidate,
)

NO_REFERENCE_LABEL = "no seizure frequency reference"
FALLBACK_RULE_ID = "fallback.no_reference"

_RULE_MODULES = (
    cluster_rules_module,
    diary_rules_module,
    gan_shorthand_rules_module,
    rate_rules_module,
    seizure_free_rules_module,
)


class LedgerDropReason(StrEnum):
    """Relocated select-stage drops; find keeps the candidate visible."""

    DUPLICATE = "select.duplicate_drop"
    CONTAINED_FRAGMENT = "select.contained_fragment_drop"
    HISTORICAL_RATE = "select.historical_rate_drop"
    # Phase B recall-first gate: every provisional candidate is dropped
    # here until Phase C accepts a keep, so enabling a provisional class
    # cannot change the select stop.
    PROVISIONAL_UNSUPPORTED = "select.provisional_unsupported_drop"
    RULE_EXCLUDE = DeferredDrop.RULE_EXCLUDE
    MEDICATION_DOSE_DISTRACTOR = DeferredDrop.MEDICATION_DOSE_DISTRACTOR
    HISTORICAL_LEAD_IN = DeferredDrop.HISTORICAL_LEAD_IN


class ExclusionRecord(BaseModel):
    """A rule-`exclude` suppression: recorded span, never built or competed."""

    model_config = ConfigDict(frozen=True)

    rule_id: str
    start_char: int
    end_char: int
    matched_text: str


class LedgerEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    ledger_index: int
    kind: CandidateKind
    raw_label: str | None
    find_tag: str
    find_extract_label: str
    find_extract_raw_label: str
    normalized_label: str
    evidence: str
    start_char: int | None
    end_char: int | None
    rule_id: str
    drop_reason: LedgerDropReason | None = None
    is_fallback: bool = False
    provisional_class: str | None = None


class GanStageStops(BaseModel):
    model_config = ConfigDict(frozen=True)

    find_label: str | None
    find_extract_label: str
    find_extract_raw_label: str
    encode_label: str
    select_label: str
    find_pick_ledger_index: int | None


@dataclass(frozen=True)
class GanThreeStageConfig:
    ablation_config: AblationConfig = field(default_factory=AblationConfig)
    # Enabled recall-first provisional producer classes (Phase B). Their
    # candidates join the find ledger and stop diagnostics but are
    # dropped by the Select gate before competition.
    provisional_classes: frozenset[str] = frozenset()
    # Phase C keeps: classes whose candidates pass the Select gate and
    # compete through the existing priority ladder. Kept candidates are
    # appended after the surviving wide-pool candidates, so on priority
    # ties the incumbent wins. Keeping a class implies producing it.
    kept_classes: frozenset[str] = frozenset()
    # Phase C override rules: named, ordered pre-ladder select rules.
    # An override that applies restricts the competition to its kept
    # candidate. Only listed rules run; each requires its class kept.
    select_overrides: frozenset[str] = frozenset()


@dataclass(frozen=True)
class GanThreeStageResult:
    ledger: tuple[LedgerEntry, ...]
    exclusions: tuple[ExclusionRecord, ...]
    final_selection: FinalSelection
    stops: GanStageStops


def tag_ledger_drops(
    candidates: Sequence[RawCandidate], normalized_text: str
) -> tuple[tuple[RawCandidate, ...], dict[int, LedgerDropReason]]:
    """Relocate the extract-time drops to tagged select decisions.

    Returns the surviving competition pool (exactly
    ``prune_contained_frequency_fragments(dedupe_candidates(candidates))``,
    reusing those functions) and a wide-ledger-index -> reason map for the
    dropped candidates. Duplicate detection is positional because the same
    (kind, label, evidence) key keeps only its first occurrence.
    """
    reasons: dict[int, LedgerDropReason] = {}
    deduped: list[RawCandidate] = []
    seen_keys: set[tuple[CandidateKind, str | None, str]] = set()
    deduped_wide_index: dict[int, int] = {}
    for index, candidate in enumerate(candidates):
        if candidate.deferred_drop:
            reasons[index] = LedgerDropReason(candidate.deferred_drop)
            continue
        key = (candidate.kind, candidate.label, candidate.evidence)
        if key in seen_keys:
            reasons[index] = LedgerDropReason.DUPLICATE
            continue
        seen_keys.add(key)
        deduped_wide_index[len(deduped)] = index
        deduped.append(candidate)

    pool = prune_contained_frequency_fragments(deduped, normalized_text)
    pool_ids = {id(candidate) for candidate in pool}
    for deduped_index, candidate in enumerate(deduped):
        if id(candidate) in pool_ids:
            continue
        wide_index = deduped_wide_index[deduped_index]
        # Mirror the prune branch order: the contained-fragment check runs
        # before the historical check and applies to FREQUENCY_RATE only.
        if candidate.kind is CandidateKind.FREQUENCY_RATE and any(
            _is_contained_monthly_list_fragment(candidate, other) for other in deduped
        ):
            reasons[wide_index] = LedgerDropReason.CONTAINED_FRAGMENT
        else:
            reasons[wide_index] = LedgerDropReason.HISTORICAL_RATE
    return tuple(pool), reasons


def _rule_specs_with_exclusions() -> tuple[RuleSpec, ...]:
    specs: dict[str, RuleSpec] = {}
    for module in _RULE_MODULES:
        for value in vars(module).values():
            if isinstance(value, RuleSpec) and value.exclude:
                specs[value.rule_id] = value
    return tuple(specs[rule_id] for rule_id in sorted(specs))


def collect_exclusion_records(
    normalized_text: str,
    ablation_config: AblationConfig,
    *,
    specs: Sequence[RuleSpec] | None = None,
) -> tuple[ExclusionRecord, ...]:
    """Record spans that a rule matched but its exclude predicate suppressed.

    This is a parallel scan over the declared ``RuleSpec.exclude`` sites; it
    never calls ``build`` and cannot change extraction behavior.
    """
    scan_specs = tuple(specs) if specs is not None else _rule_specs_with_exclusions()
    context = ExtractionContext(text=normalized_text)
    records: list[ExclusionRecord] = []
    for spec in scan_specs:
        if not ablation_config.rule_is_enabled(
            rule_id=spec.rule_id,
            group=spec.group,
            portability=spec.portability,
        ):
            continue
        for match in spec.pattern.finditer(normalized_text):
            if any(exclude(match, context) for exclude in spec.exclude):
                records.append(
                    ExclusionRecord(
                        rule_id=spec.rule_id,
                        start_char=match.start(),
                        end_char=match.end(),
                        matched_text=match.group(0),
                    )
                )
    return tuple(records)


def _ledger_entry(
    index: int,
    candidate: RawCandidate,
    note_text: str,
    ablation_config: AblationConfig,
    *,
    drop_reason: LedgerDropReason | None,
    is_fallback: bool = False,
    provisional_class: str | None = None,
) -> LedgerEntry:
    event = _candidate_event(index=index + 1, candidate=candidate, note_text=note_text)
    normalized = _normalize_candidate(event, candidate, ablation_config)
    fact = candidate.find_fact
    if fact is None and candidate.label is not None:
        fact = FindFact(kind=candidate.kind, custom_label=candidate.label)
    tag = find_tag(fact) if fact is not None else (candidate.label or NO_REFERENCE_LABEL)
    extract_label = (
        render_find_fact(fact, FIND_DIALECT_GAN_LLM_EXTRACT)
        if fact is not None
        else (candidate.label or NO_REFERENCE_LABEL)
    )
    extract_raw_label = (
        render_find_fact(fact, FIND_DIALECT_GAN_LLM_EXTRACT_RAW)
        if fact is not None
        else (candidate.label or NO_REFERENCE_LABEL)
    )
    return LedgerEntry(
        ledger_index=index,
        kind=candidate.kind,
        raw_label=candidate.label,
        find_tag=tag,
        find_extract_label=extract_label,
        find_extract_raw_label=extract_raw_label,
        normalized_label=normalized.normalized_label,
        evidence=event.evidence,
        start_char=event.start_char,
        end_char=event.end_char,
        rule_id=candidate.rule_id,
        drop_reason=drop_reason,
        is_fallback=is_fallback,
        provisional_class=provisional_class,
    )


EXCLUSIVE_TRIGGER_OVERRIDE = "select.override.exclusive_trigger_conditioned_unknown"
SINGLE_DATED_EVENT_OVERRIDE = "select.override.single_dated_event_unknown"


def phase_c_candidate_config() -> GanThreeStageConfig:
    """Promoted Phase C candidate (2026-08-29).

    Phase D aggregate-only test450 select 325/450 versus cited 321/450.
    Living five-cell rules row and ``gan_cell_replay`` rules_only use this
    config. See
    docs/research/gan2026/gan_rules_only_three_stage_phase_d_2026-08-29.md.
    """

    return GanThreeStageConfig(
        provisional_classes=ALL_PROVISIONAL_CLASSES,
        kept_classes=ALL_PROVISIONAL_CLASSES,
        select_overrides=frozenset(
            {EXCLUSIVE_TRIGGER_OVERRIDE, SINGLE_DATED_EVENT_OVERRIDE}
        ),
    )

_EXCLUSIVITY_MARKERS = re.compile(
    r"\b(?:exclusively|only)\b|\b(?:uncommon|rare)\s+when\b", re.IGNORECASE
)

# Ordered pre-ladder Select sequence: (override name, provisional class,
# evidence gate). The first override whose kept candidate passes its gate
# restricts the competition to that candidate.
_SELECT_OVERRIDES: tuple[tuple[str, str, re.Pattern[str] | None], ...] = (
    (
        EXCLUSIVE_TRIGGER_OVERRIDE,
        "provisional.trigger_conditioned_unknown",
        _EXCLUSIVITY_MARKERS,
    ),
    (
        SINGLE_DATED_EVENT_OVERRIDE,
        "provisional.single_dated_event_unknown",
        None,
    ),
)
KNOWN_SELECT_OVERRIDES: frozenset[str] = frozenset(
    name for name, _class, _gate in _SELECT_OVERRIDES
)


def _apply_select_overrides(
    overrides: frozenset[str],
    kept_by_class: dict[str, list[RawCandidate]],
) -> RawCandidate | None:
    """Return the candidate an enabled override selects, if any.

    Gates read only the candidate's own evidence span, so an override
    cannot fire off unrelated nearby wording.
    """

    for name, class_name, gate in _SELECT_OVERRIDES:
        if name not in overrides:
            continue
        for candidate in kept_by_class.get(class_name, []):
            if gate is None or gate.search(candidate.evidence):
                return candidate
    return None


def _document_order_pick(ledger: Sequence[LedgerEntry]) -> LedgerEntry | None:
    competing = [entry for entry in ledger if not entry.is_fallback]
    if not competing:
        return None
    return min(
        competing,
        key=lambda entry: (
            entry.start_char is None,
            entry.start_char if entry.start_char is not None else 0,
            entry.ledger_index,
        ),
    )


def run_record_three_stage(
    item: GanRecord, config: GanThreeStageConfig | None = None
) -> GanThreeStageResult:
    """Run one Gan record through find, encode, and select stops."""

    resolved = config or GanThreeStageConfig()
    unknown_overrides = resolved.select_overrides - KNOWN_SELECT_OVERRIDES
    if unknown_overrides:
        raise ValueError(f"unknown select overrides: {sorted(unknown_overrides)}")
    ablation_config = resolved.ablation_config
    normalized_text = normalize_note_text(item.note_text)

    wide = extract_wide_candidates(item.note_text, ablation_config)
    exclusions = collect_exclusion_records(normalized_text, ablation_config)
    survivors, drop_reasons = tag_ledger_drops(wide, normalized_text)

    enabled_classes = resolved.provisional_classes | resolved.kept_classes
    produced: list[tuple[str, RawCandidate]] = []
    if enabled_classes:
        produced = apply_provisional_producers(
            normalized_text, enabled_classes, ablation_config
        )
    kept = tuple(
        candidate
        for class_name, candidate in produced
        if class_name in resolved.kept_classes
    )

    pool: tuple[RawCandidate, ...] = survivors + kept
    fallback: RawCandidate | None = None
    if not pool:
        fallback = RawCandidate(
            kind=CandidateKind.NO_REFERENCE,
            label=NO_REFERENCE_LABEL,
            evidence=_fallback_evidence(item.note_text),
            rule_id=FALLBACK_RULE_ID,
        )
        pool = (fallback,)

    if resolved.select_overrides:
        kept_by_class: dict[str, list[RawCandidate]] = {}
        for class_name, candidate in produced:
            if class_name in resolved.kept_classes:
                kept_by_class.setdefault(class_name, []).append(candidate)
        override_winner = _apply_select_overrides(
            resolved.select_overrides, kept_by_class
        )
        if override_winner is not None:
            pool = (override_winner,)

    pool_events = tuple(
        _candidate_event(index=index, candidate=candidate, note_text=item.note_text)
        for index, candidate in enumerate(pool, start=1)
    )
    pool_normalized = tuple(
        _normalize_candidate(event, candidate, ablation_config)
        for event, candidate in zip(pool_events, pool, strict=True)
    )
    final_selection = select_final_event(pool_events, pool_normalized, ablation_config)

    ledger = [
        _ledger_entry(
            index,
            candidate,
            item.note_text,
            ablation_config,
            drop_reason=drop_reasons.get(index),
        )
        for index, candidate in enumerate(wide)
    ]
    if fallback is not None:
        ledger.append(
            _ledger_entry(
                len(wide),
                fallback,
                item.note_text,
                ablation_config,
                drop_reason=None,
                is_fallback=True,
            )
        )

    for class_name, candidate in produced:
        is_kept = class_name in resolved.kept_classes
        ledger.append(
            _ledger_entry(
                len(ledger),
                candidate,
                item.note_text,
                ablation_config,
                drop_reason=(
                    None
                    if is_kept
                    else LedgerDropReason.PROVISIONAL_UNSUPPORTED
                ),
                provisional_class=class_name,
            )
        )

    pick = _document_order_pick(ledger)
    stops = GanStageStops(
        find_label=pick.find_tag if pick is not None else NO_REFERENCE_LABEL,
        find_extract_label=(
            pick.find_extract_label if pick is not None else NO_REFERENCE_LABEL
        ),
        find_extract_raw_label=(
            pick.find_extract_raw_label if pick is not None else NO_REFERENCE_LABEL
        ),
        encode_label=(
            pick.normalized_label if pick is not None else NO_REFERENCE_LABEL
        ),
        select_label=final_selection.final_label,
        find_pick_ledger_index=pick.ledger_index if pick is not None else None,
    )
    return GanThreeStageResult(
        ledger=tuple(ledger),
        exclusions=exclusions,
        final_selection=final_selection,
        stops=stops,
    )
