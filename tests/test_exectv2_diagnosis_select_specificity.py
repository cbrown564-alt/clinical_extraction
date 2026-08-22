"""Select-authority Diagnosis specificity uses a portable hierarchy."""

from __future__ import annotations

from clinical_extraction.paper.rule_records import RULE_BY_NAME
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    DIAGNOSIS_PARENT,
)


def test_specificity_rule_is_select_rewrite() -> None:
    row = RULE_BY_NAME["selection.diagnosis_specificity_hierarchy"]
    assert row.task == "exectv2"
    assert row.runs_at == "llm_select"
    assert row.authority == "rewrite"
    assert "clinical_epilepsy" in row.notes


def test_diagnosis_hierarchy_states_lobe_and_laterality_parents() -> None:
    assert DIAGNOSIS_PARENT["temporal lobe epilepsy"] == "focal epilepsy"
    assert DIAGNOSIS_PARENT["frontal lobe epilepsy"] == "focal epilepsy"
    assert DIAGNOSIS_PARENT["parietal lobe epilepsy"] == "focal epilepsy"
    assert DIAGNOSIS_PARENT["occipital lobe epilepsy"] == "focal epilepsy"
    assert DIAGNOSIS_PARENT["symptomatic structural focal epilepsy"] == "focal epilepsy"
    assert DIAGNOSIS_PARENT["focal epilepsy"] == "epilepsy"
    assert DIAGNOSIS_PARENT["generalised epilepsy"] == "epilepsy"


def test_probable_temporal_modifier_overwrites_focal_and_etiology_forms() -> None:
    assert (
        sd.diagnosis_select_specificity_target(
            "focal epilepsy",
            "Diagnosis: focal epilepsy-Probable temporal",
        )
        == "temporal lobe epilepsy"
    )
    assert (
        sd.diagnosis_select_specificity_target(
            "focal epilepsy",
            "Diagnosis: focal epilepsy, probable temporal",
        )
        == "temporal lobe epilepsy"
    )
    assert (
        sd.diagnosis_select_specificity_target(
            "epilepsy",
            "Impression: probable temporal lobe epilepsy",
        )
        == "temporal lobe epilepsy"
    )
    assert (
        sd.diagnosis_select_specificity_target(
            "symptomatic structural focal epilepsy",
            "He has symptomatic structural temporal lobe epilepsy.",
        )
        == "temporal lobe epilepsy"
    )


def test_probable_lobe_onset_may_overwrite_focal_epilepsy() -> None:
    assert (
        sd.diagnosis_select_specificity_target(
            "focal epilepsy",
            "Diagnosis: focal epilepsy, probable parietal onset",
        )
        == "parietal lobe epilepsy"
    )


def test_possible_or_query_onset_does_not_overwrite_to_a_lobe_syndrome() -> None:
    assert (
        sd.diagnosis_select_specificity_target(
            "focal epilepsy",
            "Focal epilepsy ? right temporal lobe onset",
        )
        is None
    )
    assert (
        sd.diagnosis_select_specificity_target(
            "focal epilepsy",
            "possible temporal lobe epilepsy",
        )
        is None
    )


def test_laterality_may_upgrade_generic_epilepsy_at_possible() -> None:
    assert (
        sd.diagnosis_select_specificity_target(
            "epilepsy",
            "Diagnosis: epilepsy – possibly generalised",
        )
        == "generalised epilepsy"
    )
    assert (
        sd.diagnosis_select_specificity_target(
            "epilepsy",
            "Diagnosis: epilepsy, probable focal onset",
        )
        == "focal epilepsy"
    )


def test_hierarchy_blocks_cross_branch_and_sibling_overwrite() -> None:
    assert (
        sd.diagnosis_select_specificity_target(
            "generalised epilepsy",
            "Diagnosis: generalised epilepsy and symptomatic structural temporal "
            "lobe epilepsy",
        )
        is None
    )
    assert (
        sd.diagnosis_select_specificity_target(
            "temporal lobe epilepsy",
            "temporal lobe epilepsy, also called focal epilepsy",
        )
        is None
    )
    assert (
        sd.diagnosis_select_specificity_target(
            "juvenile myoclonic epilepsy",
            "juvenile myoclonic epilepsy / generalised epilepsy",
        )
        is None
    )


def test_convention_select_path_uses_the_hierarchy() -> None:
    assert (
        sd.diagnosis_convention_target(
            "focal epilepsy",
            "Diagnosis: focal epilepsy - probable temporal",
        )
        == "temporal lobe epilepsy"
    )
    assert (
        sd.diagnosis_format_target(
            "focal epilepsy",
            "Diagnosis: focal epilepsy - probable temporal",
        )
        is None
    )
