from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    investigations_rule_ablation as ablation,
)


def test_investigations_rule_ablation_scores_variants_and_counts_actions() -> None:
    direct_rows = [
        _row("EA1", [_mention("MRI", {"MRI_Performed": "Yes", "MRI_Results": "Normal"})]),
        _row("EA2", [_mention("MRI", {"MRI_Performed": "No"})]),
    ]
    verifier_rows = [
        _row("EA1", [_mention("MRI", {"MRI_Performed": "Yes", "MRI_Results": "Normal"})]),
        _row("EA2", [_mention("MRI", {"MRI_Performed": "Yes", "MRI_Results": "Normal"})]),
    ]

    payload = ablation.build_investigations_rule_ablation_payload(
        direct_rows,
        verifier_rows,
        generated_on="2026-06-25",
    )

    variants = {row["variant_id"]: row for row in payload["variants"]}
    assert variants["structured_direct_result_lens"]["metrics"]["f1"] == 0.5
    assert variants["verifier_only"]["metrics"]["f1"] == 1.0
    assert variants["verifier_plus_pending_suppression"]["action_counts"] == {}
    assert variants["selective_verifier_pending_suppression"]["selective_call_burden"] == 0.5
    assert variants["selective_verifier_pending_suppression"]["routed_letters"] == 1
    assert payload["decision"]["selected_next_architecture"] == (
        "selective_investigations_adjudicator_diagnostic"
    )


def test_selective_policy_routes_ambiguous_direct_rows_to_arbitrated_verifier() -> None:
    direct_rows = [
        _row(
            "EA1",
            [
                _mention(
                    "MRI",
                    {"MRI_Performed": "No", "MRI_Results": "Unknown"},
                    evidence="I will arrange MRI",
                )
            ],
        ),
        _row("EA2", [_mention("CT", {"CT_Performed": "Yes", "CT_Results": "Normal"})]),
    ]
    arbitrated_verifier_rows = [
        _row("EA1", [_mention("MRI", {"MRI_Performed": "Yes", "MRI_Results": "Normal"})]),
        _row("EA2", [_mention("CT", {"CT_Performed": "Yes", "CT_Results": "Normal"})]),
    ]

    selective, routed = ablation.selective_verifier_rows(
        direct_rows,
        arbitrated_verifier_rows,
    )

    assert routed == 1
    assert selective[0]["predicted_mentions"][0]["attributes"]["MRI_Performed"] == "Yes"
    assert selective[1]["predicted_mentions"][0]["attributes"]["CT_Performed"] == "Yes"


def _row(letter_id: str, mentions: list[dict[str, object]]) -> dict[str, object]:
    gold = [_mention("MRI", {"MRI_Performed": "Yes", "MRI_Results": "Normal"})]
    return {
        "letter_id": letter_id,
        "split": "toy",
        "pipeline_family": "toy",
        "prompt_version": "toy",
        "model": "none",
        "mode": "no-call",
        "call_error": None,
        "parse_errors": [],
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(mentions),
        "n_evidence_invalid": 0,
        "predicted_mentions": mentions,
        "gold_mentions": gold,
    }


def _mention(
    text: str,
    attributes: dict[str, str],
    *,
    evidence: str | None = None,
) -> dict[str, object]:
    return {
        "entity": "Investigations",
        "text": text,
        "attributes": attributes,
        "evidence": evidence or f"{text} was normal",
        "confidence": "high",
        "rationale": "",
    }
