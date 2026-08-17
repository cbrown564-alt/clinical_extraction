"""Full-profile prompt builder for the structured-event extractor.

The selected Full-ledger body and Compact-ledger cut remain live.
Study-only further-prune identities, including ``v0.9.44``, are
registered beside them.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .constants import (
    PromptProfile,
    prompt_version_for,
)
from .prompt_ablations import (
    ABLATION_SPECS,
    apply_v0924_ablation,
    dump_model_facing_payload,
)
from .prompt_content import (
    _attribute_vocabulary,
    _decision_procedure,
    _event_lane_guide,
    _family_guidance,
    _worked_examples,
    candidate_evidence_ledger_for_letter,
)
from .prompt_rules_full import (
    _clinical_rules,
)


def build_full_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "full",
    prompt_version: str | None = None,
) -> str:
    """Build the comprehensive structured-event payload."""

    selected_prompt_version = prompt_version_for(
        prompt_profile,
        prompt_version=prompt_version,
    )
    payload = {
        "prompt_version": selected_prompt_version,
        "task": (
            "Read the clinical letter once. Use the candidate_evidence_ledger as "
            "attention scaffolding, then build a compact list of source-near "
            "clinical events for medication, diagnosis, seizure frequency, and "
            "investigations. Each event may render one or more entity mentions when "
            "the same clinical fact validly belongs to more than one requested family."
        ),
        "architecture": {
            "name": "single hybrid key-family event ledger",
            "inspiration": (
                "Gan structured-events discipline: source-near candidate evidence, "
                "typed state lanes, exact evidence, then final mention renderings."
            ),
            "component_ownership": (
                "The deterministic ledger proposes possible evidence spans only. "
                "The model owns keep/reject/split/merge decisions and final rendered "
                "mentions. Deterministic code later validates evidence, strips illegal "
                "attributes, attaches finite ontology codes, and evaluates outputs."
            ),
        },
        "output_schema": {
            "clinical_events": [
                {
                    "family": "medication | diagnosis | seizure_frequency | investigation",
                    "anchor_text": (
                        "Short exact substring naming the clinical event. Use the "
                        "family guidance below."
                    ),
                    "evidence": (
                        "Exact clause or sentence copied from the letter that supports "
                        "the event and all rendered mentions."
                    ),
                    "event_state": (
                        "Source-near state for clinical reasoning, such as medication "
                        "dose/frequency, diagnostic assertion, seizure rate, or test "
                        "result. Values must be strings."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, SeizureFrequency, Investigations."
                            ),
                            "text": "Short exact substring used for scoring this entity.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the event.",
                }
            ]
        },
        "decision_procedure": _decision_procedure(),
        "candidate_evidence_ledger": candidate_evidence_ledger_for_letter(letter),
        "event_lane_guide": _event_lane_guide(),
        "family_guidance": _family_guidance(),
        "attribute_vocabulary": _attribute_vocabulary(),
        "worked_examples": _worked_examples(),
        "clinical_rules": _clinical_rules(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    spec = ABLATION_SPECS.get(selected_prompt_version)
    if spec is not None:
        payload = apply_v0924_ablation(payload, spec)
        return dump_model_facing_payload(payload, authored_order=spec.authored_order)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
