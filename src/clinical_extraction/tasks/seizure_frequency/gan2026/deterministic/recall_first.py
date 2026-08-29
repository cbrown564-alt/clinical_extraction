"""Phase B recall-first provisional producers for the three-stage rules program.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_protocol_2026-08-29.md
Audit: docs/research/gan2026/gan_rules_taxonomy_audit_2026-08-29.md

Each class is a named ``RuleSpec`` whose candidates enter the find
ledger tagged with the class name and are dropped by the Select gate
(``select.provisional_unsupported_drop``) until Phase C accepts a keep,
so enabling a class cannot change the select stop. Patterns are derived
from permitted `dev750` recall-gap rows; the nine protected benchmark
shorthand rows are deliberately not covered.

History flags carried into Phase C: the nightly narrative rate re-poses
G1 Candidate A (development-positive, holdout −1, killed); the
non-epileptic current class re-poses G2 Candidate B (development +1,
holdout inert). Any Phase C keep for those classes must weigh that
record explicitly.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from .candidates import (
    CandidateKind,
    RawCandidate,
)
from .deterministic_text import (
    clean_evidence,
)
from .rule_metadata import (
    AblationConfig,
    ExtractionContext,
    Portability,
    RuleExample,
    RuleGroup,
    RuleSpec,
    apply_rule,
    validate_rule_registry,
)


def _unknown_candidate(match: re.Match[str], rule_id: str) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.UNKNOWN_FREQUENCY,
        label="unknown",
        evidence=clean_evidence(match.group(0)),
        rule_id=rule_id,
        rule_group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


def _build_trigger_conditioned_unknown(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _unknown_candidate(match, TRIGGER_CONDITIONED_UNKNOWN_RULE.rule_id)


TRIGGER_CONDITIONED_UNKNOWN_RULE = RuleSpec(
    rule_id="provisional.trigger_conditioned_unknown",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "Seizures described only through a trigger condition (alcohol, missed "
        "doses, photosensitivity, exercise, sleep loss, menstrual phase) carry "
        "no countable frequency; propose unknown."
    ),
    pattern=re.compile(
        r"(?:"
        r"\b(?:seizures?|seizure\s+(?:episodes?|events?|exacerbations?))\s+"
        r"(?:only\s+)?(?:with|after|following)\s+"
        r"(?:missed\s+\w+\s+doses|alcohol\s+intake|prolonged\s+screen\s+time|"
        r"sleep\s+deprivation|flicker\s+exposure)"
        r"|\b(?:seizures?|events?|episodes?|spells?)\s+"
        r"(?:are\s+|is\s+)?(?:provoked|precipitated|triggered)\s+by\b"
        r"|\bseizures?\s+occurring\s+exclusively\s+(?:after|with|when)\b"
        r"|\bbreakthrough\s+(?:events?|seizures?)\s+linked\s+to\b"
        r"|\b[a-z]+(?:-and-[a-z]+)*-linked\s+events?\b"
        r"|\b[a-z]+-(?:induced|related|associated)\s+"
        r"(?:seizures?|seizure\s+episodes?|spillover\s+days?)\b"
        r"|\bcatamenial\s+(?:clustering|exacerbations?|seizures?)\b"
        r"|\b(?:spells?|seizures?|events?)\s+are\s+(?:uncommon|rare)\s+when\b"
        r"|\bphotosensitive\s+seizure\s+episodes?\b"
        r"|\bskipping\s+meals\s+triggers\s+seizures?\b"
        r"|\bluteal\s+phase\s+seizure\s+exacerbations?\b"
        r"|\bonly\s+with\s+sleep\s+deprivation\b"
        r")",
        re.IGNORECASE,
    ),
    build=_build_trigger_conditioned_unknown,
    examples=(
        RuleExample(
            text="Seizures after alcohol intake were described by the family.",
            expected_label="unknown",
            expected_evidence="Seizures after alcohol intake",
        ),
        RuleExample(
            text="Exercise-induced seizures remain her main concern.",
            expected_label="unknown",
            expected_evidence="Exercise-induced seizures",
        ),
        RuleExample(
            text="Her seizures are provoked by patterned visual stimuli.",
            expected_label="unknown",
            expected_evidence="seizures are provoked by",
        ),
        RuleExample(
            text="The history is consistent with catamenial clustering.",
            expected_label="unknown",
            expected_evidence="catamenial clustering",
        ),
    ),
    provenance="Phase B recall-first; dev750 recall-gap rows (gold unknown).",
)


def _build_vague_multiple_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    unit = next(
        (
            group.lower()
            for group in (
                match.group("unit1"),
                match.group("unit2"),
                match.group("unit3"),
            )
            if group
        ),
        "",
    )
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label=f"multiple per {unit}",
        evidence=clean_evidence(match.group(0)),
        rule_id=VAGUE_MULTIPLE_RATE_RULE.rule_id,
        rule_group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


VAGUE_MULTIPLE_RATE_RULE = RuleSpec(
    rule_id="provisional.vague_multiple_rate",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "A vague plural count of events in a recent window is a multiple-per-"
        "period statement, not an unknown."
    ),
    pattern=re.compile(
        r"(?:"
        r"\b(?:many|several|numerous|a\s+couple\s+of|a\s+few|a\s+handful\s+of)\s+"
        r"(?:[a-z-]+\s+){0,2}?"
        r"(?:convulsions?|seizures?|absences?|episodes?|events?|turns?|spells?)\s+"
        r"(?:(?:in|during|over)\s+the\s+"
        r"(?:past|previous|preceding|last)\s+(?P<unit1>day|week|month)|"
        r"in\s+past\s+(?P<unit2>day|week|month)|"
        r"last\s+(?P<unit3>day|week|month))"
        r")\b",
        re.IGNORECASE,
    ),
    build=_build_vague_multiple_rate,
    examples=(
        RuleExample(
            text="She reports many convulsions in past month.",
            expected_label="multiple per month",
            expected_evidence="many convulsions in past month",
        ),
        RuleExample(
            text="There were several focal seizures last week.",
            expected_label="multiple per week",
            expected_evidence="several focal seizures last week",
        ),
        RuleExample(
            text="There were a handful of short focal events during the previous month.",
            expected_label="multiple per month",
            expected_evidence="a handful of short focal events during the previous month",
        ),
    ),
    provenance="Phase B recall-first; dev750 recall-gap rows (gold multiple per X).",
)


def _build_electrographic_hourly_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="multiple per day",
        evidence=clean_evidence(match.group(0)),
        rule_id=ELECTROGRAPHIC_HOURLY_RATE_RULE.rule_id,
        rule_group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


ELECTROGRAPHIC_HOURLY_RATE_RULE = RuleSpec(
    rule_id="provisional.electrographic_hourly_rate",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "Frequent electrographic events with an approximate per-hour EEG rate "
        "occur many times per day."
    ),
    pattern=re.compile(
        r"\belectrographic\s+.{0,30}?frequent\s+on\s+EEG\s*"
        r"\(\s*~?\s*(?P<per_hour>\d+|[a-z]+)\s*/\s*h\s*\)",
        re.IGNORECASE,
    ),
    build=_build_electrographic_hourly_rate,
    examples=(
        RuleExample(
            text="Electrographic seizures frequent on EEG (~9/h) overnight.",
            expected_label="multiple per day",
            expected_evidence="Electrographic seizures frequent on EEG (~9/h)",
        ),
    ),
    provenance="Phase B recall-first; dev750 recall-gap rows (gold multiple per day).",
)


def _build_nightly_narrative_rate(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.FREQUENCY_RATE,
        label="1 per day",
        evidence=clean_evidence(match.group(0)),
        rule_id=NIGHTLY_NARRATIVE_RATE_RULE.rule_id,
        rule_group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


NIGHTLY_NARRATIVE_RATE_RULE = RuleSpec(
    rule_id="provisional.nightly_narrative_rate",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "An ongoing nightly generalised seizure pattern stated in narrative "
        "form is a daily rate. Re-poses killed G1 Candidate A; Phase C must "
        "weigh that holdout record before any keep."
    ),
    pattern=re.compile(
        r"\b(?:continues\s+to\s+have\s+)?nightly\s+generalised\s+"
        r"(?:tonic-clonic|convulsions?)\s+seizures\b",
        re.IGNORECASE,
    ),
    build=_build_nightly_narrative_rate,
    examples=(
        RuleExample(
            text="She continues to have nightly generalised tonic-clonic seizures.",
            expected_label="1 per day",
            expected_evidence=(
                "continues to have nightly generalised tonic-clonic seizures"
            ),
        ),
    ),
    provenance="Phase B recall-first; dev750 recall-gap rows; G1 history flagged.",
)


def _build_non_epileptic_current_free(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.SEIZURE_FREE,
        label="seizure free for multiple month",
        evidence=clean_evidence(match.group(0)),
        rule_id=NON_EPILEPTIC_CURRENT_FREE_RULE.rule_id,
        rule_group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
        portability=Portability.GAN2026_SPECIFIC,
        match_groups=match.groupdict(),
    )


NON_EPILEPTIC_CURRENT_FREE_RULE = RuleSpec(
    rule_id="provisional.non_epileptic_current_free",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.GAN2026_SPECIFIC,
    description=(
        "Current events judged non-epileptic mean no current epileptic "
        "seizures under the benchmark's gold policy. Re-poses G2 Candidate B "
        "(development +1, holdout inert)."
    ),
    pattern=re.compile(
        r"\b(?:events\s+at\s+present\s+are\s+considered\s+non-epileptic|"
        r"(?:seizure-like\s+)?episodes\s+are\s+currently\s+non-epileptic)\b",
        re.IGNORECASE,
    ),
    build=_build_non_epileptic_current_free,
    examples=(
        RuleExample(
            text="Events at present are considered non-epileptic and manageable.",
            expected_label="seizure free for multiple month",
            expected_evidence="Events at present are considered non-epileptic",
        ),
    ),
    provenance="Phase B recall-first; dev750 recall-gap rows; G2 history flagged.",
)


def _build_monthly_cluster_unclear_count(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return RawCandidate(
        kind=CandidateKind.CLUSTER_FREQUENCY,
        label="1 cluster per month, multiple per cluster",
        evidence=clean_evidence(match.group(0)),
        rule_id=MONTHLY_CLUSTER_UNCLEAR_COUNT_RULE.rule_id,
        rule_group=RuleGroup.CLUSTER_ARITHMETIC,
        portability=Portability.SEIZURE_FREQUENCY,
        match_groups=match.groupdict(),
    )


MONTHLY_CLUSTER_UNCLEAR_COUNT_RULE = RuleSpec(
    rule_id="provisional.monthly_cluster_unclear_count",
    group=RuleGroup.CLUSTER_ARITHMETIC,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "Monthly clusters with no per-cluster count are one cluster per month "
        "with an unresolved multiple per cluster."
    ),
    pattern=re.compile(
        r"(?:"
        r"\bmonthly\s+clusters\b"
        r"|\b(?:gather\s+into\s+)?(?:brief\s+|short\s+)?"
        r"(?:bursts?|runs?\s+of\s+events?)\s+"
        r"(?:occurring\s+)?(?:roughly|approximately|about)?\s*"
        r"(?:once\s+(?:a|each|per)\s+month|monthly)\b"
        r")",
        re.IGNORECASE,
    ),
    build=_build_monthly_cluster_unclear_count,
    examples=(
        RuleExample(
            text="Monthly clusters; within-cluster count unclear.",
            expected_label="1 cluster per month, multiple per cluster",
            expected_evidence="Monthly clusters",
        ),
        RuleExample(
            text="His events tend to gather into bursts roughly once each month.",
            expected_label="1 cluster per month, multiple per cluster",
            expected_evidence="gather into bursts roughly once each month",
        ),
    ),
    provenance="Phase B recall-first; dev750 recall-gap rows.",
)


def _build_single_dated_event_unknown(
    match: re.Match[str], _context: ExtractionContext
) -> RawCandidate:
    return _unknown_candidate(match, SINGLE_DATED_EVENT_UNKNOWN_RULE.rule_id)


SINGLE_DATED_EVENT_UNKNOWN_RULE = RuleSpec(
    rule_id="provisional.single_dated_event_unknown",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description=(
        "A single dated seizure report without a rate cannot be converted to "
        "a frequency; propose unknown."
    ),
    pattern=re.compile(
        r"\breported\s+(?:having\s+)?a\s+seizure\s+on\s+"
        r"\d{1,2}\s*[-/]\s*[A-Za-z]{3}\b",
        re.IGNORECASE,
    ),
    build=_build_single_dated_event_unknown,
    examples=(
        RuleExample(
            text="The patient reported a seizure on 22/Aug at work.",
            expected_label="unknown",
            expected_evidence="reported a seizure on 22/Aug",
        ),
    ),
    provenance="Phase B recall-first; dev750 recall-gap rows (gold unknown).",
)


PROVISIONAL_RULES: tuple[RuleSpec, ...] = (
    TRIGGER_CONDITIONED_UNKNOWN_RULE,
    VAGUE_MULTIPLE_RATE_RULE,
    ELECTROGRAPHIC_HOURLY_RATE_RULE,
    NIGHTLY_NARRATIVE_RATE_RULE,
    NON_EPILEPTIC_CURRENT_FREE_RULE,
    MONTHLY_CLUSTER_UNCLEAR_COUNT_RULE,
    SINGLE_DATED_EVENT_UNKNOWN_RULE,
)
validate_rule_registry(PROVISIONAL_RULES)

PROVISIONAL_RULES_BY_CLASS: Mapping[str, RuleSpec] = {
    spec.rule_id: spec for spec in PROVISIONAL_RULES
}
ALL_PROVISIONAL_CLASSES: frozenset[str] = frozenset(PROVISIONAL_RULES_BY_CLASS)


def apply_provisional_producers(
    normalized_text: str,
    enabled_classes: frozenset[str],
    ablation_config: AblationConfig,
) -> list[tuple[str, RawCandidate]]:
    """Apply enabled provisional classes; return (class, candidate) pairs."""

    unknown = enabled_classes - ALL_PROVISIONAL_CLASSES
    if unknown:
        raise ValueError(f"unknown provisional classes: {sorted(unknown)}")
    context = ExtractionContext(text=normalized_text)
    produced: list[tuple[str, RawCandidate]] = []
    for class_name in sorted(enabled_classes):
        spec = PROVISIONAL_RULES_BY_CLASS[class_name]
        for candidate in apply_rule(spec, context, ablation_config):
            if isinstance(candidate, RawCandidate):
                produced.append((class_name, candidate))
    return produced
