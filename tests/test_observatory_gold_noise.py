"""Tests for the read-only ``/gold-noise`` Observatory router.

Mirrors ``test_observatory_api.py::test_gold_audit_endpoints``'s ``tmp_path``
fixture style. The router reads the four ``gold_case_ledger_*.jsonl`` files, the
Gan RQ10 ambiguity-audit JSON, ``gold_data_issues.jsonl`` and the hypothesis
registry directly as JSONL/JSON (the same raw-parse pattern the gold-audit
store uses) rather than importing the ``exectv2_ledger`` package, which is not
installed -- it is only a script namespace under ``experiments/``.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from clinical_extraction.observatory.api import create_app


def _gold_case_row(
    *,
    row_id: str,
    family: str,
    letter_id: str,
    disagreement_type: str,
    match_key: str,
    mechanism: str,
    verdict: str,
    reason: str = "",
    run_id: str = "exectv2_test_run_20260628",
    source_letter_text: str = "Current seizures occur twice per month.",
    gold: dict | None = None,
    pred: dict | None = None,
) -> dict:
    return {
        "row_id": row_id,
        "family": family,
        "run_id": run_id,
        "letter_id": letter_id,
        "disagreement_type": disagreement_type,
        "match_key": match_key,
        "source_letter_text": source_letter_text,
        "gold": gold,
        "pred": pred,
        "mechanism": mechanism,
        "verdict": verdict,
        "provenance": {
            "adjudicated_by": "test fixture",
            "adjudicated_at": "2026-06-30",
            "hypothesis_id": None,
            "reason": reason,
        },
    }


def _write_gold_case_ledger(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _build_client(
    repo_root: Path,
    *,
    ledgers: dict[str, list[dict]] | None = None,
    gan_audit: dict | None = None,
    issues: list[dict] | None = None,
    hypotheses: list[dict] | None = None,
) -> TestClient:
    experiments = repo_root / "experiments"
    experiments.mkdir(parents=True, exist_ok=True)

    family_to_file = {
        "diagnosis": "gold_case_ledger_diagnosis.jsonl",
        "seizurefrequency": "gold_case_ledger_seizurefrequency.jsonl",
        "prescription": "gold_case_ledger_prescription.jsonl",
        "investigations": "gold_case_ledger_investigations.jsonl",
    }
    for family_key, filename in family_to_file.items():
        rows = (ledgers or {}).get(family_key, [])
        _write_gold_case_ledger(experiments / filename, rows)

    if gan_audit is not None:
        (experiments / "gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.json").write_text(
            json.dumps(gan_audit, ensure_ascii=False, sort_keys=True), encoding="utf-8"
        )
    if issues is not None:
        (experiments / "gold_data_issues.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in issues)
            + ("\n" if issues else ""),
            encoding="utf-8",
        )
    if hypotheses is not None:
        (experiments / "hypothesis_registry.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in hypotheses)
            + ("\n" if hypotheses else ""),
            encoding="utf-8",
        )

    return TestClient(
        create_app(
            repo_root=repo_root,
            registry_path=repo_root / "missing_registry.jsonl",
            experiments_dir=experiments,
        )
    )


def _ledgers_with_known_ceiling() -> dict[str, list[dict]]:
    """A 2-row SeizureFrequency ledger with 1 gold_right (ceiling 1/2 = 50%)."""
    return {
        "seizurefrequency": [
            _gold_case_row(
                row_id="SF:EA0001:missed:focal epilepsy",
                family="SeizureFrequency",
                letter_id="EA0001",
                disagreement_type="missed",
                match_key="focal epilepsy",
                mechanism="genuine_model_error",
                verdict="gold_right",
                reason="Model missed the explicit 'focal epilepsy' diagnosis.",
                gold={
                    "raw_text": "focal epilepsy",
                    "normalized_text": "focal epilepsy",
                    "attributes": {},
                },
                pred=None,
            ),
            _gold_case_row(
                row_id="SF:EA0002:spurious:cluster count",
                family="SeizureFrequency",
                letter_id="EA0002",
                disagreement_type="spurious",
                match_key="multiple per month",
                mechanism="gold_multiplicity_consolidation",
                verdict="model_defensible",
                reason="Gold tags the cluster twice; model's single consolidation is defensible.",
                gold=None,
                pred={
                    "raw_text": "multiple per month",
                    "normalized_text": "multiple per month",
                    "attributes": {},
                },
            ),
        ],
        "diagnosis": [
            _gold_case_row(
                row_id="Dx:EA0003:spurious:awareness",
                family="Diagnosis",
                letter_id="EA0003",
                disagreement_type="spurious",
                match_key="change in awareness",
                mechanism="gold_multiplicity_consolidation",
                verdict="both_defensible",
                reason="Granularity coin-flip.",
            )
        ],
    }


# ── /gold-noise/ledgers ──


def test_ledgers_derive_ceiling_from_verdict(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers=_ledgers_with_known_ceiling())

    r = client.get("/gold-noise/ledgers")
    assert r.status_code == 200
    payload = r.json()

    families = {fam["family"]: fam for fam in payload["families"]}
    assert families["SeizureFrequency"]["total"] == 2
    # ceiling = gold_right / total, derived live from the verdict field
    assert families["SeizureFrequency"]["gold_right"] == 1
    assert families["SeizureFrequency"]["model_defensible"] == 1
    assert families["SeizureFrequency"]["both_defensible"] == 0
    assert families["Diagnosis"]["total"] == 1
    assert families["Diagnosis"]["both_defensible"] == 1


def test_ledgers_include_mechanism_and_verdict_breakdowns(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers=_ledgers_with_known_ceiling())

    payload = client.get("/gold-noise/ledgers").json()
    sf = {fam["family"]: fam for fam in payload["families"]}["SeizureFrequency"]
    assert sf["by_mechanism"] == {"genuine_model_error": 1, "gold_multiplicity_consolidation": 1}
    assert sf["by_verdict"] == {"gold_right": 1, "model_defensible": 1}


def test_ledgers_rows_are_normalized_to_gold_noise_item(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers=_ledgers_with_known_ceiling())

    payload = client.get("/gold-noise/ledgers").json()
    sf_rows = {fam["family"]: fam for fam in payload["families"]}["SeizureFrequency"]["rows"]
    assert len(sf_rows) == 2
    item = sf_rows[0]
    # unified GoldNoiseItem shape
    for key in (
        "family",
        "letter_id",
        "row_id",
        "disagreement_type",
        "match_key",
        "mechanism",
        "verdict",
        "gold",
        "pred",
        "reason",
        "run_id",
        "source",
    ):
        assert key in item, f"missing {key}"
    assert item["family"] == "SeizureFrequency"
    assert item["source"] == "exectv2_gold_case_ledger"
    assert item["reason"] == "Model missed the explicit 'focal epilepsy' diagnosis."
    assert item["gold"]["normalized_text"] == "focal epilepsy"
    assert item["pred"] is None


# ── /gold-noise/gan-audit ──


def test_gan_audit_serves_json_verbatim(tmp_path: Path) -> None:
    gan_audit = {
        "artifact_kind": "gan2026_rq10_gold_scorer_ambiguity_audit",
        "metrics": {"hard_row_ambiguity_rate": 0.6415, "all_system_fail_rows": 46},
        "primary_class_counts": {
            "benchmark_convention_dominated": 11,
            "true_extraction_failure": 19,
            "underdetermined_note": 23,
        },
        "by_hidden_family": {
            "competing_semiologies": {"rows": 25, "main_primary_class": "underdetermined_note"},
        },
        "split": "validation",
        "date": "2026-06-04",
        "claim_language": "Development-control answer; no scorer claim.",
    }
    client = _build_client(tmp_path, ledgers={}, gan_audit=gan_audit)

    r = client.get("/gold-noise/gan-audit")
    assert r.status_code == 200
    payload = r.json()
    # echoes the audit + labels its distinct taxonomy so the UI never mixes it
    assert payload["audit"]["primary_class_counts"] == gan_audit["primary_class_counts"]
    assert payload["taxonomy"] == "rq10_class"
    assert payload["taxonomy_note"].startswith("Gan RQ10")


def test_gan_audit_missing_returns_empty_not_500(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers={})
    r = client.get("/gold-noise/gan-audit")
    assert r.status_code == 200
    assert r.json()["audit"] is None


# ── /gold-noise/issues ──


def test_issues_serves_gold_data_issues(tmp_path: Path) -> None:
    issue = {
        "letter_id": "EA0146",
        "entity": "Prescription",
        "field": "DrugName",
        "gold_value": "Perampanel",
        "conflicting_evidence": "Span text is a brivaracetam typo.",
        "resolution_status": "open",
        "date": "2026-07-02",
        "notes": "Frozen corpus NOT edited.",
    }
    client = _build_client(tmp_path, ledgers={}, issues=[issue])

    r = client.get("/gold-noise/issues")
    assert r.status_code == 200
    payload = r.json()
    assert payload["count"] == 1
    assert payload["issues"][0]["letter_id"] == "EA0146"


def test_issues_missing_returns_empty(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers={})
    r = client.get("/gold-noise/issues")
    assert r.status_code == 200
    assert r.json() == {"count": 0, "issues": []}


# ── /gold-noise/row ──


def test_row_returns_single_normalized_item(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers=_ledgers_with_known_ceiling())

    r = client.get(
        "/gold-noise/row",
        params={"family": "SeizureFrequency", "row_id": "SF:EA0001:missed:focal epilepsy"},
    )
    assert r.status_code == 200
    item = r.json()
    assert item["row_id"] == "SF:EA0001:missed:focal epilepsy"
    assert item["mechanism"] == "genuine_model_error"
    assert item["verdict"] == "gold_right"
    assert item["letter_id"] == "EA0001"


def test_row_unknown_returns_404(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers=_ledgers_with_known_ceiling())
    r = client.get(
        "/gold-noise/row",
        params={"family": "SeizureFrequency", "row_id": "does:not:exist"},
    )
    assert r.status_code == 404


# ── /gold-noise/hypotheses ──


def test_hypotheses_grouped_by_family(tmp_path: Path) -> None:
    hypotheses = [
        {
            "hypothesis_id": "sf_direction_gap_2026-06-28",
            "family": "SeizureFrequency",
            "statement": "The SF direction gap is fundamental.",
            "predeclaration_doc": "docs/plans/x.md",
            "kill_criterion": "recovery >= +0.05 dev140",
            "verdict": "CONFIRMED",
            "date": "2026-06-28",
            "owner": "ExECTv2",
        },
        {
            "hypothesis_id": "duplicate_letters_2026-07-01",
            "family": "cross_family",
            "statement": "4 duplicate pairs are a data bug.",
            "predeclaration_doc": "docs/plans/y.md",
            "kill_criterion": "n/a",
            "verdict": "REFUTED",
            "date": "2026-07-01",
            "owner": "ExECTv2",
        },
    ]
    client = _build_client(tmp_path, ledgers={}, hypotheses=hypotheses)

    r = client.get("/gold-noise/hypotheses")
    assert r.status_code == 200
    payload = r.json()
    by_family = payload["by_family"]
    assert by_family["SeizureFrequency"][0]["hypothesis_id"] == "sf_direction_gap_2026-06-28"
    assert by_family["cross_family"][0]["verdict"] == "REFUTED"
    assert payload["count"] == 2


def test_hypotheses_missing_returns_empty(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers={})
    r = client.get("/gold-noise/hypotheses")
    assert r.status_code == 200
    payload = r.json()
    assert payload == {"count": 0, "by_family": {}, "entries": []}


# ── all-ledgers-missing resilience ──


def test_ledgers_empty_when_no_files(tmp_path: Path) -> None:
    client = _build_client(tmp_path, ledgers={})
    r = client.get("/gold-noise/ledgers")
    assert r.status_code == 200
    # four families always present, each with zero rows
    families = {fam["family"]: fam for fam in r.json()["families"]}
    assert set(families) == {"Diagnosis", "SeizureFrequency", "Prescription", "Investigations"}
    assert all(fam["total"] == 0 for fam in families.values())
