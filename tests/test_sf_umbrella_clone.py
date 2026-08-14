from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_umbrella_clone as umbrella_clone,
)

apply_umbrella_clone_drop = umbrella_clone.apply_umbrella_clone_drop


def _sf(text: str, *, cui: str, evidence: str = "", **attrs: str) -> dict:
    attributes = {"CUI": cui, "CUIPhrase": text, **attrs}
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": attributes,
        "evidence": evidence,
    }


def _dx(text: str, *, cui: str, evidence: str) -> dict:
    return {
        "entity": "Diagnosis",
        "text": text,
        "attributes": {"CUI": cui, "CUIPhrase": text, "DiagCategory": "Epilepsy"},
        "evidence": evidence,
    }


def test_drops_generic_clone_of_specific_span() -> None:
    span = "focal to bilateral seizures 2 events in total, last event 10 years ago."
    mentions = [
        _sf(
            "focal seizures with altered awareness",
            cui="C0270834",
            evidence="focal seizures with altered awareness, last event 3 years ago",
            NumberOfSeizures="0",
            NumberOfTimePeriods="3",
            TimePeriod="Year",
        ),
        _sf(
            "seizures",
            cui="C0036572",
            evidence=span,
            NumberOfSeizures="0",
            NumberOfTimePeriods="10",
            TimePeriod="Year",
        ),
        _sf(
            "focal to bilateral seizures",
            cui="C0877017",
            evidence=span,
            NumberOfSeizures="0",
            NumberOfTimePeriods="10",
            TimePeriod="Year",
        ),
    ]
    after, actions = apply_umbrella_clone_drop(mentions)
    sf = [m for m in after if m["entity"] == "SeizureFrequency"]
    assert [m["attributes"]["CUI"] for m in sf] == ["C0270834", "C0877017"]
    assert actions[0]["action"] == "drop"


def test_keeps_generic_when_evidence_differs() -> None:
    mentions = [
        _sf(
            "focal to bilateral convulsive seizures",
            cui="C0877017",
            evidence="focal to bilateral convulsive seizures, last event 2018",
            NumberOfSeizures="0",
        ),
        _sf(
            "seizure free",
            cui="C1299590",
            evidence="he remains seizure free after his surgery.",
            NumberOfSeizures="0",
        ),
    ]
    after, actions = apply_umbrella_clone_drop(mentions)
    assert [m["attributes"]["CUI"] for m in after] == ["C0877017", "C1299590"]
    assert actions == []


def test_keeps_generic_when_window_differs() -> None:
    span = "same sentence"
    mentions = [
        _sf(
            "seizures",
            cui="C0036572",
            evidence=span,
            NumberOfSeizures="1",
            TimePeriod="Month",
        ),
        _sf(
            "focal seizures",
            cui="C0270834",
            evidence=span,
            NumberOfSeizures="0",
            NumberOfTimePeriods="10",
            TimePeriod="Month",
        ),
    ]
    after, actions = apply_umbrella_clone_drop(mentions)
    assert [m["attributes"]["CUI"] for m in after] == ["C0036572", "C0270834"]
    assert actions == []


def test_diagnosis_mention_is_not_a_sibling() -> None:
    span = "focal to bilateral seizures last event 10 years ago"
    mentions = [
        _dx("focal to bilateral seizures", cui="C0877017", evidence=span),
        _sf(
            "seizures",
            cui="C0036572",
            evidence=span,
            NumberOfSeizures="0",
            NumberOfTimePeriods="10",
            TimePeriod="Year",
        ),
    ]
    after, actions = apply_umbrella_clone_drop(mentions)
    assert after[-1]["attributes"]["CUI"] == "C0036572"
    assert actions == []


def test_cluster_cui_is_not_a_generic_self_clone() -> None:
    mentions = [
        _sf(
            "cluster of seizures",
            cui="C3203523",
            evidence="cluster of seizures",
            NumberOfSeizures="3",
            TimePeriod="Day",
        )
    ]
    after, actions = apply_umbrella_clone_drop(mentions)
    assert after[0]["attributes"]["CUI"] == "C3203523"
    assert actions == []


def test_empty_window_does_not_match() -> None:
    span = "seizure free since surgery"
    mentions = [
        _sf("seizures", cui="C0036572", evidence=span),
        _sf(
            "focal seizures",
            cui="C0270834",
            evidence=span,
            NumberOfSeizures="0",
        ),
    ]
    after, actions = apply_umbrella_clone_drop(mentions)
    assert [m["attributes"]["CUI"] for m in after] == ["C0036572", "C0270834"]
    assert actions == []
