"""Hand-curated few-shot demos for the SF verify program (Phase 5 H-examples).

These teach the four benchmark conventions the SF verify error analysis
(``docs/experiments/exectv2/seizure_frequency/exectv2_sf_verify_error_analysis_2026-06-29.md``)
found the model's consolidation instinct overrides — the exact error classes the
redesigned per-(type, state) feedback names:

* **A. per-type multiplicity** — a numeric rate AND a separately-stated qualitative
  change for the SAME seizure type are TWO facts (a ``frequency_rate`` event AND a
  ``changed`` event), not one.
* **A (FP). FrequencyChange=Same is not a fact** — a stability statement ("best it's
  ever been", "unchanged") is NOT a ``changed`` event when a rate is already present.
* **B. confirmed-diagnosis gate** — suspected / dissociative / non-epileptic events do
  not get a seizure-frequency fact.
* **C. historical rate vs current seizure-free** — a dated past seizure count is an
  ``active_rate``; do not replace it with ``seizure_free`` because the patient is
  "currently seizure free".

They are illustrative excerpts (not verbatim dev letters) so they teach the convention
rather than memorise an eval letter. They are attached to BOTH stages: the generate
demos show the correct extraction directly; the verify demos show the recall-additive
CORRECTION (add the missed change, drop the spurious change / non-epileptic event, repair
the historical rate). GEPA preserves seed demos through ``build_program`` (deepcopy +
instruction-only mutation), so these survive optimization and the final eval.
"""

from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_sf_verify import (
    EVENT_SCHEMA_JSON,
)


def _events(*events: dict) -> str:
    return json.dumps({"events": list(events)}, ensure_ascii=False)


# (excerpt, correct events, wrong consolidated/over-emitted draft) per convention.
_CASES: list[tuple[str, str, str]] = [
    # A — per-type multiplicity: rate AND a separate qualitative change = two facts.
    (
        "His epilepsy was well controlled until December, when it worsened. His focal "
        "seizures now occur 2 to 3 times per month.",
        _events(
            {
                "applies_to": "focal seizures",
                "kind": "frequency_rate",
                "evidence": "2 to 3 times per month",
            },
            {"applies_to": "focal seizures", "kind": "changed", "evidence": "worsened"},
        ),
        # Draft consolidated to the rate only and missed the change.
        _events(
            {
                "applies_to": "focal seizures",
                "kind": "frequency_rate",
                "evidence": "2 to 3 times per month",
            },
        ),
    ),
    # A (FP) — a stability statement is not a SEPARATE changed fact alongside a rate.
    (
        "Her epilepsy is the best it has ever been. She continues to have seizures every "
        "3 to 4 weeks.",
        _events(
            {"applies_to": "seizures", "kind": "frequency_rate", "evidence": "every 3 to 4 weeks"},
        ),
        # Draft read the stability statement as a change on top of the rate.
        _events(
            {"applies_to": "seizures", "kind": "frequency_rate", "evidence": "every 3 to 4 weeks"},
            {"applies_to": "seizures", "kind": "changed", "evidence": "best it has ever been"},
        ),
    ),
    # B — confirmed-diagnosis gate: non-epileptic / unconfirmed events get no SF fact.
    (
        "There is no confirmed diagnosis of epilepsy; these episodes are likely "
        "dissociative (non-epileptic). She reports events around twice a week.",
        _events(),
        # Draft over-emitted on the non-epileptic events.
        _events(
            {
                "applies_to": "dissociative events",
                "kind": "frequency_rate",
                "evidence": "events around twice a week",
            },
        ),
    ),
    # C — a dated past count is an active_rate, not the current seizure-free status.
    (
        "He had 2 generalised tonic-clonic seizures in 2014. He remains seizure free currently.",
        _events(
            {
                "applies_to": "generalised tonic-clonic seizures",
                "kind": "frequency_rate",
                "evidence": "2 generalised tonic-clonic seizures in 2014",
            },
        ),
        # Draft replaced the historical rate with current seizure-free.
        _events(
            {"applies_to": "seizures", "kind": "seizure_free", "evidence": "remains seizure free"},
        ),
    ),
]


def build_generate_demos() -> list[dspy.Example]:
    """Demos for the generate stage: letter excerpt -> correct events_json."""

    return [
        dspy.Example(
            letter_text=excerpt,
            output_schema=EVENT_SCHEMA_JSON,
            events_json=correct,
        )
        for excerpt, correct, _draft in _CASES
    ]


def build_verify_demos() -> list[dspy.Example]:
    """Demos for the verify stage: excerpt + flawed draft -> corrected events_json."""

    return [
        dspy.Example(
            letter_text=excerpt,
            draft_events_json=draft,
            output_schema=EVENT_SCHEMA_JSON,
            events_json=correct,
        )
        for excerpt, correct, draft in _CASES
    ]


def build_sf_verify_demos() -> tuple[list[dspy.Example], list[dspy.Example]]:
    """(generate_demos, verify_demos) — the full hand-curated H-examples set."""

    return build_generate_demos(), build_verify_demos()
