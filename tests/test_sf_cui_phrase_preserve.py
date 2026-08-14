from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_cui_phrase_preserve as cui_phrase_preserve,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    assign_cui,
)

apply_cui_phrase_preserve = cui_phrase_preserve.apply_cui_phrase_preserve


def _sf(text: str, *, cui: str = "", **attrs: str) -> dict:
    attributes = dict(attrs)
    if cui:
        attributes["CUI"] = cui
        attributes.setdefault("CUIPhrase", text)
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": attributes,
        "evidence": text,
    }


def test_assign_cui_preserves_cluster_and_generlised() -> None:
    assert assign_cui("cluster of seizures") == "C3203523"
    assert assign_cui("clusters of seizure") == "C3203523"
    assert assign_cui("seizure cluster") == "C3203523"
    assert assign_cui("generlised tonic clonic seizure") == "C0494475"
    assert assign_cui("seizures") == "C0036572"


def test_preserve_rewrites_generic_cluster_cui() -> None:
    mentions = [_sf("cluster of seizures", cui="C0036572", NumberOfSeizures="3")]
    after, actions = apply_cui_phrase_preserve(mentions, arm="preserve_cluster_cui")
    assert after[0]["attributes"]["CUI"] == "C3203523"
    assert after[0]["attributes"]["CUIPhrase"] == "cluster of seizures"
    assert after[0]["text"] == "cluster of seizures"
    assert actions[0]["action"] == "preserve_cluster_cui"


def test_preserve_ignores_cluster_of_count() -> None:
    mentions = [_sf("cluster of 3", cui="C0036572", NumberOfSeizures="3")]
    after, actions = apply_cui_phrase_preserve(mentions, arm="preserve_cluster_cui")
    assert after[0]["attributes"]["CUI"] == "C0036572"
    assert actions == []


def test_preserve_does_not_overwrite_specific_cui() -> None:
    mentions = [_sf("cluster of seizures", cui="C0494475")]
    after, actions = apply_cui_phrase_preserve(mentions, arm="preserve_cluster_cui")
    assert after[0]["attributes"]["CUI"] == "C0494475"
    assert actions == []


def test_generlised_typo_gets_gtcs_cui() -> None:
    mentions = [_sf("generlised tonic clonic seizure", NumberOfSeizures="1")]
    after, actions = apply_cui_phrase_preserve(mentions, arm="fold_generlised_cui")
    assert after[0]["attributes"]["CUI"] == "C0494475"
    assert after[0]["text"] == "generlised tonic clonic seizure"
    assert actions[0]["action"] == "fold_generlised_cui"


def test_generlised_does_not_overwrite_existing_cui() -> None:
    mentions = [_sf("generlised tonic clonic seizure", cui="C0234533")]
    after, actions = apply_cui_phrase_preserve(mentions, arm="fold_generlised_cui")
    assert after[0]["attributes"]["CUI"] == "C0234533"
    assert actions == []


def test_bundle_applies_cluster_then_typo() -> None:
    mentions = [
        _sf("cluster of seizures", cui="C0036572"),
        _sf("generlised tonic chronic seizures"),
        _sf("seizures", cui="C0036572"),
    ]
    after, actions = apply_cui_phrase_preserve(mentions, arm="bundle")
    assert after[0]["attributes"]["CUI"] == "C3203523"
    assert after[1]["attributes"]["CUI"] == "C0494475"
    assert after[2]["attributes"]["CUI"] == "C0036572"
    assert [item["action"] for item in actions] == [
        "preserve_cluster_cui",
        "fold_generlised_cui",
    ]
