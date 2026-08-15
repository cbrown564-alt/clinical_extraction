"""Gold-free mechanism tests for rules-only Investigations extraction."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as inv,
)

_extract_investigations = inv._extract_investigations


def _by_modality(text: str) -> dict[str, dict[str, str]]:
    return {mention.text: dict(mention.attributes) for mention in _extract_investigations(text)}


def test_same_sentence_list9_finding_is_abnormal() -> None:
    attrs = _by_modality("An EEG in 2014 did show some temporal slowing.")
    assert attrs["EEG"]["EEG_Results"] == "Abnormal"


def test_gliosis_and_atrophy_are_abnormal_mri() -> None:
    gliosis = _by_modality(
        "Her last MRI in January 2018 did show frontal lobe gliosis."
    )
    atrophy = _by_modality("MRI 1993: mild cerebellar atrophy")
    assert gliosis["MRI"]["MRI_Results"] == "Abnormal"
    assert atrophy["MRI"]["MRI_Results"] == "Abnormal"


def test_next_sentence_anaphora_binds_finding() -> None:
    attrs = _by_modality(
        "He had an MRI brain performed in 2016. "
        "This does show some left-sided white matter changes."
    )
    assert attrs["MRI"]["MRI_Results"] == "Abnormal"
    assert len(attrs) == 1


def test_planned_test_is_dropped() -> None:
    attrs = _by_modality(
        "I will arrange an MRI scan of his brain as well as an ECG."
    )
    assert attrs == {}


def test_completed_normal_kept_when_sibling_eeg_is_awaited() -> None:
    attrs = _by_modality(
        "Her MRI has been reported as normal and she is awaiting an appointment for an EEG."
    )
    assert attrs["MRI"]["MRI_Results"] == "Normal"
    assert "EEG" not in attrs


def test_negated_epileptiform_is_normal() -> None:
    attrs = _by_modality(
        "Doing a video EEG she had some of these episodes and there "
        "was no epileptiform EEG correlate."
    )
    assert attrs["EEG"]["EEG_Results"] == "Normal"


def test_sibling_modalities_keep_their_own_results() -> None:
    attrs = _by_modality(
        "As you know she has had a normal MRI scan last year and previously "
        "has had an abnormal EEG with some generalised spike and wave abnormalities."
    )
    assert attrs["MRI"]["MRI_Results"] == "Normal"
    assert attrs["EEG"]["EEG_Results"] == "Abnormal"


def test_comma_split_eeg_abnormal_mri_negative() -> None:
    attrs = _by_modality("Focal EEG abnormalities, MRI negative")
    assert attrs["EEG"]["EEG_Results"] == "Abnormal"
    assert attrs["MRI"]["MRI_Results"] == "Normal"


def test_coordinated_pair_shares_trailing_normal() -> None:
    attrs = _by_modality("MRI and EEG have been normal.")
    assert attrs["MRI"]["MRI_Results"] == "Normal"
    assert attrs["EEG"]["EEG_Results"] == "Normal"


def test_unknown_result_when_report_absent() -> None:
    attrs = _by_modality("I do not have the results of his recent EEG test.")
    assert attrs["EEG"]["EEG_Results"] == "Unknown"


def test_stated_normal_wins_over_unseen_report() -> None:
    attrs = _by_modality(
        "He had an MRI scan around 5 years ago which was normal "
        "although I have not seen the report."
    )
    assert attrs["MRI"]["MRI_Results"] == "Normal"


def test_ecg_normal_is_not_a_ct_result() -> None:
    attrs = _by_modality(
        "She had a CT head in 2013 and an ECG in clinic today shows a "
        "sinus rhythm of 72 bpm, a normal QT interval and normal QRS morphology."
    )
    assert "CT" not in attrs or attrs["CT"].get("CT_Results") != "Normal"


def test_duplicate_tokens_collapse_to_one_result() -> None:
    mentions = _extract_investigations(
        "EEG 2019: generalised spike and wave with photosensitivity. "
        "I explained that the EEG changes, which show a generalised pattern, "
        "are in keeping with the syndrome. I explained that the EEG also "
        "showed evidence of photosensitivity."
    )
    eeg = [mention for mention in mentions if mention.text == "EEG"]
    assert len(eeg) == 1
    assert eeg[0].attributes["EEG_Results"] == "Abnormal"


def test_simple_abnormal_and_normal_pair_still_works() -> None:
    attrs = _by_modality("EEG was abnormal. MRI brain was normal.")
    assert attrs["EEG"]["EEG_Results"] == "Abnormal"
    assert attrs["MRI"]["MRI_Results"] == "Normal"


def test_they_anaphora_binds_hyperintensity() -> None:
    attrs = _by_modality(
        "As you know he has now had 2 MRI scans. "
        "They have both shown a small hyperintensity in the posterior frontal lobe."
    )
    assert attrs["MRI"]["MRI_Results"] == "Abnormal"


def test_ecg_and_ct_were_normal_keeps_ct() -> None:
    attrs = _by_modality("I note that his ECG and CT head were normal.")
    assert attrs["CT"]["CT_Results"] == "Normal"


def test_finding_before_next_modality_stays_with_first() -> None:
    attrs = _by_modality(
        "Her MRI does show some gliosis and changes in the left "
        "fronto-temporal region and an EEG in 2016 did show focal slowing."
    )
    assert attrs["MRI"]["MRI_Results"] == "Abnormal"
    assert attrs["EEG"]["EEG_Results"] == "Abnormal"


def test_normal_as_was_an_eeg_shares_result() -> None:
    attrs = _by_modality(
        "A previous CT scan of the brain in 2002 was normal as was an EEG examination."
    )
    assert attrs["CT"]["CT_Results"] == "Normal"
    assert attrs["EEG"]["EEG_Results"] == "Normal"


def test_slowing_beats_otherwise_normal_in_same_clause() -> None:
    mentions = _extract_investigations(
        "Her EEG showed some minor temporal slowing but otherwise was reported as normal. "
        "Her sleep deprived EEG did not show any epileptic activity."
    )
    results = sorted(
        mention.attributes["EEG_Results"]
        for mention in mentions
        if mention.text == "EEG"
    )
    assert results == ["Abnormal", "Normal"]


def test_clear_changes_is_not_a_normal_result() -> None:
    attrs = _by_modality(
        "Investigations: MRI, right parietal focal cortical dysplasia. "
        "Given the clear changes on his MRI scan he would be high risk."
    )
    assert attrs["MRI"]["MRI_Results"] == "Abnormal"


def test_normal_apart_from_tiny_hyperintensity_stays_normal() -> None:
    attrs = _by_modality(
        "He had a MRI scan in 2014 which was normal apart from a few "
        "scattered tiny hyperintensities."
    )
    assert attrs["MRI"]["MRI_Results"] == "Normal"


def test_occipital_focus_is_abnormal_eeg() -> None:
    attrs = _by_modality(
        "Previous MRI scans have been normal although some EEGs have shown "
        "a probable left occipital lobe focus."
    )
    assert attrs["MRI"]["MRI_Results"] == "Normal"
    assert attrs["EEG"]["EEG_Results"] == "Abnormal"


def test_pnes_confirmed_on_eeg_is_normal() -> None:
    attrs = _by_modality(
        "She has been diagnosed with non epileptic psychogenic seizures "
        "which is confirmed on EEG."
    )
    assert attrs["EEG"]["EEG_Results"] == "Normal"

