"""Always-on contract for ExECT later-stage encode and select prompts."""

from __future__ import annotations

import json

from clinical_extraction.paper.exect_later_stage import join_encode_mentions
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_llm_encode import (
    EXECT_LLM_ENCODE,
    LLM_ENCODE_AUTHORED_KEYS,
    build_llm_encode_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_llm_select import (
    EXECT_LLM_SELECT,
    LLM_SELECT_AUTHORED_KEYS,
    build_llm_select_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_standard_names import (
    standard_names_payload,
)

_EXTRACT_MENTIONS = [
    {
        "mention_id": "m1",
        "entity": "SeizureFrequency",
        "text": "tonic clonic seizures",
        "evidence": "2 generalised tonic clonic seizures in 2014",
        "attributes": {
            "NumberOfSeizures": "2",
            "YearDate": "2014",
            "CUI": "must-not-appear",
            "CUIPhrase": "must-not-appear",
        },
    },
    {
        "mention_id": "m2",
        "clinical_family": "Diagnosis",
        "clinical_name": "Focal epilepsy",
        "evidence": "Diagnosis Focal epilepsy, probable occipital lobe onset",
        "attributes": {},
    },
]


def test_flatten_mints_missing_mention_ids() -> None:
    rows = structured.assign_flatten_mention_ids(
        [{"text": "a"}, {"text": "b", "finding_id": "kept"}]
    )
    assert rows[0]["mention_id"] == "m1"
    assert rows[1]["mention_id"] == "kept"


def test_join_encode_writes_standard_name_and_attaches_cui() -> None:
    joined = join_encode_mentions(
        [
            {
                "mention_id": "m1",
                "entity": "SeizureFrequency",
                "text": "tonic clonic seizures",
                "attributes": {"NumberOfSeizures": "2"},
            }
        ],
        [
            {
                "mention_id": "m1",
                "standard_name": "generalised tonic clonic seizures",
                "details": {"count": "2"},
            }
        ],
    )
    assert joined[0]["text"] == "generalised tonic clonic seizures"
    assert joined[0]["attributes"]["NumberOfSeizures"] == "2"
    assert joined[0]["attributes"]["CUI"] == "C0494475"


def test_prompt_versions_are_stable() -> None:
    assert EXECT_LLM_ENCODE == "exect_llm_encode"
    assert EXECT_LLM_SELECT == "exect_llm_select"


def test_standard_names_cover_every_family() -> None:
    payload = standard_names_payload()
    diagnosis = [row["standard_name"] for row in payload["diagnosis"]]
    medicines = [row["standard_name"] for row in payload["medicines"]]
    tests = [row["standard_name"] for row in payload["tests"]]
    assert "focal epilepsy" in diagnosis
    assert "temporal lobe epilepsy" in diagnosis
    assert "levetiracetam" in medicines
    assert "sodium valproate" in medicines
    assert tests == ["MRI", "CT", "EEG"]
    assert payload["details"]["SeizureFrequency"]["period"] == [
        "Day",
        "Week",
        "Month",
        "Year",
    ]
    assert payload["details"]["Prescription"]["dose"] == "number already on the row"
    assert payload["details"]["Prescription"]["unit"] == ["mg", "g"]
    assert payload["details"]["Investigations"]["result"] == [
        "Normal",
        "Abnormal",
        "Unknown",
    ]
    assert "certainty" not in json.dumps(payload["details"])
    assert "negation" not in json.dumps(payload["details"])
    blob = json.dumps(payload)
    assert "C0014544" not in blob
    assert "CUI" not in blob
    epilepsy = next(
        row for row in payload["diagnosis"] if row["standard_name"] == "epilepsy"
    )
    assert "also" not in epilepsy


def test_standard_names_list_the_sixteen_heads() -> None:
    payload = standard_names_payload()
    names = [row["standard_name"] for row in payload["seizure_types"]]
    assert names[-1] == "seizures"
    assert "generalised tonic clonic seizures" in names
    assert "grand mal" not in names
    assert len(names) == 16
    assert len(set(names)) == 16
    gtc = next(
        row
        for row in payload["seizure_types"]
        if row["standard_name"] == "generalised tonic clonic seizures"
    )
    assert "grand mal" in gtc["also"]
    assert "tonic clonic seizures" in gtc["also"]
    assert "generalised" not in gtc["also"]
    seizures = next(
        row for row in payload["seizure_types"] if row["standard_name"] == "seizures"
    )
    assert "no further seizures" not in seizures["also"]


def test_encode_payload_has_no_letter_and_no_cui() -> None:
    payload = json.loads(build_llm_encode_prompt_input(_EXTRACT_MENTIONS))
    blob = json.dumps(payload)
    assert set(payload) == set(LLM_ENCODE_AUTHORED_KEYS)
    assert "letter_text" not in payload
    assert "note_text" not in payload
    assert payload["mentions"] == [
        {
            "mention_id": "m1",
            "clinical_family": "SeizureFrequency",
            "clinical_name": "tonic clonic seizures",
            "supporting_sentence": "2 generalised tonic clonic seizures in 2014",
            "details": {"count": "2", "year": "2014"},
        },
        {
            "mention_id": "m2",
            "clinical_family": "Diagnosis",
            "clinical_name": "Focal epilepsy",
            "supporting_sentence": "Diagnosis Focal epilepsy, probable occipital lobe onset",
            "details": {},
        },
    ]
    assert payload["standard_names"] == standard_names_payload()
    assert "leave mention_id unchanged" in blob.lower()
    assert "standard name" in blob.lower()
    _assert_no_internal_prompt_language(blob)


def test_select_payload_omits_clinical_name() -> None:
    encoded = [
        {
            "mention_id": "m1",
            "clinical_family": "SeizureFrequency",
            "standard_name": "generalised tonic clonic seizures",
            "supporting_sentence": "2 generalised tonic clonic seizures in 2014",
            "details": {"count": "2", "year": "2014"},
            "clinical_name": "must-not-appear",
            "text": "must-not-appear",
        }
    ]
    payload = json.loads(build_llm_select_prompt_input(encoded))
    blob = json.dumps(payload)
    assert set(payload) == set(LLM_SELECT_AUTHORED_KEYS)
    assert "letter_text" not in payload
    assert payload["mentions"] == [
        {
            "mention_id": "m1",
            "clinical_family": "SeizureFrequency",
            "standard_name": "generalised tonic clonic seizures",
            "supporting_sentence": "2 generalised tonic clonic seizures in 2014",
            "details": {"count": "2", "year": "2014"},
        }
    ]
    assert "must-not-appear" not in blob
    assert "do not write a new quote" in blob.lower()
    assert "companion" in blob.lower()
    _assert_no_internal_prompt_language(blob)


def _assert_no_internal_prompt_language(blob: str) -> None:
    lowered = blob.lower()
    for term in (
        "cui",
        "cuiphrase",
        "codebook",
        "frozen",
        "hybrid",
        "gold",
        "residual",
        "leftover",
        "invent",
        "designed",
        "lexicon",
        "umls",
        "encode",
        "rung",
        "exect",
    ):
        assert term not in lowered, term
