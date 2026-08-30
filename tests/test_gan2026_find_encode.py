"""Same-fact encode registry for the Gan rules-only find ledger.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_phase_e_protocol_2026-08-30.md
"""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.candidates import (
    CandidateKind,
    RawCandidate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.find_dialects import (
    FIND_DIALECT_GAN_LLM_EXTRACT,
    FIND_DIALECT_GAN_LLM_EXTRACT_RAW,
    project_find_event,
    render_find_fact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.find_encode import (
    FindFact,
    encode_find_fact,
    find_tag,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    ExtractionContext,
    RuleSpec,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.cluster import (
    CLUSTER_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.diary import (
    DIARY_DATE_LIST_RULE,
    SEIZURE_DAYS_FRACTION_RULE,
    SEIZURE_DAYS_PER_PERIOD_RULE,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules.gan_shorthand import (
    GAN_SHORTHAND_RULES,
)


def test_rate_find_tag_keeps_raw_slots() -> None:
    fact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="four",
        unit="day",
    )
    assert find_tag(fact) == "four/day"
    assert encode_find_fact(fact) == "4 per day"


def test_rate_find_tag_keeps_raw_denominator() -> None:
    fact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="1",
        unit="months",
        denominator="8",
    )
    assert find_tag(fact) == "1/8 months"
    assert encode_find_fact(fact) == "1 per 8 month"


def test_cluster_find_tag_keeps_raw_slots() -> None:
    fact = FindFact(
        kind=CandidateKind.CLUSTER_FREQUENCY,
        cluster_count="two",
        unit="weeks",
        cluster_size="three",
    )
    assert find_tag(fact) == "cluster:two/weeks:three"
    assert encode_find_fact(fact) == "2 cluster per week, 3 per cluster"


def test_unknown_cluster_size_encodes_codebook_form() -> None:
    fact = FindFact(
        kind=CandidateKind.UNKNOWN_FREQUENCY,
        sentinel="unknown",
        cluster_size="four",
    )
    assert find_tag(fact) == "unknown"
    assert encode_find_fact(fact) == "unknown, 4 per cluster"


def test_shorthand_compact_unit_encodes_to_codebook() -> None:
    fact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="5",
        unit="mo",
    )
    assert find_tag(fact) == "5/mo"
    assert encode_find_fact(fact) == "5 per month"


def test_adjective_rate_unit_encodes_to_codebook() -> None:
    fact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="1",
        unit="daily",
    )
    assert find_tag(fact) == "1/daily"
    assert encode_find_fact(fact) == "1 per day"


def test_seizure_free_find_tag_is_state() -> None:
    fact = FindFact(
        kind=CandidateKind.SEIZURE_FREE,
        custom_label="seizure free for 2 year",
    )
    assert find_tag(fact) == "seizure_free"
    assert encode_find_fact(fact) == "seizure free for 2 year"


def _assert_example_slots(spec: RuleSpec) -> None:
    config = AblationConfig()
    checked = 0
    for example in spec.examples:
        if example.anti_example or example.expected_label is None:
            continue
        built = [
            candidate
            for candidate in spec.apply(ExtractionContext(text=example.text), config)
            if isinstance(candidate, RawCandidate)
        ]
        if not built:
            continue
        assert built[0].label == example.expected_label, spec.rule_id
        assert built[0].find_fact is not None
        assert built[0].find_fact.custom_label is None
        checked += 1
    assert checked > 0, spec.rule_id


def test_cluster_examples_use_slot_encode() -> None:
    for spec in CLUSTER_RULES:
        if spec.rule_id == "cluster.last_convulsive_persistence":
            continue
        _assert_example_slots(spec)


def test_codebook_dialect_matches_encode_find_fact() -> None:
    fact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="four",
        unit="day",
    )
    assert render_find_fact(fact, FIND_DIALECT_GAN_LLM_EXTRACT) == "4 per day"
    assert render_find_fact(fact, FIND_DIALECT_GAN_LLM_EXTRACT) == encode_find_fact(
        fact
    )


def test_source_near_dialect_keeps_found_tokens() -> None:
    rate = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="four",
        unit="day",
    )
    compact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="5",
        unit="mo",
    )
    adjective = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="1",
        unit="daily",
    )
    cluster = FindFact(
        kind=CandidateKind.CLUSTER_FREQUENCY,
        cluster_count="two",
        unit="weeks",
        cluster_size="three",
    )
    assert render_find_fact(rate, FIND_DIALECT_GAN_LLM_EXTRACT_RAW) == "four per day"
    assert render_find_fact(compact, FIND_DIALECT_GAN_LLM_EXTRACT_RAW) == "5 per mo"
    assert render_find_fact(adjective, FIND_DIALECT_GAN_LLM_EXTRACT_RAW) == "daily"
    assert (
        render_find_fact(cluster, FIND_DIALECT_GAN_LLM_EXTRACT_RAW)
        == "two cluster per weeks, three per cluster"
    )
    assert render_find_fact(rate, FIND_DIALECT_GAN_LLM_EXTRACT_RAW) != encode_find_fact(
        rate
    )


def test_project_find_event_maps_llm_extract_schema() -> None:
    fact = FindFact(
        kind=CandidateKind.FREQUENCY_RATE,
        count="four",
        unit="day",
    )
    codebook = project_find_event(
        fact,
        FIND_DIALECT_GAN_LLM_EXTRACT,
        evidence="four times per day",
    )
    source_near = project_find_event(
        fact,
        FIND_DIALECT_GAN_LLM_EXTRACT_RAW,
        evidence="four times per day",
    )
    assert codebook["kind"] == "frequency_rate"
    assert codebook["raw_value"] == "four times per day"
    assert codebook["final_label"] == "4 per day"
    assert source_near["raw_value"] == "four times per day"
    assert source_near["final_label"] == "four per day"


def test_diary_and_shorthand_examples_use_slot_encode() -> None:
    for spec in (
        SEIZURE_DAYS_PER_PERIOD_RULE,
        SEIZURE_DAYS_FRACTION_RULE,
        DIARY_DATE_LIST_RULE,
        *GAN_SHORTHAND_RULES,
    ):
        _assert_example_slots(spec)
