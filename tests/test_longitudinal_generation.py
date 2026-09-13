"""Generation provenance must survive failures, review and exact replay.

Admission: one new vertical slice protects provisional-reference provenance and
cutoff integrity; provider/source-policy corruption must fail before capture.
"""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.longitudinal.generate_seed_free_batch import (
    capture_stage,
    case_hashes,
    regenerate,
    review_stage,
    validate_config,
)
from scripts.longitudinal.verify_patient_case import expected_requests


def fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    config = {
        "version": "test",
        "mode": "seed_free_authoring",
        "provider_enabled": False,
        "source_conditioned_generation": False,
        "source_records": [],
        "additional_paid_call_cap_gbp": 0,
        "per_patient_paid_call_cap_gbp": 0,
        "automatic_retries": 0,
        "inspection_policy": "development_only",
        "stage_patient_counts": [1, 2],
        "pinned_sha256": {},
        "patients": [
            {"patient_id": f"probe-{i}", "style": "concise", "scenario": "missing"} for i in (1, 2)
        ],
        "author": {"identity": "fixture", "model": None},
    }
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps(config))
    sources = tmp_path / "sources"
    sources.mkdir()
    for i in (1, 2):
        source = {
            "patient_id": f"probe-{i}",
            "revision": 1,
            "age_at_first_visit": 40,
            "origin": "fictional_seed_free",
            "source_records": [],
            "lineage": ["fixture"],
            "history": {"intended": "No clinical statements"},
            "documentation_plan": {"style": "concise", "omissions": "All clinical facts"},
            "documents": [
                {
                    "letter_id": f"L{j}",
                    "visit_date": d,
                    "available_date": d,
                    "text": "Fictional outpatient administrative letter.\n",
                }
                for j, d in enumerate(("2025-01-01", "2025-06-30", "2025-12-27"), 1)
            ],
            "first_index": "2025-01-01",
            "annotations": {"assertions": [], "links": []},
            "reference": {
                "evidence": [],
                "links": [],
                "answers": [
                    {
                        "request_id": r["request_id"],
                        "status": "indeterminate",
                        "evidence_ids": [],
                        "reason": "No clinical information is documented.",
                    }
                    for r in expected_requests("2025-01-01")
                ],
            },
            "no_assertion_letters": {f"L{j}": "Administrative text only." for j in (1, 2, 3)},
        }
        (sources / f"probe-{i}.json").write_text(json.dumps(source))
    return cfg, sources, tmp_path / "run"


def test_capture_review_resume_and_replay_preserve_provenance(tmp_path: Path) -> None:
    cfg, sources, run = fixture(tmp_path)
    with pytest.raises(ValueError, match="previous stage"):
        capture_stage(cfg, run, sources, 2)
    result = capture_stage(cfg, run, sources, 1)
    assert result["patients"][0]["status"] == "checked"
    before = case_hashes(run)
    assert capture_stage(cfg, run, sources, 1) == result
    assert case_hashes(run) == before
    with pytest.raises(ValueError, match="review"):
        capture_stage(cfg, run, sources, 2)
    patient = result["patients"][0]
    review = {
        "reviewer": "test author",
        "independent": False,
        "patients": [
            {
                "patient_id": "probe-1",
                "case_sha256": patient["case_sha256"],
                "qc_sha256": patient["qc_sha256"],
                "disposition": "accepted",
                "reason": "All absent clinical information remains unknown.",
                "items": [
                    {
                        "item_id": item,
                        "disposition": "uncertainty_preserved",
                        "reason": "Administrative letters cannot settle this query.",
                    }
                    for item in patient["review_items"]
                ],
            }
        ],
    }
    with pytest.raises(ValueError, match="coverage"):
        review_stage(run, 1, {**review, "patients": []})
    review_stage(run, 1, review)
    clean = tmp_path / "replay"
    replay = regenerate(run, clean)
    assert replay["byte_identical"] and replay["accepted_patients"] == 1
    raw = sources / "probe-1.json"
    raw.write_text(raw.read_text().replace("administrative", "changed"))
    with pytest.raises(ValueError, match="changed"):
        capture_stage(cfg, run, sources, 1)
    # A review cannot authorize expansion after accepted output was altered.
    final = run / patient["attempt_path"] / "case/letters/L1.txt"
    final.write_text("tampered")
    with pytest.raises(ValueError, match="hash|changed"):
        capture_stage(cfg, run, sources, 2)


def test_failed_capture_retains_raw_and_requires_explicit_new_attempt(tmp_path: Path) -> None:
    cfg, sources, run = fixture(tmp_path)
    raw = sources / "probe-1.json"
    valid = raw.read_text()
    raw.write_text("{broken")
    result = capture_stage(cfg, run, sources, 1)
    assert result["patients"][0]["status"] == "failed"
    captured = run / result["patients"][0]["attempt_path"] / "raw.json"
    assert captured.read_text() == "{broken"
    raw.write_text(valid)
    with pytest.raises(ValueError, match="retry"):
        capture_stage(cfg, run, sources, 1)
    result = capture_stage(cfg, run, sources, 1, retry={"probe-1"})
    assert result["patients"][0]["status"] == "checked"
    assert captured.read_text() == "{broken"
    assert len(list((run / "patients/probe-1").glob("attempt-*"))) == 2
    # Simulate termination after raw capture but before its completion record.
    interrupted = run / result["patients"][0]["attempt_path"]
    (interrupted / "record.json").unlink()
    with pytest.raises(ValueError, match="Interrupted"):
        capture_stage(cfg, run, sources, 1)
    recovered = capture_stage(cfg, run, sources, 1, retry={"probe-1"})
    assert recovered["patients"][0]["status"] == "checked"
    assert (interrupted / "raw.json").read_text() == valid
    assert json.loads((interrupted / "record.json").read_text())["status"] == "failed"


def test_generation_refuses_unfunded_calls_and_source_or_pin_drift(tmp_path: Path) -> None:
    cfg, _, _ = fixture(tmp_path)
    config = json.loads(cfg.read_text())
    validate_config(config)
    for key, value in {
        "provider_enabled": True,
        "source_records": ["private"],
        "additional_paid_call_cap_gbp": 1,
        "automatic_retries": 1,
    }.items():
        changed = deepcopy(config)
        changed[key] = value
        with pytest.raises(ValueError):
            validate_config(changed)
    config["pinned_sha256"] = {"docs/longitudinal/annotation.schema.json": "wrong"}
    with pytest.raises(ValueError, match="pin"):
        validate_config(config)
