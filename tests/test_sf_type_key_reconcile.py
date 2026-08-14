from scripts.sf_type_key_reconcile import apply_type_key_reconcile, candidate_specific_cuis


def _sf(text: str, *, cui: str, **attrs: str) -> dict:
    attributes = {"CUI": cui, "CUIPhrase": text, **attrs}
    return {"entity": "SeizureFrequency", "text": text, "attributes": attributes}


def _dx(text: str, *, cui: str) -> dict:
    return {
        "entity": "Diagnosis",
        "text": text,
        "attributes": {"CUI": cui, "CUIPhrase": text, "DiagCategory": "Epilepsy"},
    }


def test_retargets_generic_rate_to_unique_diagnosis_cui() -> None:
    mentions = [
        _sf("seizures", cui="C0036572", NumberOfSeizures="3", TimePeriod="Week"),
        _dx("generalised tonic clonic seizures", cui="C0494475"),
    ]
    after, actions = apply_type_key_reconcile(mentions, arm="retarget_generic_unique")
    sf = [m for m in after if m["entity"] == "SeizureFrequency"]
    assert sf[0]["attributes"]["CUI"] == "C0494475"
    assert actions[0]["action"] == "retarget"


def test_does_not_retarget_when_two_specific_types_exist() -> None:
    mentions = [
        _sf("seizures", cui="C0036572", NumberOfSeizures="3", TimePeriod="Week"),
        _dx("generalised tonic clonic seizures", cui="C0494475"),
        _dx("myoclonic jerks", cui="C0027066"),
    ]
    assert len(candidate_specific_cuis(mentions)) == 2
    after, actions = apply_type_key_reconcile(mentions, arm="retarget_generic_unique")
    sf = [m for m in after if m["entity"] == "SeizureFrequency"]
    assert sf[0]["attributes"]["CUI"] == "C0036572"
    assert actions == []


def test_drops_generic_when_specific_already_holds_the_state() -> None:
    mentions = [
        _sf("seizures", cui="C0036572", NumberOfSeizures="0", TimePeriod="Year"),
        _sf(
            "focal seizures with altered awareness",
            cui="C0270834",
            NumberOfSeizures="0",
            TimePeriod="Year",
        ),
    ]
    after, actions = apply_type_key_reconcile(
        mentions, arm="drop_generic_duplicate_state"
    )
    sf = [m for m in after if m["entity"] == "SeizureFrequency"]
    assert len(sf) == 1
    assert sf[0]["attributes"]["CUI"] == "C0270834"
    assert actions[0]["action"] == "drop"
