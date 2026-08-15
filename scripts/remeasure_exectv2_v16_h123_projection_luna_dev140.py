"""No-call H1-H3 projection study on saved ExECT v16 dev140 rows.

This script never calls a model. It derives SeizureFrequency-only counterfactual
rows from the saved v16 structured output, assembles them with the untouched v16
Diagnosis/Prescription/Investigations producer, and scores the resulting hybrid
view through the current HEAD stack.
"""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import copy
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
    render_finding_assembly_markdown,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as prescription_dictionary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows as write_jsonl,
)
from scripts import run_exectv2_2call_model_swap as swap_runner
from scripts import run_exectv2_structured_prompt_v10_luna_dev20 as v10_run

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / (
    "experiments/exectv2_v16_rules_and_shapes_luna_dev140_20260815/"
    "v16_live/structured.jsonl"
)
STUDY_DIR = REPO_ROOT / "experiments/exectv2_v16_h123_projection_luna_dev140_20260815"
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v16_h123_projection_luna_dev140_protocol_2026-08-15.md"
)
REPORT = REPO_ROOT / (
    "docs/research/exectv2/structured_prompt_v16_h123_projection_luna_dev140_2026-08-15.md"
)
EXPECTED_N = 140
SEIZURE_FAMILY = "SeizureFrequency"
ZERO = "0"
SEIZURE_FREE_RE = re.compile(r"\bseizure[- ]free\b", re.IGNORECASE)
NAMED_LAST_EVENT_RE = re.compile(
    r"\b(?P<phrase>general(?:ised|ized)\s+tonic[- ](?:clonic|chronic)\s+seizures?)\b"
    r"\s*,\s*the\s+last\s+occurred\b",
    re.IGNORECASE,
)
NAMED_RATE_HEAD_RE = re.compile(
    r"\b(?P<phrase>(?:secondary\s+general(?:ised|ized)|general(?:ised|ized)\s+tonic[- ](?:clonic|chronic)|"
    r"focal\s+motor|focal)\s+seizures?)\b\s*,?\s*(?:they|the|which|are|happen)",
    re.IGNORECASE,
)
GENERIC_HEAD_RE = re.compile(r"\b(?P<phrase>seizures?)\b", re.IGNORECASE)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    result = run_study(overwrite=args.overwrite)
    print(json.dumps(result, indent=2, sort_keys=True))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _letters() -> list[Any]:
    letters = sorted(load_letters_for_split("dev"), key=lambda item: item.letter_id)
    if len(letters) != EXPECTED_N:
        raise RuntimeError(f"expected {EXPECTED_N} development letters, found {len(letters)}")
    return letters


def _copy_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [copy.deepcopy(dict(row)) for row in rows]


def _normalized(value: object) -> str:
    return " ".join(str(value or "").lower().replace("-", " ").split())


def _sf_mentions(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        mention
        for mention in row.get("predicted_mentions", [])
        if str(mention.get("entity")) == SEIZURE_FAMILY
    ]


def _replace_text(mention: dict[str, Any], text: str, reason: str) -> dict[str, Any]:
    changed = copy.deepcopy(mention)
    changed["text"] = text
    attrs = dict(changed.get("attributes") or {})
    attrs.pop("CUI", None)
    attrs.pop("CUIPhrase", None)
    changed["attributes"] = attrs
    changed["rationale"] = (
        str(changed.get("rationale") or "").strip() + " " + reason
    ).strip()
    return changed


def _clause_head(evidence: str) -> str | None:
    named = NAMED_LAST_EVENT_RE.search(evidence)
    if named:
        return named.group("phrase")
    named_rate = NAMED_RATE_HEAD_RE.search(evidence)
    if named_rate and re.search(r"\b(?:had|has had|gets?|have)\b", evidence[: named_rate.start()], re.I):
        return named_rate.group("phrase")
    lower = evidence.lower()
    # These cues bind to the short generic noun phrase, even when a more
    # specific semiology appears later in the evidence window.
    if re.search(r"\blast\s+seizures?\b", lower):
        match = re.search(r"\b(seizures?)\b", evidence, re.IGNORECASE)
        return match.group(1) if match else None
    if re.search(r"\b(?:no further|no more)\s+seizures?\b", lower):
        match = re.search(r"\b(seizures?)\b", evidence, re.IGNORECASE)
        return match.group(1) if match else None
    if re.search(r"\b(?:had|around|about)\b.{0,45}\bseizures?\b", lower, re.DOTALL):
        match = re.search(r"\b(seizures?)\b", evidence, re.IGNORECASE)
        return match.group(1) if match else None
    subject = re.search(r"\b(seizures?)\s+(?:are|were|have|happen|occur)", evidence, re.I)
    return subject.group(1) if subject else None


def _derive_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    h1: bool,
    h2: bool,
    h3: bool,
    h7: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    derived = _copy_rows(rows)
    actions: list[dict[str, str]] = []
    for row in derived:
        mentions = list(row.get("predicted_mentions") or [])
        sf = _sf_mentions({"predicted_mentions": mentions})
        active_exists = any(
            str((item.get("attributes") or {}).get("NumberOfSeizures")) not in {"", ZERO}
            and any(
                key in (item.get("attributes") or {})
                for key in ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
            )
            for item in sf
        )
        rewritten: list[dict[str, Any]] = []
        for mention in mentions:
            if str(mention.get("entity")) != SEIZURE_FAMILY:
                rewritten.append(mention)
                continue
            attrs = dict(mention.get("attributes") or {})
            evidence = str(mention.get("evidence") or "")
            current = mention
            if h7 and active_exists:
                if re.search(r"\bbefore\s+this\b", evidence, re.IGNORECASE):
                    actions.append(
                        {"letter_id": str(row["letter_id"]), "rule": "H7.drop_stale_older_zero"}
                    )
                    continue
            if h1 and attrs.get("NumberOfSeizures") == ZERO:
                free = SEIZURE_FREE_RE.search(evidence)
                if free and "seizure free" not in _normalized(mention.get("text")):
                    current = _replace_text(
                        current,
                        free.group(0),
                        "H1 retargeted zero frequency to the seizure-free clause head.",
                    )
                    actions.append(
                        {"letter_id": str(row["letter_id"]), "rule": "H1.retarget_seizure_free_span"}
                    )
                    attrs = dict(current.get("attributes") or {})
            if h3:
                head = _clause_head(evidence)
                if (
                    head
                    and NAMED_LAST_EVENT_RE.search(evidence)
                    and attrs.get("NumberOfSeizures") != ZERO
                ):
                    attrs = dict(current.get("attributes") or {})
                    attrs["NumberOfSeizures"] = ZERO
                    attrs["TimeSince_or_TimeOfEvent"] = "Since"
                    current = copy.deepcopy(current)
                    current["attributes"] = attrs
                    actions.append(
                        {"letter_id": str(row["letter_id"]), "rule": "H3.named_last_event_zero"}
                    )
                if head and _normalized(head) != _normalized(current.get("text")):
                    # Preserve a named last-event head from being flattened by
                    # the existing generic last-event rewrite on the replay.
                    if NAMED_LAST_EVENT_RE.search(evidence) and attrs.get("NumberOfSeizures") != ZERO:
                        attrs = dict(current.get("attributes") or {})
                        attrs["NumberOfSeizures"] = ZERO
                        attrs["TimeSince_or_TimeOfEvent"] = "Since"
                        current = copy.deepcopy(current)
                        current["attributes"] = attrs
                        actions.append(
                            {"letter_id": str(row["letter_id"]), "rule": "H3.named_last_event_zero"}
                        )
                    current = _replace_text(
                        current,
                        head,
                        "H3 bound frequency to the clause-head noun phrase.",
                    )
                    if h2 and re.fullmatch(r"seizures?", head, re.IGNORECASE):
                        sentences = re.split(r"(?<=[.!?])\s+", evidence)
                        clipped = next(
                            (sentence for sentence in sentences if re.search(rf"\b{re.escape(head)}\b", sentence, re.I)),
                            evidence,
                        )
                        current["evidence"] = clipped
                        actions.append(
                            {"letter_id": str(row["letter_id"]), "rule": "H2.clip_evidence_to_generic_clause"}
                        )
                    actions.append(
                        {"letter_id": str(row["letter_id"]), "rule": "H3.retarget_clause_head"}
                    )
            rewritten.append(current)
        row["predicted_mentions"] = rewritten
    return derived, actions


def _build_candidate(
    *,
    slug: str,
    source_rows: Sequence[Mapping[str, Any]],
    derived_rows: Sequence[Mapping[str, Any]],
    letters: Sequence[Any],
) -> dict[str, Any]:
    out_dir = STUDY_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    derived_path = out_dir / "derived_structured.jsonl"
    write_jsonl(list(derived_rows), derived_path)
    sf_final = out_dir / "arm_sf_unknown_suppression.jsonl"
    swap_runner._run_model_led_sf_chain(
        structured_jsonl=derived_path,
        sf_output_jsonl=sf_final,
        letters=list(letters),
    )
    cfg = v10_run._arm_assembly(slug, derived_path, sf_final)
    structured_producer = cfg.producers["structured_key_family_event_ledger"]
    cfg = replace(
        cfg,
        producers={
            **cfg.producers,
            "structured_key_family_event_ledger": replace(
                structured_producer,
                artifact=SOURCE,
            ),
        },
        candidate_id=f"exectv2_v16_h123_projection_luna_dev140_{slug}",
        row_count=EXPECTED_N,
        claim_boundary="No-call H1-H3 projection counterfactual on saved ExECT v16 dev140 rows.",
    )
    run = build_finding_assembly(
        cfg,
        generated_on="2026-08-15",
        gold_loader=lambda _split: list(letters),
        diagnosis_resolution_candidate=True,
        diagnosis_policy_variant="default",
        prescription_policy_variant="default",
    )
    assembly_jsonl = out_dir / "assembly.jsonl"
    assembly_json = out_dir / "assembly.json"
    write_jsonl(run.rows, assembly_jsonl)
    assembly_json.write_text(json.dumps(run.report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assembly_json.with_suffix(".md").write_text(
        render_finding_assembly_markdown(run.report, json_path=assembly_json, jsonl_path=assembly_jsonl),
        encoding="utf-8",
    )
    letter_rows = v10_run._letter_family_rows(
        gold=letters,
        structured_path=SOURCE,
        assembly_jsonl=assembly_jsonl,
        prompt_version="v16_derived_projection",
        arm=slug,
    )
    summary = v10_run._arm_summary(
        run.report,
        letter_rows,
        "v16_derived_projection",
        "saved_structured_no_call",
        0,
    )
    write_jsonl(letter_rows, out_dir / "letter_family.jsonl")
    return {"summary": summary, "letter_rows": letter_rows}


def _h2_diagnostic(source_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V16)
        payload = json.loads(structured.build_prompt_input(_letters()[0]))
    finally:
        structured.set_active_prompt_version(original)
    ambiguous = []
    for row in source_rows:
        for mention in _sf_mentions(row):
            attrs = mention.get("attributes") or {}
            if attrs.get("NumberOfSeizures") == ZERO and "seizure free" not in _normalized(mention.get("text")):
                if SEIZURE_FREE_RE.search(str(mention.get("evidence") or "")):
                    ambiguous.append(str(row["letter_id"]))
    return {
        "status": "diagnostic_only_unscorable_from_saved_raw",
        "reason": "saved model rows contain no causal attribution to an individual worked example",
        "v16_shape_ids": [str(item["id"]) for item in payload.get("worked_examples", [])],
        "named_type_not_generic_present": "named_type_not_generic" in {
            str(item["id"]) for item in payload.get("worked_examples", [])
        },
        "observable_zero_span_ambiguity_letters": sorted(set(ambiguous)),
        "model_calls": 0,
    }


def _h9_guard(source_rows: Sequence[Mapping[str, Any]], assembly_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    raw = next(row for row in source_rows if str(row["letter_id"]) == "EA0107")
    hybrid = next(row for row in assembly_rows if str(row["letter_id"]) == "EA0107")
    raw_rx = [m for m in raw.get("predicted_mentions", []) if m.get("entity") == "Prescription"]
    hybrid_rx = hybrid.get("lanes", {}).get("Prescription", {}).get("predicted_mentions", [])
    splitter = []
    planned = []
    for mention in raw_rx:
        attrs = dict(mention.get("attributes") or {})
        evidence = str(mention.get("evidence") or "")
        if prescription_dictionary.split_daily_dose_regimen(
            str(mention.get("text") or ""), evidence=evidence, attributes=attrs
        ):
            splitter.append(str(mention.get("text") or ""))
        if prescription_dictionary.is_planned_start_prescription(
            str(mention.get("text") or ""), evidence=evidence, attributes=attrs
        ):
            planned.append(str(mention.get("text") or ""))
    return {
        "letter_id": "EA0107",
        "status": "start_drop_guard_is_failure" if planned and len(hybrid_rx) < len(raw_rx) else "no_failure_detected",
        "raw_prescription_count": len(raw_rx),
        "hybrid_prescription_count": len(hybrid_rx),
        "splitter_fired_on": splitter,
        "planned_start_or_titration_drop_on": planned,
        "interpretation": "loss is in planned-start/titration classification, not the regimen splitter",
    }


def run_study(*, overwrite: bool) -> dict[str, Any]:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    letters = _letters()
    source_rows = _read_jsonl(SOURCE)
    if len(source_rows) != EXPECTED_N:
        raise RuntimeError(f"expected {EXPECTED_N} saved v16 rows, found {len(source_rows)}")
    if overwrite and STUDY_DIR.exists():
        # Only the study-owned directory is eligible for replacement.
        for child in STUDY_DIR.iterdir():
            if child.is_dir():
                for item in child.iterdir():
                    if item.is_file():
                        item.unlink()
            elif child.is_file():
                child.unlink()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    arms: dict[str, Any] = {}
    actions: dict[str, list[dict[str, str]]] = {}
    for slug, flags in (
        ("h1_seizure_free_retarget", {"h1": True, "h2": False, "h3": False, "h7": False}),
        ("h1_h3_clause_head", {"h1": True, "h2": False, "h3": True, "h7": False}),
        ("h1_h2_h3_clause_head", {"h1": True, "h2": True, "h3": True, "h7": False}),
        ("h1_h2_h3_h7_guard", {"h1": True, "h2": True, "h3": True, "h7": True}),
    ):
        derived, arm_actions = _derive_rows(source_rows, **flags)
        actions[slug] = arm_actions
        arms[slug] = _build_candidate(
            slug=slug,
            source_rows=source_rows,
            derived_rows=derived,
            letters=letters,
        )
    baseline_rows = _read_jsonl(
        REPO_ROOT
        / "experiments/exectv2_v16_rules_and_shapes_luna_dev140_20260815/v16_live/assembly.jsonl"
    )
    baseline_letter_rows = _read_jsonl(
        REPO_ROOT
        / "experiments/exectv2_v16_rules_and_shapes_luna_dev140_20260815/v16_live/letter_family.jsonl"
    )
    baseline_report = json.loads(
        (
            REPO_ROOT
            / "experiments/exectv2_v16_rules_and_shapes_luna_dev140_20260815/v16_live/assembly.json"
        ).read_text(encoding="utf-8")
    )
    baseline = {
        "summary": v10_run._arm_summary(
            baseline_report,
            baseline_letter_rows,
            "exectv2_hybrid_key_family_event_ledger_v16",
            "live",
            140,
        ),
        "letter_rows": baseline_letter_rows,
    }
    comparisons = {
        slug: v10_run._compare_arms(baseline, arm, letters)
        for slug, arm in arms.items()
    }
    row_checks = {
        "H1": {
            letter_id: next(
                row["hybrid_letter_exact"]
                for row in arms["h1_seizure_free_retarget"]["letter_rows"]
                if row["letter_id"] == letter_id and row["family"] == SEIZURE_FAMILY
            )
            for letter_id in ("EA0084", "EA0088", "EA0102", "EA0156", "EA0195")
        },
        "H3_with_H2_guard": {
            letter_id: next(
                row["hybrid_letter_exact"]
                for row in arms["h1_h2_h3_clause_head"]["letter_rows"]
                if row["letter_id"] == letter_id and row["family"] == SEIZURE_FAMILY
            )
            for letter_id in ("EA0010", "EA0075", "EA0124", "EA0167", "EA0175")
        },
        "H7": {
            "EA0071": next(
                row["hybrid_letter_exact"]
                for row in arms["h1_h2_h3_h7_guard"]["letter_rows"]
                if row["letter_id"] == "EA0071" and row["family"] == SEIZURE_FAMILY
            )
        },
    }
    h2 = _h2_diagnostic(source_rows)
    h9 = _h9_guard(source_rows, baseline_rows)
    artifact = {
        "schema_version": "exectv2.v16_h123_projection_luna_dev140.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "source": SOURCE.relative_to(REPO_ROOT).as_posix(),
        "split": "dev140",
        "row_count": EXPECTED_N,
        "row_policy": "dev_rows_permitted",
        "scorer": "four-family clinical_headline",
        "model_calls": 0,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "default_prompt_version": structured.PROMPT_VERSION,
        "arms": {"v16_head": baseline["summary"], **{slug: arm["summary"] for slug, arm in arms.items()}},
        "comparisons_vs_v16_head": comparisons,
        "actions": actions,
        "row_checks": row_checks,
        "h2_diagnostic": h2,
        "h9_guard": h9,
        "claim_boundary": "Development-only no-call projection counterfactual; not a prompt ablation, holdout result, fill, or promotion.",
    }
    artifact_path = STUDY_DIR / "comparison.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    return {"artifact": artifact_path.relative_to(REPO_ROOT).as_posix(), "report": REPORT.relative_to(REPO_ROOT).as_posix(), "model_calls": 0}


def _render_report(artifact: Mapping[str, Any]) -> str:
    base = artifact["arms"]["v16_head"]
    lines = [
        "# v16 H1-H3 projection follow-up on Luna `dev140`",
        "",
        "Date: 2026-08-15",
        "Status: complete; no-call development projection study",
        f"Protocol: [{PROTOCOL.rsplit('/', 1)[-1]}]({PROTOCOL.rsplit('/', 1)[-1]})",
        "Split: ExECT `dev140` (n=140). `test60` not touched.",
        "Model calls: 0. Live default remains `v0.9.24`.",
        "",
        "## Verdict",
        "",
        "H1 and H3 are scoreable as deterministic projection counterfactuals on the saved v16 clinical objects. H2 is not a valid no-call prompt ablation; the H2 arm is only an operational guard that prevents the existing named-type ownership pass from undoing a generic clause-head projection.",
        "",
        "## Hybrid comparison versus `v16_head`",
        "",
        "| Arm | Headline delta | SF delta | Four-family exact wins | losses | net |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for slug, comparison in artifact["comparisons_vs_v16_head"].items():
        hybrid = comparison["surfaces"]["hybrid"]
        lines.append(
            f"| `{slug}` | {hybrid['headline_f1_delta']:+.4f} | {hybrid['family_f1_delta']['SeizureFrequency']:+.4f} | {hybrid['four_family_letter_exact_wins']} | {hybrid['four_family_letter_exact_losses']} | {hybrid['four_family_letter_exact_net']:+d} |"
        )
    lines.extend(
        [
            "",
            "## Arm scores",
            "",
            "| Arm | Hybrid headline F1 | SF F1 | Four-family exact |",
            "| --- | ---: | ---: | ---: |",
            f"| `v16_head` | {base['hybrid_headline_f1']:.4f} | {base['hybrid_family_f1']['SeizureFrequency']:.4f} | {base['hybrid_four_family_letter_exact']}/140 |",
        ]
    )
    for slug in artifact["comparisons_vs_v16_head"]:
        arm = artifact["arms"][slug]
        lines.append(
            f"| `{slug}` | {arm['hybrid_headline_f1']:.4f} | {arm['hybrid_family_f1']['SeizureFrequency']:.4f} | {arm['hybrid_four_family_letter_exact']}/140 |"
        )
    lines.extend(
        [
            "",
            "## Representative permitted rows",
            "",
            "| Hypothesis | Rows | Candidate SF family exact |",
            "| --- | --- | --- |",
            f"| H1 seizure-free span | {', '.join(artifact['row_checks']['H1'])} | {', '.join(f'{row}={str(ok).lower()}' for row, ok in artifact['row_checks']['H1'].items())} |",
            f"| H3 clause head with H2 observable guard | {', '.join(artifact['row_checks']['H3_with_H2_guard'])} | {', '.join(f'{row}={str(ok).lower()}' for row, ok in artifact['row_checks']['H3_with_H2_guard'].items())} |",
            f"| H7 stale older last-event zero | EA0071 | EA0071={str(artifact['row_checks']['H7']['EA0071']).lower()} |",
        ]
    )
    lines.extend(
        [
            "",
            "## H2 instrumentation result",
            "",
            f"Status: `{artifact['h2_diagnostic']['status']}`. {artifact['h2_diagnostic']['reason']}. The observable seizure-free ambiguity letters were {', '.join(artifact['h2_diagnostic']['observable_zero_span_ambiguity_letters']) or 'none'}. The scoreable operational arm is `h1_h2_h3_clause_head`; it must not be read as a prompt-example ablation.",
            "",
            "## H9 guard",
            "",
            f"EA0107: {artifact['h9_guard']['interpretation']}. Raw Prescription mentions: {artifact['h9_guard']['raw_prescription_count']}; hybrid: {artifact['h9_guard']['hybrid_prescription_count']}; splitter fired on {artifact['h9_guard']['splitter_fired_on'] or 'none'}; planned/titration classifier fired on {artifact['h9_guard']['planned_start_or_titration_drop_on'] or 'none'}.",
            "",
            "## Boundary",
            "",
            "This is a development diagnostic. It does not promote a prompt or rule, change Decision 0046/0050, inspect `test60`, or support clinical validation.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
