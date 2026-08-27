"""Rules-only recall-first extract plus encode/Select on the inventory scorer."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    extract_deterministic_all9,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as inv,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    extract_seizure_frequency,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    INVESTIGATION_SAME_RESULT_DEDUPE,
    SF_RATELESS_ANCHOR_DROP,
    apply_select_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    run_letter,
)


def test_investigations_keep_repeated_same_result_at_extract() -> None:
    mentions = inv._extract_investigations(
        "She had a normal MRI in 2016. A later MRI in 2019 was also normal."
    )
    results = [mention.attributes.get("MRI_Results") for mention in mentions]
    assert results == ["Normal", "Normal"]
    prediction = extract_deterministic_all9(
        ExectLetter(
            "INV-REPEAT",
            "She had a normal MRI in 2016. A later MRI in 2019 was also normal.",
        )
    )
    investigations = [
        mention
        for mention in prediction.mentions
        if mention.entity == INVESTIGATIONS.name
    ]
    assert [
        mention.attributes.get("MRI_Results") for mention in investigations
    ] == ["Normal", "Normal"]


def test_investigation_same_result_dedupe_is_select_and_clinical_epilepsy() -> None:
    selected = [
        {
            "entity": INVESTIGATIONS.name,
            "text": "MRI",
            "evidence": "normal MRI in 2016",
            "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        },
        {
            "entity": INVESTIGATIONS.name,
            "text": "MRI",
            "evidence": "MRI in 2019 was also normal",
            "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        },
    ]
    kept, actions = apply_select_rules(
        selected,
        source_mentions=selected,
        note_text="She had a normal MRI in 2016. A later MRI in 2019 was also normal.",
        enabled_rule_ids=frozenset({INVESTIGATION_SAME_RESULT_DEDUPE}),
    )
    assert len(kept) == 1
    assert actions[0]["rule_id"] == INVESTIGATION_SAME_RESULT_DEDUPE
    assert actions[0]["action"] == "drop"
    assert actions[0]["portability"] == "clinical_epilepsy"


def test_diagnosis_recognise_keeps_focal_onset_heading() -> None:
    prediction = extract_deterministic_all9(
        ExectLetter("DX-FOCAL-ONSET", "Diagnosis: focal onset epilepsy (occipital).")
    )
    diagnoses = [
        mention.text.lower()
        for mention in prediction.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert any("focal onset epilepsy" in text or "focal epilepsy" in text for text in diagnoses)


def test_run_letter_encodes_probable_focal_heading_to_focal_epilepsy() -> None:
    result = run_letter(
        ExectLetter(
            "DX-PROBABLE-FOCAL",
            "Diagnosis: epilepsy – probable focal. EEG was abnormal.",
        )
    )
    diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in result.comparison_projection.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert "focal epilepsy" in diagnoses


def test_sf_rateless_anchor_is_optional_and_select_can_drop_it() -> None:
    letter = ExectLetter("SF-RATELESS", "She has focal seizures. No rate is given.")
    default = extract_seizure_frequency(letter)
    recall = extract_seizure_frequency(letter, keep_unassociated_anchors=True)
    default_texts = [mention.text.lower() for mention in default.mentions]
    recall_rows = [
        {
            "entity": mention.entity,
            "text": mention.text,
            "evidence": mention.evidence,
            "attributes": dict(mention.attributes),
        }
        for mention in recall.mentions
        if mention.entity == SEIZURE_FREQUENCY.name
    ]
    assert "focal seizures" not in default_texts or all(
        mention.attributes for mention in default.mentions
    )
    assert any(
        mention.text.lower() == "focal seizures" and not _has_frequency_attrs(mention.attributes)
        for mention in recall.mentions
    )
    kept, actions = apply_select_rules(
        recall_rows,
        source_mentions=recall_rows,
        note_text=letter.note_text,
        enabled_rule_ids=frozenset({SF_RATELESS_ANCHOR_DROP}),
    )
    assert not any(
        str(row.get("text") or "").lower() == "focal seizures"
        and not _has_frequency_attrs(row.get("attributes") or {})
        for row in kept
    )
    assert any(action["rule_id"] == SF_RATELESS_ANCHOR_DROP for action in actions)
    assert actions[0]["portability"] == "seizure_frequency"


def _has_frequency_attrs(attributes: dict[str, str]) -> bool:
    semantic = set(attributes) - {"CUI", "CUIPhrase"}
    return bool(semantic)
