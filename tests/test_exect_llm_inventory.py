"""Inventory extract: scorer + prompt. Living cell-3 method."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.cells import CELL_ORDER, RESULT_COLUMNS
from clinical_extraction.paper.exect import (
    EXTRACT_VERSION,
    INVENTORY_VERSION,
    verify_llm_extract,
    verify_llm_inventory,
)
from clinical_extraction.paper.methods import LIVE_METHODS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as structured_pkg,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
    clinical_inventory_unit_keys,
    inventory_unit_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    gold_headline_support,
    gold_inventory_support,
)

pytestmark = pytest.mark.local_corpus


def _dx(text: str) -> ExectAnnotation:
    return ExectAnnotation(
        entity=DIAGNOSIS.name,
        text=text,
        attributes={"DiagCategory": "Epilepsy", "Certainty": "5", "Negation": "Affirmed"},
    )


def test_extract_is_the_living_cell_3_method() -> None:
    assert "exect_llm_extract" in LIVE_METHODS
    assert LIVE_METHODS["exect_llm_extract"].get("scorer") == (
        "clinical_inventory_unit_keys"
    )
    assert LIVE_METHODS["exect_llm_pre_post"].get("scorer") == (
        "clinical_inventory_unit_keys"
    )
    assert LIVE_METHODS["exect_llm_extract"].get("paper_cell") is not False
    assert LIVE_METHODS["exect_llm_extract_filtered"].get("paper_cell") is False
    assert LIVE_METHODS["exect_llm_only"]["alias_of"] == "exect_llm_extract_and_select"
    assert LIVE_METHODS["exect_llm_inventory"]["alias_of"] == "exect_llm_extract"
    assert "exect_llm_extract" not in RESULT_COLUMNS
    assert "llm_inventory" not in CELL_ORDER
    assert EXTRACT_VERSION == structured.EXECT_LLM_EXTRACT == INVENTORY_VERSION


def test_inventory_keeps_generic_and_specific_diagnosis() -> None:
    mentions = [_dx("epilepsy"), _dx("focal epilepsy")]
    headline = clinical_headline_unit_keys("Diagnosis", mentions)
    inventory = clinical_inventory_unit_keys("Diagnosis", mentions)
    assert inventory_unit_keys is clinical_inventory_unit_keys
    assert len(inventory) >= len(headline)
    assert ("Diagnosis", "epilepsy") in inventory
    assert ("Diagnosis", "focal epilepsy") in inventory


def test_dev140_diagnosis_inventory_count_vs_headline() -> None:
    letters = list(load_letters_for_split("dev"))
    assert len(letters) == 140
    headline = gold_headline_support(letters)
    inventory = gold_inventory_support(letters)
    dx_h = headline["by_family"]["Diagnosis"]
    dx_i = inventory["by_family"]["Diagnosis"]
    assert dx_h == 289
    assert dx_i >= dx_h
    assert dx_i == 329
    assert inventory["by_family"]["SeizureFrequency"] == headline["by_family"][
        "SeizureFrequency"
    ]
    assert inventory["by_family"]["Prescription"] == headline["by_family"]["Prescription"]
    assert inventory["by_family"]["Investigations"] == headline["by_family"][
        "Investigations"
    ]


def test_inventory_prompt_is_authored_separately_from_compact() -> None:
    package_dir = Path(structured_pkg.__file__).parent
    inventory_source = (package_dir / "prompt_inventory.py").read_text()
    compact_source = (package_dir / "prompt_compact.py").read_text()
    assert "INVENTORY_AUTHORED_KEYS" in inventory_source
    assert "build_inventory_prompt_input" in inventory_source
    assert "_INVENTORY_DROPPED_DIAGNOSIS_RULES" not in inventory_source
    assert "_INVENTORY_DROPPED_SF_RULES" not in inventory_source
    assert "build_compact_llm_inventory_prompt_input" not in compact_source
    assert "INVENTORY_AUTHORED_KEYS" not in compact_source
    assert "_INVENTORY_DROPPED_DIAGNOSIS_RULES" not in compact_source
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    payload = json.loads(
        structured.build_prompt_input(letter, prompt_version=INVENTORY_VERSION)
    )
    shared = " ".join(payload["clinical_rules"]["shared"])
    assert "Use one event per medication, diagnostic concept" not in shared
    assert "Write a separate event for each stated" in shared


def test_inventory_prompt_emits_both_and_leaves_live_default() -> None:
    before = structured.PROMPT_VERSION
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    payload = json.loads(
        structured.build_prompt_input(letter, prompt_version=INVENTORY_VERSION)
    )
    diagnosis_rules = " ".join(payload["clinical_rules"]["diagnosis"])
    sf_rules = " ".join(payload["clinical_rules"]["seizure_frequency"])
    procedure = " ".join(payload["decision_procedure"])
    assert "nocturnal GTCS" in diagnosis_rules or any(
        "nocturnal GTCS" in json.dumps(ex) for ex in payload["examples"]
    )
    assert "named seizure type in a seizure-type or frequency heading" in diagnosis_rules
    assert "Do not write the hedge word alone as the fact" in diagnosis_rules
    assert "write a seizure-frequency event for each named type" in sf_rules.lower()
    assert "keep a separate generic seizure event" in sf_rules
    assert "still write the event" in sf_rules
    assert "Heading-named myoclonic jerks and absences" in sf_rules
    assert "Write it even when that date is years ago" in sf_rules
    assert "Never include a seizure-frequency event with empty attributes" not in sf_rules
    assert "Include at most one seizure-frequency event" not in sf_rules
    assert "are not enough on their own" not in sf_rules
    assert "Reject vague words such as 'events'" not in sf_rules
    assert "previous seizure was a year ago" not in sf_rules
    assert "Onset-history statements such as" not in sf_rules
    assert "Do not add a separate generic epilepsy diagnosis to a specific" not in (
        diagnosis_rules
    )
    assert "Prefer the most specific epilepsy syndrome or seizure type" not in (
        diagnosis_rules
    )
    assert "Onset-history phrases such as" not in diagnosis_rules
    assert "remove exact duplicate events" not in procedure
    assert "only after the state is clear" not in procedure
    assert "Write every stated diagnosis" in procedure
    assert "Provide exact evidence from the letter" in procedure
    assert "Do not delete events before returning JSON" not in procedure
    assert list(payload) == list(structured.INVENTORY_AUTHORED_KEYS)
    assert structured.compact_rule_count(payload["clinical_rules"]) == (
        structured.INVENTORY_RULE_COUNT
    )
    assert len(payload["examples"]) == 5
    assert any(
        "has not had any further seizures" in json.dumps(example)
        for example in payload["examples"]
    )
    assert any(
        "Myoclonic jerks daily" in json.dumps(example)
        for example in payload["examples"]
    )
    blob = json.dumps(payload).lower()
    for phrase in (
        "gold label",
        "headline",
        "unit key",
        "clinical f1",
        "scorer",
        "annotation",
        "leftover",
        "residual",
        "regex",
    ):
        assert phrase not in blob
    only = json.loads(
        structured.build_prompt_input(letter, prompt_version=structured.EXECT_LLM_ONLY)
    )
    assert payload["family_guidance"]["medication"] == only["family_guidance"]["medication"]
    assert payload["family_guidance"]["investigation"] == only["family_guidance"]["investigation"]
    assert "Write fact as only that short name." not in payload["family_guidance"]["diagnosis"]
    assert "Write fact as only that short name." in only["family_guidance"]["diagnosis"]
    assert "heading types such as myoclonic jerks" in payload["family_guidance"]["diagnosis"]
    assert "Write diagnosis fact as only the short syndrome" not in diagnosis_rules
    assert "Do not include isolated symptoms or aura features as diagnosis" not in diagnosis_rules
    assert "Do not put hedges, timing, or extra anatomy" not in diagnosis_rules
    assert "Do not include vague symptoms, blackout" in diagnosis_rules
    assert "A problem-list or diagnosis header is not enough" in diagnosis_rules
    assert "split compound seizure clauses" in diagnosis_rules
    assert "tonic chronic" in diagnosis_rules
    assert "use the exact abbreviation as fact" in diagnosis_rules
    assert payload["decision_procedure"] != only["decision_procedure"]
    assert all("remove duplicates" not in step for step in only["decision_procedure"])
    only_dx = " ".join(only["clinical_rules"]["diagnosis"])
    only_sf = " ".join(only["clinical_rules"]["seizure_frequency"])
    only_shared = " ".join(only["clinical_rules"]["shared"])
    assert "Do not add a separate generic epilepsy diagnosis to a specific" not in (
        only_dx
    )
    assert "Prefer the most specific epilepsy syndrome or seizure type" not in (
        only_dx
    )
    assert "Onset-history phrases such as" not in only_dx
    assert "Use one event per medication, diagnostic concept" not in only_shared
    assert "Keep a generic epilepsy diagnosis when the letter states it" in only_dx
    assert "named seizure type in a seizure-type or frequency heading" in only_dx
    assert "Never include a seizure-frequency event with empty attributes" in only_sf
    assert "examples" not in only
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_both_extract_is_inventory_plus_suggested_candidates() -> None:
    letter = ExectLetter(
        letter_id="EA0000",
        note_text="Diagnosis: Epilepsy, probable focal onset. She remains well.",
    )
    extract = json.loads(
        structured.build_prompt_input(letter, prompt_version=INVENTORY_VERSION)
    )
    both = json.loads(
        structured.build_prompt_input(
            letter, prompt_version=structured.EXECT_LLM_PRE_POST
        )
    )
    assert list(both) == list(structured.INVENTORY_BOTH_AUTHORED_KEYS)
    assert "suggested_evidence" in both
    assert "categories" not in both
    assert both["suggested_evidence"]
    assert both["clinical_rules"] == extract["clinical_rules"]
    assert both["examples"] == extract["examples"]
    assert both["family_guidance"] == extract["family_guidance"]
    assert both["attribute_vocabulary"] == extract["attribute_vocabulary"]
    assert both["output_schema"] == extract["output_schema"]
    assert "Write every stated diagnosis" in " ".join(both["decision_procedure"])
    assert "remove duplicates" not in " ".join(both["decision_procedure"])
    assert "Use the suggested evidence as a starting point" in both["task"]
    assert "suggested evidence" not in extract["task"]
    assert "suggested_evidence" not in extract
    expected = [
        {
            "family": str(row["family"]),
            "evidence": str(row["evidence"]),
            "name_hint": str(row["anchor_hint"]),
            "category": str(row["lane_hint"]),
        }
        for row in structured.high_priority_evidence_ledger_for_letter(letter)
    ]
    assert both["suggested_evidence"] == expected


def test_verify_llm_extract_does_not_change_live_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_llm_extract(split="dev140")
    assert payload["ok"] is True
    assert payload["method"] == "exect_llm_extract"
    assert payload["prompt_version"] == structured.EXECT_LLM_EXTRACT
    assert payload["work_root"] == "experiments/paper/exect_llm_extract"
    assert verify_llm_inventory is verify_llm_extract
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_inventory_residuals_ablation_invents_named_type() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        inventory_residuals,
    )

    note = (
        "Diagnosis: symptomatic structural focal epilepsy. "
        "Seizure type and frequency: focal seizures with altered awareness every 3 weeks; "
        "focal to bilateral convulsive seizures 2014. "
        "She remains seizure free."
    )
    mentions = [
        {
            "entity": "Diagnosis",
            "text": "symptomatic structural focal epilepsy",
            "attributes": {"DiagCategory": "Epilepsy"},
        },
        {
            "entity": "SeizureFrequency",
            "text": "focal seizures with altered awareness",
            "attributes": {
                "CUIPhrase": "focal seizures with altered awareness",
                "NumberOfSeizures": "1",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Week",
            },
            "evidence": (
                "Seizure type and frequency: focal seizures with altered awareness "
                "every 3 weeks; focal to bilateral convulsive seizures 2014."
            ),
        },
    ]
    updated, stats = inventory_residuals.apply_inventory_residuals(note, mentions)
    texts = {(row["entity"], row["text"]) for row in updated}
    assert stats["diagnosis_residual_adds"] >= 1
    assert ("Diagnosis", "focal seizures with altered awareness") in texts
    assert stats["sf_adds"] == 0
    assert "invent" in inventory_residuals.apply_inventory_residuals.__doc__.lower()
