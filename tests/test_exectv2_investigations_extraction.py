"""Exemplars for rules-only Investigations extraction.

Keep one case each for result binding, planned-test drop, anaphora,
sibling modalities, and the landed PNES-EEG confirmation.
"""

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


def test_planned_test_is_dropped() -> None:
    attrs = _by_modality("I will arrange an MRI scan of his brain as well as an ECG.")
    assert attrs == {}


def test_next_sentence_anaphora_binds_finding() -> None:
    attrs = _by_modality(
        "He had an MRI brain performed in 2016. "
        "This does show some left-sided white matter changes."
    )
    assert attrs["MRI"]["MRI_Results"] == "Abnormal"
    assert len(attrs) == 1


def test_sibling_modalities_keep_their_own_results() -> None:
    attrs = _by_modality(
        "As you know she has had a normal MRI scan last year and previously "
        "has had an abnormal EEG with some generalised spike and wave abnormalities."
    )
    assert attrs["MRI"]["MRI_Results"] == "Normal"
    assert attrs["EEG"]["EEG_Results"] == "Abnormal"


def test_pnes_confirmed_on_eeg_is_normal() -> None:
    attrs = _by_modality(
        "She has been diagnosed with non epileptic psychogenic seizures "
        "which is confirmed on EEG."
    )
    assert attrs["EEG"]["EEG_Results"] == "Normal"
