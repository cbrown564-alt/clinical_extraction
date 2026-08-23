"""Diagnostic inventory track: scorer + prompt, not a paper cell."""

from __future__ import annotations

import json

import pytest

from clinical_extraction.paper.cells import CELL_ORDER, RESULT_COLUMNS
from clinical_extraction.paper.exect import (
    INVENTORY_VERSION,
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


def test_inventory_method_is_live_but_not_a_paper_cell() -> None:
    assert "exect_llm_inventory" in LIVE_METHODS
    assert "exect_llm_inventory" not in RESULT_COLUMNS
    assert "llm_inventory" not in CELL_ORDER
    assert LIVE_METHODS["exect_llm_inventory"].get("paper_cell") is False


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


def test_inventory_prompt_emits_both_and_leaves_live_default() -> None:
    before = structured.PROMPT_VERSION
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    payload = json.loads(
        structured.build_prompt_input(letter, prompt_version=INVENTORY_VERSION)
    )
    diagnosis_rules = " ".join(payload["clinical_rules"]["diagnosis"])
    assert "include each as its own diagnosis event" in diagnosis_rules
    assert "more specific place or type" in diagnosis_rules
    assert "nocturnal GTCS" in diagnosis_rules or any(
        "nocturnal GTCS" in json.dumps(ex) for ex in payload["examples"]
    )
    sf_rules = " ".join(payload["clinical_rules"]["seizure_frequency"])
    assert "write a seizure-frequency event for each named type" in sf_rules.lower()
    assert "keep a separate generic seizure event" in sf_rules
    assert "Do not add a separate generic epilepsy diagnosis to a specific" not in (
        diagnosis_rules
    )
    assert "Prefer the most specific epilepsy syndrome or seizure type" not in (
        diagnosis_rules
    )
    assert "Onset-history phrases such as" not in diagnosis_rules
    assert list(payload) == list(structured.INVENTORY_AUTHORED_KEYS)
    assert structured.compact_rule_count(payload["clinical_rules"]) == 50
    assert len(payload["examples"]) == 3
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
    assert payload["family_guidance"]["seizure_frequency"] == only["family_guidance"]["seizure_frequency"]
    assert payload["family_guidance"]["investigation"] == only["family_guidance"]["investigation"]
    assert "Write fact as only that short name." not in payload["family_guidance"]["diagnosis"]
    assert "Write fact as only that short name." in only["family_guidance"]["diagnosis"]
    assert "Do not include vague symptoms or non-epileptic" in payload["family_guidance"]["diagnosis"]
    assert "Write diagnosis fact as only the short syndrome" not in diagnosis_rules
    assert "Do not include isolated symptoms or aura features as diagnosis" not in diagnosis_rules
    assert "Do not put hedges, timing, or extra anatomy" not in diagnosis_rules
    assert "Do not include vague symptoms, blackout" in diagnosis_rules
    assert "A problem-list or diagnosis header is not enough" in diagnosis_rules
    assert "split compound seizure clauses" in diagnosis_rules
    assert "Never write 'tonic chronic'" in diagnosis_rules
    assert "use the exact abbreviation as fact" in diagnosis_rules
    assert payload["decision_procedure"] != only["decision_procedure"]
    assert any("remove exact duplicate events" in step for step in payload["decision_procedure"])
    assert not any("remove exact duplicate events" in step for step in only["decision_procedure"])
    only_dx = " ".join(only["clinical_rules"]["diagnosis"])
    assert "Do not add a separate generic epilepsy diagnosis to a specific" in only_dx
    assert "Prefer the most specific epilepsy syndrome or seizure type" in only_dx
    assert "Onset-history phrases such as" in only_dx
    assert "examples" not in only
    assert structured.PROMPT_VERSION == before == structured.EXECT_LLM_PRE_POST


def test_verify_llm_inventory_does_not_change_live_default() -> None:
    before = structured.PROMPT_VERSION
    payload = verify_llm_inventory(split="dev140")
    assert payload["ok"] is True
    assert payload["method"] == "exect_llm_inventory"
    assert payload["prompt_version"] == structured.EXECT_LLM_INVENTORY
    assert payload["work_root"] == "experiments/paper/exect_llm_inventory"
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
