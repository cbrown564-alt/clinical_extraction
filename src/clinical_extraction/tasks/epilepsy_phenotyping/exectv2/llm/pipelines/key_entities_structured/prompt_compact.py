"""Compact-ledger structured prompt.

Ordinary-language one-call request. No examples. No research metadata.
``exectv2_compact_ledger`` and ``exect_llm_with_rules`` emit this payload.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .prompt_content import (
    _attribute_vocabulary,
    _event_lane_guide,
    candidate_evidence_ledger_for_letter,
)
from .prompt_plain_language import (
    _clean_categories,
    _clean_ledger_row,
    _clean_rule_text,
)
from .prompt_rules_full import (
    _clinical_rules,
)

COMPACT_AUTHORED_KEYS = (
    "task",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "categories",
    "clinical_rules",
    "suggested_evidence",
    "letter_text",
)

_TASK = (
    "Read the clinical letter once. Use the suggested evidence as a starting "
    "point, then list the medication, diagnosis, seizure-frequency, and "
    "investigation facts the letter states. If one fact belongs to more than "
    "one of those families, include each valid family separately."
)

_DECISION_PROCEDURE = [
    (
        "Scan the whole letter for medication, diagnosis, seizure frequency, "
        "and investigations. Do not stop at section headers."
    ),
    (
        "Treat suggested-evidence rows as likely supporting sentences, but do "
        "not include a fact unless the full sentence supports that family."
    ),
    "For each suggested row, choose a category, then keep, reject, split, or merge.",
    (
        "Write the listed items only after the state is clear from the letter. "
        "Counts, dates, result status, dose, and certainty belong in "
        "attributes, not in made-up wording."
    ),
    (
        "Before returning JSON, remove duplicates and remove events whose "
        "evidence or mention text is not an exact copy from the letter."
    ),
]

_FAMILY_GUIDANCE = {
    "medication": (
        "Anti-seizure medicines. Include Prescription items with DrugName, "
        "DrugDose, DoseUnit, and Frequency when stated. Copy the medication "
        "wording from the letter: the full short regimen when it appears in a "
        "list, or the drug name alone when that is all the note states."
    ),
    "diagnosis": (
        "Diagnoses such as epilepsy, focal epilepsy, seizure disorder, or "
        "named seizure types. Include Diagnosis items with DiagCategory, "
        "Certainty, and Negation. Keep uncertainty words out of the diagnosis "
        "wording and put them in Certainty. Do not include vague symptoms or "
        "non-epileptic alternatives unless the letter states they are epileptic "
        "diagnoses, even when they appear under a Diagnosis or problem-list "
        "heading."
    ),
    "seizure_frequency": (
        "How often a seizure type occurs, including seizure-free duration, "
        "ranges, interval rates, cluster counts, dated counts, and frequency "
        "change. Keep the stated seizure words and time period; do not turn "
        "them into a guessed rate. Exclude non-epileptic events and blackouts "
        "unless the letter states they are epileptic seizures."
    ),
    "investigation": (
        "EEG, MRI, CT, telemetry, and related test statements. Include "
        "Investigations with performed, result, and type attributes only for "
        "completed tests or tests with a result, not planned repeats or a test "
        "name with no result."
    ),
}

_OUTPUT_SCHEMA = {
    "clinical_events": [
        {
            "family": "medication | diagnosis | seizure_frequency | investigation",
            "anchor_text": (
                "Short exact copy from the letter that names the fact. Use the "
                "family guidance below."
            ),
            "evidence": (
                "Exact clause or sentence copied from the letter that supports "
                "the event and all of its mentions."
            ),
            "event_state": (
                "The stated state, such as a dose and frequency, a diagnosis, "
                "a seizure rate, or a test result."
            ),
            "mentions": [
                {
                    "entity": (
                        "One of Prescription, Diagnosis, SeizureFrequency, "
                        "Investigations."
                    ),
                    "text": "Short exact copy from the letter for this family.",
                    "attributes": "Only attributes allowed for that family.",
                }
            ],
            "confidence": "low | medium | high",
            "rationale": "One brief sentence explaining the event.",
        }
    ]
}

# Non-SF encoding rules from the 2026-08-15 convention catalog (16 rules).
_ENCODING_NON_SF = frozenset(
    {
        "rule-11",
        "rule-12",
        "rule-14",
        "rule-16",
        "rule-19",
        "rule-20",
        "rule-21",
        "rule-22",
        "rule-28",
        "rule-29",
        "rule-31",
        "rule-32",
        "rule-68",
        "rule-78",
        "rule-79",
        "rule-80",
    }
)


def build_compact_prompt_input(letter: ExectLetter) -> str:
    """Build the Compact-ledger structured-event payload."""

    payload = {
        "task": _TASK,
        "output_schema": _OUTPUT_SCHEMA,
        "decision_procedure": list(_DECISION_PROCEDURE),
        "family_guidance": dict(_FAMILY_GUIDANCE),
        "attribute_vocabulary": _compact_attribute_vocabulary(),
        "categories": _clean_categories(_event_lane_guide()),
        "clinical_rules": _compact_clinical_rules(),
        "suggested_evidence": [
            _clean_ledger_row(row)
            for row in candidate_evidence_ledger_for_letter(letter)
        ],
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False)


def _compact_clinical_rules() -> list[str]:
    return [
        _clean_rule_text(_rule_text(rule))
        for index, rule in enumerate(_clinical_rules())
        if f"rule-{index + 1:02d}" not in _ENCODING_NON_SF
    ]


def _compact_attribute_vocabulary() -> dict[str, dict[str, Any]]:
    return {
        entity: {
            name: (
                "string copied from the letter."
                if isinstance(value, str) and "normalized" in value
                else value
            )
            for name, value in attrs.items()
        }
        for entity, attrs in _attribute_vocabulary().items()
    }


def _rule_text(rule: str | tuple[str, ...]) -> str:
    return rule if isinstance(rule, str) else "".join(rule)
