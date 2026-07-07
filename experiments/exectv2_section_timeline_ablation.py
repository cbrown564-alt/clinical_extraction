"""Phase C: Section/Timeline Agent ablation pilot (SeizureFrequency, Investigations).

See docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md and
docs/research/supervisor_brief_conformance_audit_2026-07-01.md.

Design: the "without timeline" arm reuses the frozen v08 dev140 baseline
lane files directly (zero new calls); only the "with timeline" arm issues
new live gpt-4.1-mini calls, re-running the SF and Investigations LLM
stages with an optional `timeline_context` prompt field, then replaying the
same deterministic downstream chain (SF: state-projection -> unknown-
suppression -> union-arbitration; Investigations: arbitration) that the
frozen baseline already went through. Both arms are then scored through the
same `build_finding_assembly` manifest machinery used to produce the v08
dev140 headline numbers, so the delta is apples-to-apples.

Stages, run via --stage:
  smoke  - zero LLM cost. Prints rendered timeline context for 8 sample
           dev letters, then verifies the score_variant() path reproduces
           the known frozen v08 dev140 baseline (SF 0.9053, Investigations
           0.9132) using ONLY the existing frozen artifacts.
  live   - real $ cost (~280 gpt-4.1-mini calls). Requires
           --confirm-live-spend. Runs the "with timeline" arm fresh and
           writes a baseline-vs-with-timeline result JSON.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    load_finding_assembly_manifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection as sf_projection,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_unknown_suppression as sf_suppression,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.section_timeline import (
    build_timeline,
    render_context_block,
    segment_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_arbitration as inv_arbitration,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_verifier as inv_verifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_state_adjudicator as sf_adjudicator,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_union_arbitration as sf_union,
)

MODEL = "openai/gpt-4.1-mini"
SPLIT = "dev"

BASE_MANIFEST_PATH = Path(
    "configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml"
)
SF_BASELINE_PRODUCER_ID = "sf_union_arbitration_v08"
INV_BASELINE_PRODUCER_ID = "investigations_arbitration_v02"
SF_BASELINE_JSONL = Path(
    "experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl"
)
INV_BASELINE_JSONL = Path(
    "experiments/exectv2_llm_investigations_arbitration_v02_dev140_20260621.jsonl"
)

OUT_DIR = Path("experiments")
RUN_TAG = "exectv2_section_timeline_ablation_dev140"


def load_baseline_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def timeline_context_for_letters(letters: list[ExectLetter]) -> dict[str, str]:
    """Precompute the rendered timeline/section context block per letter."""
    out: dict[str, str] = {}
    for letter in letters:
        sections = segment_letter(letter.note_text)
        timeline = build_timeline(letter.note_text)
        block = render_context_block(sections, timeline)
        if block:
            out[letter.letter_id] = block
    return out


def draft_rows_from_baseline(rows: list[dict[str, Any]], entity_name: str) -> list[dict[str, Any]]:
    """Reconstruct predicted_mentions-shaped draft_rows from a frozen lane
    file's own `draft_mentions` field, so `draft_mentions_by_letter`
    recovers the exact same drafts that fed the original v08 baseline
    call. See draft_io.py::draft_mentions_by_letter / _draft_mention_row.
    """
    return [
        {
            "letter_id": row["letter_id"],
            "predicted_mentions": [
                {**mention, "entity": entity_name} for mention in row.get("draft_mentions", [])
            ],
        }
        for row in rows
    ]


def _assert_draft_reconstruction_is_faithful(
    baseline_rows: list[dict[str, Any]],
    draft_rows: list[dict[str, Any]],
    config_module: Any,
    entity_name: str,
) -> None:
    """Zero-cost sanity check: draft_mentions_by_letter(draft_rows) must
    recover exactly the same drafts as the frozen row's own
    `draft_mentions` field, or the ablation would not be apples-to-apples.
    """
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.draft_io import (
        draft_mentions_by_letter,
    )

    reconstructed = draft_mentions_by_letter(draft_rows, config_module)
    for row in baseline_rows:
        letter_id = row["letter_id"]
        original = row.get("draft_mentions", [])
        got = reconstructed.get(letter_id, [])
        # Compare on the fields _draft_mention_row keeps (text/attributes/
        # evidence/confidence/rationale); "entity" was synthetically added
        # above and is not part of the original draft_mentions shape.
        stripped_got = [{k: v for k, v in m.items() if k != "entity"} for m in got]
        if stripped_got != original:
            raise AssertionError(
                f"draft reconstruction mismatch for {entity_name} letter {letter_id}: "
                f"{stripped_got!r} != {original!r}"
            )


def smoke_test(letters: list[ExectLetter], n: int = 8) -> None:
    print(f"Rendering timeline context for {n} sample dev letters (zero LLM cost):")
    for letter in letters[:n]:
        sections = segment_letter(letter.note_text)
        timeline = build_timeline(letter.note_text)
        block = render_context_block(sections, timeline)
        print("=" * 70)
        print(letter.letter_id)
        print(block or "(empty context block)")

    print("\nVerifying score_variant() reproduces the known frozen v08 dev140 baseline...")
    baseline_scores = score_variant(SF_BASELINE_JSONL, INV_BASELINE_JSONL)
    print("baseline scores:", baseline_scores)
    expected = {"SeizureFrequency": 0.9053, "Investigations": 0.9132}
    for entity, expected_f1 in expected.items():
        got = baseline_scores[entity]
        if abs(got - expected_f1) > 1e-4:
            raise AssertionError(
                f"scoring path did not reproduce known v08 baseline for {entity}: "
                f"got {got}, expected {expected_f1}"
            )
    print("OK: scoring path reproduces the known v08 dev140 baseline exactly.")

    print("\nVerifying draft-row reconstruction is faithful (zero LLM cost)...")
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_sf_verifier as sf_verifier_config_module,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier import (
        investigations as inv_config_module,
    )

    sf_baseline_rows = load_baseline_rows(SF_BASELINE_JSONL)
    sf_draft_rows = draft_rows_from_baseline(sf_baseline_rows, SEIZURE_FREQUENCY.name)
    _assert_draft_reconstruction_is_faithful(
        sf_baseline_rows, sf_draft_rows, sf_verifier_config_module.CONFIG, SEIZURE_FREQUENCY.name
    )
    print("OK: SF draft reconstruction is faithful.")

    inv_baseline_rows = load_baseline_rows(INV_BASELINE_JSONL)
    inv_draft_rows = draft_rows_from_baseline(inv_baseline_rows, INVESTIGATIONS.name)
    _assert_draft_reconstruction_is_faithful(
        inv_baseline_rows, inv_draft_rows, inv_config_module.CONFIG, INVESTIGATIONS.name
    )
    print("OK: Investigations draft reconstruction is faithful.")
    print("\nSmoke test passed. Safe to proceed to --stage live with --confirm-live-spend.")


def run_sf_with_timeline(letters: list[ExectLetter], timeline_by_letter: dict[str, str]) -> Path:
    baseline_rows = load_baseline_rows(SF_BASELINE_JSONL)
    draft_rows = draft_rows_from_baseline(baseline_rows, SEIZURE_FREQUENCY.name)

    adjudicator_jsonl = OUT_DIR / f"{RUN_TAG}_sf_adjudicator_with_timeline.jsonl"
    sf_adjudicator.run_split(
        letters,
        draft_rows=draft_rows,
        split=SPLIT,
        model=MODEL,
        temperature=0.0,
        max_tokens=2600,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=adjudicator_jsonl,
        checkpoint_report_path=adjudicator_jsonl.with_suffix(".md"),
        resume=True,
        timeline_context_by_letter=timeline_by_letter,
    )

    projection_jsonl = OUT_DIR / f"{RUN_TAG}_sf_projection_with_timeline.jsonl"
    sf_projection.write_rows_and_report(
        sf_projection.read_rows(adjudicator_jsonl),
        ablation="combined",
        jsonl_path=projection_jsonl,
        report_path=projection_jsonl.with_suffix(".md"),
    )

    suppression_jsonl = OUT_DIR / f"{RUN_TAG}_sf_suppression_with_timeline.jsonl"
    sf_suppression.write_rows_and_report(
        sf_suppression.read_rows(projection_jsonl),
        jsonl_path=suppression_jsonl,
        report_path=suppression_jsonl.with_suffix(".md"),
    )

    union_jsonl = OUT_DIR / f"{RUN_TAG}_sf_union_with_timeline.jsonl"
    sf_union.write_rows_and_report(
        sf_union.read_rows(suppression_jsonl),
        sf_union.deterministic_rows_from_letters(letters, split=SPLIT),
        jsonl_path=union_jsonl,
        report_path=union_jsonl.with_suffix(".md"),
    )
    return union_jsonl


def run_inv_with_timeline(letters: list[ExectLetter], timeline_by_letter: dict[str, str]) -> Path:
    baseline_rows = load_baseline_rows(INV_BASELINE_JSONL)
    draft_rows = draft_rows_from_baseline(baseline_rows, INVESTIGATIONS.name)

    verifier_jsonl = OUT_DIR / f"{RUN_TAG}_inv_verifier_with_timeline.jsonl"
    inv_verifier.run_split(
        letters,
        draft_rows=draft_rows,
        split=SPLIT,
        model=MODEL,
        temperature=0.0,
        max_tokens=1800,
        mode="live",
        dspy_cache=True,
        progress_every=10,
        checkpoint_jsonl_path=verifier_jsonl,
        checkpoint_report_path=verifier_jsonl.with_suffix(".md"),
        resume=True,
        timeline_context_by_letter=timeline_by_letter,
    )

    arbitration_jsonl = OUT_DIR / f"{RUN_TAG}_inv_arbitration_with_timeline.jsonl"
    inv_arbitration.write_rows_and_report(
        inv_arbitration.read_rows(verifier_jsonl),
        jsonl_path=arbitration_jsonl,
        report_path=arbitration_jsonl.with_suffix(".md"),
    )
    return arbitration_jsonl


def score_variant(sf_producer_path: Path, inv_producer_path: Path) -> dict[str, float]:
    base_manifest = load_finding_assembly_manifest(BASE_MANIFEST_PATH)
    producers = dict(base_manifest.producers)
    producers[SF_BASELINE_PRODUCER_ID] = replace(
        producers[SF_BASELINE_PRODUCER_ID], artifact=sf_producer_path
    )
    producers[INV_BASELINE_PRODUCER_ID] = replace(
        producers[INV_BASELINE_PRODUCER_ID], artifact=inv_producer_path
    )
    manifest = replace(base_manifest, producers=producers)
    run = build_finding_assembly(manifest)
    by_indicator = run.report["score_ladder"]["headline_target"]["by_indicator"]
    return {
        "SeizureFrequency": by_indicator[SEIZURE_FREQUENCY.name]["f1"],
        "Investigations": by_indicator[INVESTIGATIONS.name]["f1"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["smoke", "live"], required=True)
    parser.add_argument(
        "--confirm-live-spend",
        action="store_true",
        help="Required for --stage live. Real $ cost: ~280 gpt-4.1-mini calls.",
    )
    args = parser.parse_args()

    letters = load_letters_for_split(SPLIT)[:140]

    if args.stage == "smoke":
        smoke_test(letters)
        return

    if not args.confirm_live_spend:
        raise SystemExit(
            "Refusing to run --stage live without --confirm-live-spend "
            "(real $ cost, ~280 gpt-4.1-mini calls: 140 letters x 2 families)."
        )

    timeline_by_letter = timeline_context_for_letters(letters)
    print(f"Timeline context computed for {len(timeline_by_letter)}/{len(letters)} letters.")

    print("Scoring baseline (without timeline, reused frozen v08 artifacts)...")
    baseline_scores = score_variant(SF_BASELINE_JSONL, INV_BASELINE_JSONL)
    print("baseline:", baseline_scores)

    print("Running SF stage with timeline context (live calls)...")
    sf_with_timeline_path = run_sf_with_timeline(letters, timeline_by_letter)

    print("Running Investigations stage with timeline context (live calls)...")
    inv_with_timeline_path = run_inv_with_timeline(letters, timeline_by_letter)

    print("Scoring with-timeline arm...")
    with_timeline_scores = score_variant(sf_with_timeline_path, inv_with_timeline_path)
    print("with_timeline:", with_timeline_scores)

    result = {
        "baseline": baseline_scores,
        "with_timeline": with_timeline_scores,
        "delta": {
            entity: with_timeline_scores[entity] - baseline_scores[entity]
            for entity in baseline_scores
        },
        "sf_with_timeline_artifact": str(sf_with_timeline_path),
        "inv_with_timeline_artifact": str(inv_with_timeline_path),
        "sf_baseline_artifact": str(SF_BASELINE_JSONL),
        "inv_baseline_artifact": str(INV_BASELINE_JSONL),
    }
    result_path = OUT_DIR / f"{RUN_TAG}_result.json"
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nResult written to {result_path}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
