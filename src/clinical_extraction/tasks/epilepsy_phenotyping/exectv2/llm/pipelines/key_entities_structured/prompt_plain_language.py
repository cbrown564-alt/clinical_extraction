"""Compact wording adapters for shared Full-ledger catalog text.

Compact authors its own task, schema, procedure, and family guidance.
These helpers only rewrite shared rule, category, and evidence-row text.
"""

from __future__ import annotations

from typing import Any

_RULE_PREFIXES = (
    "SF recall: ",
    "SF state choice: ",
    "SF precision: ",
    "Medication decision lane: ",
    "Medication current-list split dosing: ",
    "Medication frequency completion: ",
    "Investigation decision lane: ",
    "Investigation pending-test cues are decisive: ",
)

_RULE_PHRASES = (
    ("candidate_evidence_ledger item", "suggested-evidence row"),
    ("candidate_evidence_ledger", "suggested evidence"),
    ("into an event lane:", "into a category:"),
    (
        "Candidate ledger rows are not predictions. ",
        "Suggested-evidence rows are only hints. ",
    ),
    (
        "Return only final clinical_events. Do not return candidate IDs unless "
        "you copy them into event_state as trace strings.",
        "Return only clinical_events.",
    ),
    ("one short final-justification sentence", "one short sentence"),
    (
        "Do not add a generic epilepsy companion to a specific epilepsy subtype",
        "Do not add a separate generic epilepsy diagnosis to a specific "
        "epilepsy subtype",
    ),
    ("atomic diagnostic concepts", "separate diagnoses"),
    ("when that is the source span", "when that is the wording in the letter"),
    ("the source separately asserts", "the letter separately states"),
    ("unless the source also gives", "unless the letter also gives"),
    ("named seizure-frequency row", "named seizure-frequency statement"),
    ("a current scorable epileptic seizure type", "an epileptic seizure type"),
    ("a scorable SF state", "a seizure-frequency fact"),
    ("two SF mentions", "two SeizureFrequency mentions"),
    (
        "mention text is only the seizure-type anchor",
        "mention text is only the seizure-type wording",
    ),
    ("For SeizureFrequency anchors,", "For SeizureFrequency wording,"),
    ("for that anchor even", "for those seizure words even"),
    ("keep the full named anchor", "keep the full named wording"),
    ("that the anchor itself", "that those words themselves"),
    (
        "a seizure-free since-age anchor",
        "a seizure-free since-age time point",
    ),
    ("since that anchor for", "since that point for"),
    ("or a temporal anchor", "or a time point"),
    ("not a merged 'X and Y' anchor", "not a merged 'X and Y' wording"),
    (
        "anchor text to the underlying seizure phrase",
        "set mention text to the underlying seizure phrase",
    ),
    ("a frequency-state attribute", "a frequency attribute"),
    ("When the selected current regimen", "When the current regimen"),
    ("or since-frame is present", "or since period is present"),
    (
        "whose only support is a pending cue",
        "whose only support is pending-test wording",
    ),
    (
        "a bare modality-only investigation",
        "a bare test-name-only investigation",
    ),
    (
        "a duplicate modality-only mention",
        "a duplicate test-name-only mention",
    ),
    ("an ExECTv2 target investigation", "one of the requested investigations"),
    ("an anaphoric anchor", "a pointing phrase"),
    ("generic spell anchors", "vague words"),
    ("are high-value evidence. ", "often state the frequency. "),
    ("the exact medication item span", "the exact medication wording"),
    ("Every rendered mention object", "Every mention"),
    ("Every rendered mention text", "Every mention text"),
    ("can render both", "can include both"),
    ("Do not render", "Do not include"),
    ("do not render", "do not include"),
    ("Never emit", "Never include"),
    ("Do not emit", "Do not include"),
    ("do not emit", "do not include"),
    ("Emit at most", "Include at most"),
    ("emit at most", "include at most"),
    ("render both", "include both"),
    ("render each", "include each"),
    ("render a ", "include a "),
    ("render the ", "include the "),
    ("render only ", "include only "),
    ("render separate ", "include separate "),
    ("render text as", "write text as"),
    ("renders only", "includes only"),
    ("render '", "include '"),
    ("regimens render Prescription", "regimens include Prescription"),
    ("results render Investigations", "results include Investigations"),
    ("Only render ", "Only include "),
    ("already rendered", "already included"),
)

_CATEGORY_PHRASES = (
    (
        "patient-level epilepsy syndrome or named seizure type",
        "this patient's epilepsy syndrome or named seizure type",
    ),
    (
        "bare modality without performed/result/not-performed status",
        "a test name with no completed or result status",
    ),
    (
        "count/rate/current cadence for generic or named seizures",
        "count or rate for generic or named seizures",
    ),
    (
        "unlabelled events, historical best period",
        "unnamed events, or an old best period",
    ),
)


def _clean_categories(lanes: dict[str, list[str]]) -> dict[str, list[str]]:
    cleaned: dict[str, list[str]] = {}
    for family, rows in lanes.items():
        rewritten: list[str] = []
        for row in rows:
            text = row
            for old, new in _CATEGORY_PHRASES:
                text = text.replace(old, new)
            rewritten.append(text)
        cleaned[family] = rewritten
    return cleaned


def _clean_ledger_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": row["family"],
        "evidence": row["evidence"],
        "name_hint": row["anchor_hint"],
        "category": row["lane_hint"],
    }


def _clean_rule_text(rule: str) -> str:
    text = rule
    for prefix in _RULE_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix) :]
            if text:
                text = text[0].upper() + text[1:]
            break
    for old, new in _RULE_PHRASES:
        text = text.replace(old, new)
    return text
